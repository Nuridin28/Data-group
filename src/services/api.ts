import axios from 'axios';
import type { AnalyticsResponse, ChatMessage } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});


// Загрузка CSV файла
export const uploadCSV = async (file: File): Promise<{ message: string; file_id: string }> => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await api.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || error.message || 'Ошибка при загрузке файла');
  }
};

// Получение аналитики - объединяем данные из разных эндпоинтов
export const getAnalytics = async (_fileId?: string): Promise<AnalyticsResponse> => {
  try {
    console.log('getAnalytics called');
    // Запрашиваем данные из разных эндпоинтов бэкенда
    const emptyBody = {};
    const [revenueRes, channelsRes, retentionRes, suspiciousRes, roiRes] = await Promise.all([
      api.post('/analytics/revenue', emptyBody).catch((e) => {
        console.error('Analytics revenue error:', e.response?.data || e.message);
        return { data: null };
      }),
      api.post('/analytics/channels', emptyBody).catch((e) => {
        console.error('Analytics channels error:', e.response?.data || e.message);
        return { data: null };
      }),
      api.post('/analytics/retention', emptyBody).catch((e) => {
        console.error('Analytics retention error:', e.response?.data || e.message);
        return { data: null };
      }),
      api.post('/predict/suspicious', emptyBody).catch((e) => {
        console.error('Predict suspicious error:', e.response?.data || e.message);
        return { data: null };
      }),
      api.post('/analytics/roi', emptyBody).catch((e) => {
        console.error('Analytics ROI error:', e.response?.data || e.message);
        return { data: null };
      })
    ]);
    
    console.log('Analytics responses received:', {
      revenue: revenueRes?.data ? 'OK' : 'null',
      channels: channelsRes?.data ? 'OK' : 'null',
      retention: retentionRes?.data ? 'OK' : 'null',
      suspicious: suspiciousRes?.data ? 'OK' : 'null'
    });

    const revenueData = revenueRes.data;
    const channelsData = channelsRes.data;
    const retentionData = retentionRes.data;
    const suspiciousData = suspiciousRes.data;
    const roiData = roiRes.data;

    // Преобразуем revenue_by_date в revenue_trend
    const revenue_trend = revenueData?.revenue_by_date?.map((item: any) => ({
      date: item.date || item.Date || Object.keys(item)[0],
      revenue: item.revenue || item.amount || item.value || 0,
      transactions_count: item.count || item.transactions || 0
    })) || [];

    // Преобразуем channel_performance в revenue_by_channel
    const revenue_by_channel = channelsData?.channel_performance?.map((item: any) => ({
      channel: item.channel || item.name || 'Unknown',
      revenue: item.revenue || item.total_revenue || item.amount || 0,
      transactions: item.transactions || item.count || 0,
      customers: item.customers || item.unique_customers || 0,
      roi: item.roi || (item.revenue && item.investment ? ((item.revenue - item.investment) / item.investment * 100) : 0),
      conversion_rate: item.conversion_rate || item.conversion || 0
    })) || [];

    // Преобразуем retention данные - используем правильную структуру
    const cohort_analysis = retentionData?.customer_segment_retention?.map((item: any, index: number) => ({
      cohort: item.cohort || item.segment || item.customer_segment || `Cohort ${index}`,
      period: typeof item.period === 'number' ? item.period : (item.period || 0),
      retention: item.retention_rate || item.retention || 0,
      customers: item.customers || item.count || item.unique_customers || 0
    })) || [];

    // ROI метрики - получаем из нового эндпоинта с LLM анализом по источникам привлечения
    let roi_metrics = [];
    if (roiData?.roi_metrics && Array.isArray(roiData.roi_metrics)) {
      roi_metrics = roiData.roi_metrics.map((metric: any) => ({
        source: metric.source,
        investment: metric.investment || 0,
        revenue: metric.revenue || 0,
        roi: metric.roi || 0,
        profit: metric.profit || 0,
        transactions: metric.transactions,
        customers: metric.customers,
        avg_transaction: metric.avg_transaction,
        cpa: metric.cpa,
        conversion_rate: metric.conversion_rate
      }));
    } else {
      // Fallback если эндпоинт не доступен - используем каналы
      roi_metrics = revenue_by_channel.map((channel: any) => ({
        source: channel.channel,
        investment: channel.revenue * 0.15, // 15% для маркетинга
        revenue: channel.revenue,
        roi: channel.roi || 0,
        profit: channel.revenue - (channel.revenue * 0.15),
        transactions: channel.transactions,
        customers: channel.customers
      }));
    }

    // Summary из revenue данных
    const summary = {
      total_revenue: revenueData?.total_revenue || 0,
      total_transactions: revenueData?.transaction_count || 0,
      active_customers: retentionData?.retention_rate ? Math.round(revenueData?.transaction_count * retentionData.retention_rate / 100) : 0,
      avg_transaction_value: revenueData?.average_transaction || 0,
      cancellation_rate: 0 // Будет из прогнозов
    };

    // Аномалии из suspicious - используем данные от модели с LLM анализом на русском
    const anomalies = suspiciousData?.suspicious_transactions?.slice(0, 100).map((item: any, index: number) => {
      const anomalyScore = item.anomaly_score || item.risk_score || item.suspicious_score || 0.5;
      const riskScore = item.risk_score || item.anomaly_score || 0.5;
      
      // Определяем risk_level на основе score
      let riskLevel: 'low' | 'medium' | 'high' = 'medium';
      if (anomalyScore > 0.8 || riskScore > 0.8) {
        riskLevel = 'high';
      } else if (anomalyScore > 0.6 || riskScore > 0.6) {
        riskLevel = 'medium';
      } else {
        riskLevel = 'low';
      }
      
      return {
        transaction_id: String(item.transaction_id || item.id || `txn_${index}`),
        date: item.date || item.transaction_date || new Date().toISOString(),
        amount: item.amount_kzt || item.amount || 0,
        anomaly_score: anomalyScore,
        risk_score: riskScore,
        reason: item.reason || item.risk_factors?.join(', ') || 'Обнаружена аномалия моделью ML',
        risk_level: (item.risk_level || riskLevel) as 'low' | 'medium' | 'high',
        city: item.city,
        channel: item.channel,
        payment_method: item.payment_method,
        merchant_category: item.merchant_category,
        is_refunded: item.is_refunded,
        is_canceled: item.is_canceled
      };
    }) || [];

    const result = {
      revenue_trend,
      revenue_by_channel,
      cohort_analysis,
      roi_metrics,
      summary,
      anomalies: anomalies.length > 0 ? anomalies : undefined,
      forecasts: undefined,
      recommendations: undefined
    };
    
    console.log('Analytics result:', {
      revenue_trend_count: result.revenue_trend.length,
      revenue_by_channel_count: result.revenue_by_channel.length,
      summary: result.summary
    });
    
    return result;
  } catch (error: any) {
    console.error('getAnalytics error:', error);
    throw new Error(error.response?.data?.detail || error.message || 'Ошибка при получении аналитики');
  }
};

