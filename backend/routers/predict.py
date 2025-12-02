from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.schemas import (
    PredictionRequest, TransactionPredictionResponse,
    CancellationPredictionRequest, CancellationPredictionResponse,
    SuspiciousTransactionResponse, AnalyticsRequest,
    RecommendationsResponse, RecommendationItem, ROIMetricsResponse
)
from services.prediction_service import get_prediction_service
from services.data_service import get_data_service
from rag.rag_chain import get_rag_chain

router = APIRouter(prefix="/predict", tags=["Predictions"])

@router.post("/transactions", response_model=TransactionPredictionResponse)
async def predict_transactions(request: PredictionRequest = PredictionRequest(days_ahead=30)) -> TransactionPredictionResponse:
    try:
        prediction_service = get_prediction_service()
        rag_chain = get_rag_chain()
        
        filters = {}
        if request.start_date:
            filters['start_date'] = request.start_date
        if request.end_date:
            filters['end_date'] = request.end_date
        
        predictions = prediction_service.predict_transaction_volume(
            days_ahead=request.days_ahead,
            filters=filters if filters else None
        )
        
        question = f"""Проанализируй прогнозы объема транзакций на русском языке:
- Период прогноза: {request.days_ahead} дней
- Прогнозируемая общая выручка: {predictions['predicted_total_revenue']:,.2f} KZT
- Прогнозируемые объемы: {predictions['predicted_volume'][:10] if len(predictions['predicted_volume']) > 10 else predictions['predicted_volume']}

Предоставь анализ прогноза, определи тренды и предложи действия на основе прогнозов. ОТВЕТЬ НА РУССКОМ ЯЗЫКЕ."""
        
        ai_result = rag_chain.query_with_analytics(question, predictions)
        
        return TransactionPredictionResponse(
            predicted_volume=predictions["predicted_volume"],
            predicted_total_revenue=predictions["predicted_total_revenue"],
            confidence_interval=predictions["confidence_interval"],
            ai_analysis=ai_result["answer"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating transaction predictions: {str(e)}")

@router.post("/cancellation", response_model=CancellationPredictionResponse)
async def predict_cancellation(request: CancellationPredictionRequest) -> CancellationPredictionResponse:
    try:
        prediction_service = get_prediction_service()
        rag_chain = get_rag_chain()
        
        prediction = prediction_service.predict_cancellation_probability(
            amount_kzt=request.amount_kzt,
            channel=request.channel,
            payment_method=request.payment_method,
            customer_segment=request.customer_segment,
            city=request.city,
            merchant_category=request.merchant_category
        )
        
        question = f"""Проанализируй прогноз отмены транзакции на русском языке:
- Вероятность отмены: {prediction['cancellation_probability']:.2%}
- Уровень риска: {prediction['risk_level']}
- Ключевые факторы: {prediction['factors']}
- Детали транзакции: Сумма={request.amount_kzt} KZT, Канал={request.channel}, Оплата={request.payment_method}, Сегмент={request.customer_segment}

Предоставь рекомендации по снижению риска отмены. ОТВЕТЬ НА РУССКОМ ЯЗЫКЕ."""
        
        ai_result = rag_chain.query_with_analytics(question, prediction)
        
        return CancellationPredictionResponse(
            cancellation_probability=prediction["cancellation_probability"],
            risk_level=prediction["risk_level"],
            factors=prediction["factors"],
            ai_recommendations=ai_result["answer"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating cancellation prediction: {str(e)}")

@router.post("/suspicious", response_model=SuspiciousTransactionResponse)
async def detect_suspicious_transactions(request: AnalyticsRequest = AnalyticsRequest()) -> SuspiciousTransactionResponse:
    try:
        prediction_service = get_prediction_service()
        rag_chain = get_rag_chain()
        
        filters = {}
        if request.start_date:
            filters['start_date'] = request.start_date
        if request.end_date:
            filters['end_date'] = request.end_date
        if request.region:
            filters['region'] = request.region
        if request.city:
            filters['city'] = request.city
        
        suspicious_data = prediction_service.detect_suspicious_transactions(
            filters=filters if filters else None,
            limit=100
        )
        
        sample_txns = suspicious_data['suspicious_transactions'][:10] if suspicious_data['suspicious_transactions'] else []
        txn_details = "\n".join([
            f"- Txn {t.get('transaction_id', 'N/A')}: {t.get('amount_kzt', 0):,.0f} KZT, "
            f"Score: {t.get('anomaly_score', 0):.2f}, Reason: {t.get('reason', 'N/A')}, "
            f"Risk: {t.get('risk_level', 'unknown')}"
            for t in sample_txns
        ])
        
        question = f"""Ты профессиональный аналитик по мошенничеству и аномалиям в транзакционных данных для цифровой экономики Казахстана.

ПРОАНАЛИЗИРУЙ следующие подозрительные транзакции:

СВОДКА:
- Всего обнаружено подозрительных транзакций: {suspicious_data['total_suspicious']}
- Выявлено факторов риска: {len(suspicious_data.get('risk_factors', []))}
- Методология модели: {suspicious_data.get('model_insights', 'ML-based anomaly detection')}

ПРИМЕРЫ ПОДОЗРИТЕЛЬНЫХ ТРАНЗАКЦИЙ:
{txn_details if txn_details else 'Не обнаружено'}

ФАКТОРЫ РИСКА:
{chr(10).join([f"- {rf.get('factor', 'unknown')}: {rf.get('description', '')} ({rf.get('count', 0)} случаев)" for rf in suspicious_data.get('risk_factors', [])])}

ОБЯЗАТЕЛЬНО ОТВЕТЬ НА РУССКОМ ЯЗЫКЕ и предоставь профессиональный анализ:
1. Определи наиболее критические паттерны мошенничества и их влияние на бизнес
2. Объясни ПОЧЕМУ каждый паттерн подозрителен с конкретными метриками
3. Рекомендуй немедленные действия и стратегии предотвращения мошенничества
4. Оцени потенциальный финансовый риск
5. Предложи правила мониторинга и алертинга
Используй профессиональный аналитический язык с конкретными числами и практическими рекомендациями."""
        
        ai_result = rag_chain.query_with_analytics(question, suspicious_data)
        
        return SuspiciousTransactionResponse(
            suspicious_transactions=suspicious_data["suspicious_transactions"],
            total_suspicious=suspicious_data["total_suspicious"],
            risk_factors=suspicious_data["risk_factors"],
            ai_analysis=ai_result["answer"],
            model_insights=suspicious_data.get("model_insights", "ML-based anomaly detection using Isolation Forest")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting suspicious transactions: {str(e)}")

