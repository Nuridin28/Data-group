import axios from 'axios';
import type { AnalyticsResponse, ChatMessage, Recommendation } from '../types';

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
    // Отправляем пустой объект или можем не отправлять body вообще
    const emptyBody = {};
    const [revenueRes, channelsRes, retentionRes, suspiciousRes] = await Promise.all([
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

    // ROI метрики из каналов
    const roi_metrics = revenue_by_channel.map((channel: any) => ({
      source: channel.channel,
      investment: channel.revenue * 0.2, // Упрощенная модель
      revenue: channel.revenue,
      roi: channel.roi,
      profit: channel.revenue - (channel.revenue * 0.2)
    }));

    // Summary из revenue данных
    const summary = {
      total_revenue: revenueData?.total_revenue || 0,
      total_transactions: revenueData?.transaction_count || 0,
      active_customers: retentionData?.retention_rate ? Math.round(revenueData?.transaction_count * retentionData.retention_rate / 100) : 0,
      avg_transaction_value: revenueData?.average_transaction || 0,
      cancellation_rate: 0 // Будет из прогнозов
    };

    // Аномалии из suspicious - используем данные от модели с объяснениями
    const anomalies = suspiciousData?.suspicious_transactions?.slice(0, 100).map((item: any, index: number) => ({
      transaction_id: String(item.transaction_id || item.id || `txn_${index}`),
      date: item.date || item.transaction_date || new Date().toISOString(),
      amount: item.amount_kzt || item.amount || 0,
      anomaly_score: item.anomaly_score || item.risk_score || item.suspicious_score || 0.5,
      risk_score: item.risk_score || item.anomaly_score || 0.5,
      reason: item.reason || item.risk_factors?.join(', ') || 'Обнаружена аномалия моделью ML',
      risk_level: (item.risk_level || (item.anomaly_score > 0.8 ? 'high' : item.anomaly_score > 0.6 ? 'medium' : 'low')) as 'low' | 'medium' | 'high',
      city: item.city,
      channel: item.channel,
      payment_method: item.payment_method,
      merchant_category: item.merchant_category,
      is_refunded: item.is_refunded,
      is_canceled: item.is_canceled
    })) || [];

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

// Рекомендации - используем AI insights из аналитики
export const getRecommendations = async (_fileId?: string): Promise<AnalyticsResponse['recommendations']> => {
  try {
    // Получаем данные из разных эндпоинтов для контекста
    const emptyBody = {};
    const [, channelsRes] = await Promise.all([
      api.post('/analytics/revenue', emptyBody).catch(() => ({ data: null })),
      api.post('/analytics/channels', emptyBody).catch(() => ({ data: null }))
    ]);

    const channelsData = channelsRes.data;

    const recommendations: Recommendation[] = [];

    // Рекомендации из AI insights
    if (channelsData?.ai_recommendations) {
      const aiText = channelsData.ai_recommendations;
      // Парсим рекомендации из текста
      const lines = aiText.split('\n').filter((line: string) => line.trim().length > 0);
      
      lines.forEach((line: string, index: number) => {
        if (line.includes('рекоменд') || line.includes('совет') || line.includes('увелич') || line.includes('оптимиз')) {
          const type: 'discount' | 'marketing' | 'optimization' = line.toLowerCase().includes('канал') ? 'marketing' : 'optimization';
          const priority: 'high' | 'medium' | 'low' = index < 2 ? 'high' : 'medium';
          
          recommendations.push({
            id: `rec_${index + 1}`,
            type,
            title: line.substring(0, 100),
            description: line,
            expected_impact: "Улучшение показателей",
            priority
          });
        }
      });
    }

    // Если нет рекомендаций из AI, создаем базовые
    if (recommendations.length === 0 && channelsData?.best_channel) {
      recommendations.push({
        id: 'rec_1',
        type: 'marketing' as const,
        title: `Увеличить инвестиции в ${channelsData.best_channel}`,
        description: `Канал ${channelsData.best_channel} показывает лучшие результаты`,
        expected_impact: "Увеличение выручки на 15-25%",
        priority: 'high' as const
      });
    }

    return recommendations.slice(0, 10);
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || error.message || 'Ошибка при получении рекомендаций');
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