// Прогнозы
export const getForecasts = async (_fileId?: string, days: number = 30): Promise<AnalyticsResponse['forecasts']> => {
  try {
    const response = await api.post('/predict/transactions', {
      days_ahead: days,
      start_date: null,
      end_date: null
    });
    
    const data = response.data;
    
    // Преобразуем predicted_volume в revenue_forecast
    const revenue_forecast = data?.predicted_volume?.map((item: any) => ({
      date: item.date || item.Date || new Date().toISOString(),
      predicted: item.predicted_revenue || item.revenue || item.amount || 0,
      lower_bound: item.lower_bound || (item.predicted_revenue ? item.predicted_revenue * 0.8 : 0),
      upper_bound: item.upper_bound || (item.predicted_revenue ? item.predicted_revenue * 1.2 : 0)
    })) || [];

    // Получаем вероятность отмены
    const cancellationResponse = await api.post('/predict/cancellation', {
      amount_kzt: 1000,
      channel: 'Kaspi QR',
      payment_method: 'card',
      customer_segment: 'regular'
    }).catch(() => ({ data: { cancellation_probability: 0 } }));

    const cancellation_probability = (cancellationResponse.data?.cancellation_probability || 0) * 100;

    return {
      revenue_forecast,
      cancellation_probability: Math.round(cancellation_probability * 100) / 100
    };
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || error.message || 'Ошибка при получении прогнозов');
  }
};

