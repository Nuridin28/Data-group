from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class QuestionRequest(BaseModel):
    question: str = Field(..., description="The question to ask about the financial data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Какие каналы привлечения наиболее эффективны?"
            }
        }

class QuestionResponse(BaseModel):
    answer: str = Field(..., description="The AI-generated answer")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Retrieved data sources")
    confidence: Optional[float] = Field(None, description="Confidence score if available")

class SQLRequest(BaseModel):
    question: str = Field(default="", description="Natural language question to convert to SQL query")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the total revenue by city?"
            }
        }

class SQLResponse(BaseModel):
    sql_query: str = Field(..., description="Generated SQL query")
    explanation: str = Field(..., description="Explanation of the SQL query")
    table_name: str = Field(default="transactions", description="Target table name")

class AnalyticsRequest(BaseModel):
    start_date: Optional[str] = Field(
        default=None, 
        description="Start date in YYYY-MM-DD format (e.g., 2024-01-01)",
        examples=["2024-01-01"]
    )
    end_date: Optional[str] = Field(
        default=None, 
        description="End date in YYYY-MM-DD format (e.g., 2024-12-31)",
        examples=["2024-12-31"]
    )
    region: Optional[str] = Field(default=None, description="Filter by region")
    city: Optional[str] = Field(default=None, description="Filter by city")
    merchant_category: Optional[str] = Field(default=None, description="Filter by merchant category")
    channel: Optional[str] = Field(default=None, description="Filter by channel")
    
    class Config:
        # Allow empty body for POST requests
        json_schema_extra = {
            "example": {}
        }

class RevenueResponse(BaseModel):
    total_revenue: float = Field(..., description="Total revenue in KZT")
    transaction_count: int = Field(..., description="Total number of transactions")
    average_transaction: float = Field(..., description="Average transaction amount")
    revenue_by_date: List[Dict[str, Any]] = Field(default_factory=list)
    revenue_by_city: List[Dict[str, Any]] = Field(default_factory=list)
    revenue_by_channel: List[Dict[str, Any]] = Field(default_factory=list)
    ai_insights: str = Field(..., description="AI-generated insights based on the data")

class ChannelResponse(BaseModel):
    channel_performance: List[Dict[str, Any]] = Field(..., description="Performance metrics by channel")
    best_channel: str = Field(..., description="Best performing channel")
    worst_channel: str = Field(..., description="Worst performing channel")
    ai_recommendations: str = Field(..., description="AI recommendations for channel optimization")

class RetentionResponse(BaseModel):
    customer_segment_retention: List[Dict[str, Any]] = Field(..., description="Retention by customer segment")
    acquisition_source_performance: List[Dict[str, Any]] = Field(..., description="Performance by acquisition source")
    retention_rate: float = Field(..., description="Overall retention rate")
    ai_insights: str = Field(..., description="AI-generated retention insights")

class PredictionRequest(BaseModel):
    days_ahead: Optional[int] = Field(default=30, description="Number of days to predict ahead", ge=1, le=365)
    start_date: Optional[str] = Field(
        default=None, 
        description="Start date for prediction context in YYYY-MM-DD format",
        examples=["2024-01-01"]
    )
    end_date: Optional[str] = Field(
        default=None, 
        description="End date for prediction context in YYYY-MM-DD format",
        examples=["2024-12-31"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "days_ahead": 30
            }
        }

class TransactionPredictionResponse(BaseModel):
    predicted_volume: List[Dict[str, Any]] = Field(..., description="Predicted transaction volumes by date")
    predicted_total_revenue: float = Field(..., description="Predicted total revenue")
    confidence_interval: Dict[str, float] = Field(..., description="Confidence interval for predictions")
    ai_analysis: str = Field(..., description="AI analysis of the predictions")

class CancellationPredictionRequest(BaseModel):
    amount_kzt: float = Field(..., description="Transaction amount", gt=0)
    channel: str = Field(..., description="Transaction channel")
    payment_method: str = Field(..., description="Payment method")
    customer_segment: str = Field(..., description="Customer segment")
    city: Optional[str] = Field(default=None, description="City")
    merchant_category: Optional[str] = Field(default=None, description="Merchant category")

class CancellationPredictionResponse(BaseModel):
    cancellation_probability: float = Field(..., description="Probability of cancellation (0-1)")
    risk_level: str = Field(..., description="Risk level: low, medium, high")
    factors: List[Dict[str, Any]] = Field(..., description="Key factors influencing the prediction")
    ai_recommendations: str = Field(..., description="AI recommendations to reduce cancellation risk")

class SuspiciousTransactionResponse(BaseModel):
    suspicious_transactions: List[Dict[str, Any]] = Field(..., description="List of suspicious transactions with anomaly scores and reasons")
    total_suspicious: int = Field(..., description="Total number of suspicious transactions")
    risk_factors: List[Dict[str, Any]] = Field(..., description="Common risk factors")
    ai_analysis: str = Field(..., description="AI analysis of suspicious patterns")
    model_insights: Optional[str] = Field(None, description="ML model insights and methodology")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

class TransactionListItem(BaseModel):
    transaction_id: str = Field(..., description="Transaction ID")
    date: str = Field(..., description="Transaction date")
    amount_kzt: float = Field(..., description="Transaction amount in KZT")
    merchant_category: str = Field(..., description="Merchant category")
    channel: str = Field(..., description="Transaction channel")
    payment_method: str = Field(..., description="Payment method")
    city: str = Field(..., description="City")
    region: str = Field(..., description="Region")
    is_refunded: bool = Field(..., description="Whether transaction was refunded")
    is_canceled: bool = Field(..., description="Whether transaction was canceled")

