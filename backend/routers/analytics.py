from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.schemas import (
    AnalyticsRequest, RevenueResponse, ChannelResponse, RetentionResponse, TransactionListItem
)
from services.data_service import get_data_service
from rag.rag_chain import get_rag_chain

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.post("/revenue", response_model=RevenueResponse)
async def get_revenue_analytics(request: AnalyticsRequest = AnalyticsRequest()) -> RevenueResponse:
    try:
        data_service = get_data_service()
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
        if request.merchant_category:
            filters['merchant_category'] = request.merchant_category
        if request.channel:
            filters['channel'] = request.channel
        
        revenue_data = data_service.get_revenue_analytics(filters)
        
        question = f"""Analyze the revenue data:
- Total revenue: {revenue_data['total_revenue']:,.2f} KZT
- Transaction count: {revenue_data['transaction_count']}
- Average transaction: {revenue_data['average_transaction']:,.2f} KZT
- Top cities: {revenue_data['revenue_by_city'][:5] if revenue_data['revenue_by_city'] else 'N/A'}
- Top channels: {revenue_data['revenue_by_channel'][:5] if revenue_data['revenue_by_channel'] else 'N/A'}

Provide insights on revenue trends, city performance, and channel effectiveness. Identify opportunities for growth."""
        
        ai_result = rag_chain.query_with_analytics(question, revenue_data)
        
        return RevenueResponse(
            total_revenue=revenue_data["total_revenue"],
            transaction_count=revenue_data["transaction_count"],
            average_transaction=revenue_data["average_transaction"],
            revenue_by_date=revenue_data["revenue_by_date"],
            revenue_by_city=revenue_data["revenue_by_city"],
            revenue_by_channel=revenue_data["revenue_by_channel"],
            ai_insights=ai_result["answer"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating revenue analytics: {str(e)}")

@router.post("/channels", response_model=ChannelResponse)
async def get_channel_analytics(request: AnalyticsRequest = AnalyticsRequest()) -> ChannelResponse:
    try:
        data_service = get_data_service()
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
        
        channel_data = data_service.get_channel_analytics(filters)
        
        question = f"""Analyze channel performance:
{channel_data['channel_performance']}

Best channel: {channel_data['best_channel']}
Worst channel: {channel_data['worst_channel']}

Provide recommendations for channel optimization and marketing budget allocation."""
        
        ai_result = rag_chain.query_with_analytics(question, channel_data)
        
        return ChannelResponse(
            channel_performance=channel_data["channel_performance"],
            best_channel=channel_data["best_channel"],
            worst_channel=channel_data["worst_channel"],
            ai_recommendations=ai_result["answer"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating channel analytics: {str(e)}")

@router.post("/retention", response_model=RetentionResponse)
async def get_retention_analytics(request: AnalyticsRequest = AnalyticsRequest()) -> RetentionResponse:
    try:
        data_service = get_data_service()
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
        
        retention_data = data_service.get_retention_analytics(filters)
        
        question = f"""Analyze customer retention:
- Overall retention rate: {retention_data['retention_rate']:.2f}%
- Customer segment performance: {retention_data['customer_segment_retention'][:5] if retention_data['customer_segment_retention'] else 'N/A'}
- Acquisition source performance: {retention_data['acquisition_source_performance'][:5] if retention_data['acquisition_source_performance'] else 'N/A'}

Provide insights on retention trends and recommend strategies to improve customer loyalty."""
        
        ai_result = rag_chain.query_with_analytics(question, retention_data)
        
        return RetentionResponse(
            customer_segment_retention=retention_data["customer_segment_retention"],
            acquisition_source_performance=retention_data["acquisition_source_performance"],
            retention_rate=retention_data["retention_rate"],
            ai_insights=ai_result["answer"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating retention analytics: {str(e)}")

@router.post("/transactions", response_model=List[TransactionListItem])
async def get_transactions(request: AnalyticsRequest = AnalyticsRequest(), limit: int = Query(100, ge=1, le=1000)) -> List[TransactionListItem]:
    """Get list of transactions with optional filters"""
    try:
        data_service = get_data_service()
        
        filters = {}
        if request.start_date:
            filters['start_date'] = request.start_date
        if request.end_date:
            filters['end_date'] = request.end_date
        if request.region:
            filters['region'] = request.region
        if request.city:
            filters['city'] = request.city
        if request.merchant_category:
            filters['merchant_category'] = request.merchant_category
        if request.channel:
            filters['channel'] = request.channel
        
        df = data_service.get_dataframe(filters)
        
        # Limit results and convert to dict
        transactions = df.head(limit).to_dict('records')
        
        # Format the response
        formatted_transactions = []
        for txn in transactions:
            formatted_txn = TransactionListItem(
                transaction_id=str(txn.get('transaction_id', '')),
                date=str(txn.get('date', '')),
                amount_kzt=float(txn.get('amount_kzt', 0)),
                merchant_category=str(txn.get('merchant_category', '')),
                channel=str(txn.get('channel', '')),
                payment_method=str(txn.get('payment_method', '')),
                city=str(txn.get('city', '')),
                region=str(txn.get('region', '')),
                is_refunded=bool(txn.get('is_refunded', 0)),
                is_canceled=bool(txn.get('is_canceled', 0)),
            )
            formatted_transactions.append(formatted_txn)
        
        return formatted_transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching transactions: {str(e)}")