// Аномалии
export const getAnomalies = async (_fileId?: string): Promise<AnalyticsResponse['anomalies']> => {
  try {
    const response = await api.post('/predict/suspicious', {
      start_date: null,
      end_date: null,
      region: null,
      city: null,
      merchant_category: null,
      channel: null
    });
    
    const suspicious = response.data?.suspicious_transactions || [];
    
    return suspicious.slice(0, 100).map((item: any, index: number) => ({
      transaction_id: item.transaction_id || item.id || `txn_${index}`,
      date: item.date || item.transaction_date || new Date().toISOString(),
      amount: item.amount_kzt || item.amount || 0,
      anomaly_score: item.risk_score || item.suspicious_score || 0.5,
      reason: item.reason || item.risk_factors?.join(', ') || 'Обнаружена аномалия',
      risk_level: (item.risk_level || 'medium') as 'low' | 'medium' | 'high'
    }));
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || error.message || 'Ошибка при получении аномалий');
  }
};

// Рекомендации - используем новый эндпоинт с LLM анализом
export const getRecommendations = async (_fileId?: string): Promise<AnalyticsResponse['recommendations']> => {
  try {
    const response = await api.post('/analytics/recommendations', {});
    
    const data = response.data;
    
    console.log('[Recommendations] Received data:', data);
    
    // Преобразуем ответ из нового эндпоинта
    if (data?.recommendations && Array.isArray(data.recommendations) && data.recommendations.length > 0) {
      const mapped = data.recommendations.map((rec: any) => ({
        id: rec.id || `rec_${Math.random()}`,
        type: (rec.type || 'optimization') as 'discount' | 'marketing' | 'optimization',
        title: rec.title || 'Рекомендация',
        description: rec.description || '',
        expected_impact: rec.expected_impact || 'Улучшение показателей',
        priority: (rec.priority || 'medium') as 'high' | 'medium' | 'low',
        segment: rec.segment,
        estimated_benefit: rec.estimated_benefit || 'Требует оценки',
        implementation_effort: (rec.implementation_effort || 'medium') as 'low' | 'medium' | 'high'
      }));
      console.log(`[Recommendations] Mapped ${mapped.length} recommendations`);
      return mapped;
    }
    
    console.warn('[Recommendations] No recommendations in response, returning empty array');
    return [];
  } catch (error: any) {
    console.error('Error getting recommendations:', error);
    // Не бросаем ошибку, возвращаем пустой массив чтобы не ломать UI
    console.warn('[Recommendations] Returning empty array due to error');
    return [];
  }
};

// AI Чат - используем новый эндпоинт /chat
export const sendChatMessage = async (
  message: string,
  _fileId?: string,
  _conversationHistory?: ChatMessage[]
): Promise<{ response: string }> => {
  try {
    console.log('Sending chat message to /chat:', message);
    
    // Пробуем использовать новый эндпоинт /chat
    let response;
    try {
      response = await api.post('/chat', {
        question: message
      });
    } catch (chatError: any) {
      console.warn('Chat endpoint failed, trying /ask:', chatError.message);
      // Fallback to /ask
      response = await api.post('/ask', {
        question: message
      });
    }
    
    // Обрабатываем разные форматы ответа
    let answer = "";
    if (response.data) {
      // QuestionResponse format from /chat
      if (response.data.answer) {
        answer = response.data.answer;
      }
      // SQLResponse format from /ask
      else if (response.data.explanation) {
        answer = response.data.explanation;
      }
      // Fallback to sql_query
      else if (response.data.sql_query) {
        answer = response.data.sql_query;
      }
    }
    
    if (!answer || answer.includes("AI service unavailable") || answer.includes("Returning basic query")) {
      throw new Error("AI service is not available. Please check API configuration.");
    }
    
    console.log('Chat response received:', answer.substring(0, 100));
    return { response: answer };
  } catch (error: any) {
    console.error('Chat error:', error);
    const errorMessage = error.response?.data?.detail || error.message || 'Ошибка при отправке сообщения';
    throw new Error(errorMessage);
  }
};

export default api;