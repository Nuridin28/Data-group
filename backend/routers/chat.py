from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.schemas import QuestionRequest, QuestionResponse
from services.data_service import get_data_service
from config.config import settings

router = APIRouter(prefix="/chat", tags=["AI Chat"])

def call_deepseek_api(question: str, context: str = "") -> str:
    try:
        import os
        import sys
        
        try:
            import langchain
            attrs_to_set = ['verbose', 'debug', 'llm_cache', 'tracing_v2', 'tracing_callback']
            for attr in attrs_to_set:
                if not hasattr(langchain, attr):
                    setattr(langchain, attr, None if attr == 'llm_cache' else False)
        except (ImportError, AttributeError) as patch_error:
            print(f"Warning: Could not patch langchain: {patch_error}")
        
        os.environ["LANGCHAIN_VERBOSE"] = "false"
        os.environ["LANGCHAIN_DEBUG"] = "false"
        
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage
        
        try:
            from langchain_core import globals as langchain_globals
            for attr in ['_verbose', '_debug', '_llm_cache']:
                if hasattr(langchain_globals, attr):
                    setattr(langchain_globals, attr, None if 'cache' in attr else False)
        except:
            pass
        
        llm_kwargs = {
            "model": settings.LLM_MODEL or "deepseek-chat",
            "temperature": float(settings.TEMPERATURE) if settings.TEMPERATURE else 0.7,
        }
        
        api_key = settings.API_KEY
        if api_key:
            llm_kwargs["openai_api_key"] = api_key
        else:
            raise ValueError("API_KEY is not set in environment")
        
        if settings.API_BASE_URL:
            base_url = settings.API_BASE_URL.rstrip('/')
            if not base_url.endswith('/v1'):
                base_url = base_url + '/v1'
            llm_kwargs["base_url"] = base_url
        
        try:
            try:
                from langchain_core import globals as langchain_globals
                if hasattr(langchain_globals, '_verbose'):
                    langchain_globals._verbose = False
                if hasattr(langchain_globals, '_debug'):
                    langchain_globals._debug = False
            except:
                pass
            
            llm = ChatOpenAI(**llm_kwargs)
        except (AttributeError, TypeError) as e:
                error_str = str(e)
                if "verbose" in error_str or "debug" in error_str or "has no attribute" in error_str:
                    try:
                        import langchain
                        langchain.verbose = False
                        langchain.debug = False
                    except:
                        pass
                    
                    llm = ChatOpenAI(**llm_kwargs)
                else:
                    raise
        
        system_prompt = """Ты эксперт по финансовой аналитике и AI-ассистент, специализирующийся на аналитике цифровой экономики Казахстана.

Твоя экспертиза включает:
- Анализ транзакционных данных и обнаружение мошенничества
- Прогнозирование выручки и анализ трендов
- Ретеншн клиентов и сегментация
- Оптимизация эффективности каналов
- Оценка рисков и обнаружение аномалий

КРИТИЧЕСКИ ВАЖНЫЕ ИНСТРУКЦИИ:
1. Всегда отвечай на основе предоставленного контекста данных - будь data-driven
2. НИКОГДА не выдумывай числа, даты или статистику, которых нет в предоставленных данных
3. Если данных недостаточно, четко укажи что можно и нельзя определить
4. Показывай свое аналитическое мышление и расчеты
5. Для обнаружения мошенничества/аномалий объясняй ПОЧЕМУ транзакции подозрительны
6. Предоставляй практические бизнес-инсайты и рекомендации
7. Используй профессиональный аналитический язык с конкретными метриками
8. Сравнивай сегменты, каналы и временные периоды когда это уместно
9. Определяй паттерны, тренды и аномалии с четкими объяснениями
10. Всегда указывай временной период, фильтры и область данных которые анализируешь

ВАЖНО: Всегда отвечай на РУССКОМ ЯЗЫКЕ, если не указано иное.

Формат ответа для профессионального анализа:
- Прямой ответ с ключевыми находками
- Конкретные числа, проценты и метрики из данных
- Четкое объяснение паттернов и аномалий
- Практические рекомендации
- Оценка рисков с обоснованием
- Контекст: даты, регионы, категории, сегменты

ВАЖНО: Форматируй ответ используя Markdown для лучшей читаемости:
- Используй
- Используй **жирный** для акцента и ключевых метрик
- Используй маркированные списки (-) для списков
- Используй --- для горизонтальных разделителей
- Используй таблицы при представлении данных
- Делай параграфы краткими и хорошо структурированными"""
        
        if context:
            user_message = f"""Контекст из датасета:
{context}

Вопрос: {question}

Предоставь комплексный профессиональный анализ на основе предоставленного контекста. ОТВЕТЬ НА РУССКОМ ЯЗЫКЕ."""
        else:
            user_message = f"""Вопрос: {question}

Предоставь комплексный профессиональный анализ. Если нужен контекст данных, попроси уточнения. ОТВЕТЬ НА РУССКОМ ЯЗЫКЕ."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        try:
            import langchain
            for attr in ['verbose', 'debug', 'llm_cache', 'tracing_v2', 'tracing_callback']:
                if not hasattr(langchain, attr):
                    setattr(langchain, attr, None if attr == 'llm_cache' else False)
        except:
            pass
        
        try:
            response = llm.invoke(messages)
        except (AttributeError, TypeError) as e:
            error_str = str(e)
            if "has no attribute" in error_str:
                try:
                    import langchain
                    import re
                    match = re.search(r"has no attribute '(\w+)'", error_str)
                    if match:
                        attr_name = match.group(1)
                        setattr(langchain, attr_name, None if 'cache' in attr_name else False)
                        response = llm.invoke(messages)
                    else:
                        raise
                except:
                    raise
            else:
                raise
        
        answer = response.content if hasattr(response, 'content') else str(response)
        
        return answer
        
    except ImportError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"LLM library not available: {str(e)}. Please install langchain-openai."
        )
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "401" in error_msg or "invalid" in error_msg.lower():
            raise HTTPException(
                status_code=401,
                detail=f"Invalid API key or authentication error. Please check API_KEY in .env file. Error: {error_msg[:200]}"
            )
        raise HTTPException(
            status_code=500,
            detail=f"Error calling DeepSeek API: {error_msg[:300]}"
        )

@router.post("", response_model=QuestionResponse)
async def chat_message(request: QuestionRequest) -> QuestionResponse:
    try:
        question = request.question if hasattr(request, 'question') and request.question else ""
        
        if not question or not question.strip():
            raise HTTPException(status_code=400, detail="Question is required")
        
        context = ""
        sources = []
        
        try:
            data_service = get_data_service()
            df = data_service.get_dataframe()
            
            if df is not None and len(df) > 0:
                import pandas as pd
                
                context_parts = []
                
                context_parts.append("=== DATASET OVERVIEW ===")
                context_parts.append(f"Total transactions: {len(df)}")
                
                if 'date' in df.columns and not df['date'].isna().all():
                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                    date_range = df['date'].dropna()
                    if len(date_range) > 0:
                        context_parts.append(f"Date range: {date_range.min()} to {date_range.max()}")
                        context_parts.append(f"Unique dates: {date_range.dt.date.nunique()}")
                        context_parts.append(f"Months covered: {date_range.dt.to_period('M').nunique()}")
                
                if 'amount_kzt' in df.columns:
                    valid_amounts = df['amount_kzt'].dropna()
                    if len(valid_amounts) > 0:
                        context_parts.append(f"\n=== REVENUE STATISTICS ===")
                        context_parts.append(f"Total revenue: {valid_amounts.sum():,.2f} KZT")
                        context_parts.append(f"Average transaction: {valid_amounts.mean():,.2f} KZT")
                        context_parts.append(f"Median transaction: {valid_amounts.median():,.2f} KZT")
                        context_parts.append(f"Min: {valid_amounts.min():,.2f} KZT, Max: {valid_amounts.max():,.2f} KZT")
                
                if 'channel' in df.columns:
                    channel_stats = df.groupby('channel').agg({
                        'amount_kzt': ['sum', 'count', 'mean'],
                        'transaction_id': 'nunique' if 'transaction_id' in df.columns else 'count'
                    }).round(2)
                    context_parts.append(f"\n=== CHANNEL DISTRIBUTION ===")
                    for channel in channel_stats.index:
                        total = channel_stats.loc[channel, ('amount_kzt', 'sum')]
                        count = channel_stats.loc[channel, ('amount_kzt', 'count')]
                        avg = channel_stats.loc[channel, ('amount_kzt', 'mean')]
                        pct = (total / valid_amounts.sum() * 100) if len(valid_amounts) > 0 and valid_amounts.sum() > 0 else 0
                        context_parts.append(f"{channel}: {total:,.2f} KZT ({pct:.1f}%), {count} transactions, avg {avg:,.2f} KZT")
                
                if 'merchant_category' in df.columns:
                    category_stats = df.groupby('merchant_category').agg({
                        'amount_kzt': ['sum', 'count', 'mean']
                    }).round(2)
                    context_parts.append(f"\n=== MERCHANT CATEGORY DISTRIBUTION ===")
                    for category in category_stats.index:
                        total = category_stats.loc[category, ('amount_kzt', 'sum')]
                        count = category_stats.loc[category, ('amount_kzt', 'count')]
                        avg = category_stats.loc[category, ('amount_kzt', 'mean')]
                        pct = (total / valid_amounts.sum() * 100) if len(valid_amounts) > 0 and valid_amounts.sum() > 0 else 0
                        context_parts.append(f"{category}: {total:,.2f} KZT ({pct:.1f}%), {count} transactions")
                
                if 'city' in df.columns:
                    city_stats = df.groupby('city').agg({
                        'amount_kzt': ['sum', 'count']
                    }).round(2).sort_values(('amount_kzt', 'sum'), ascending=False).head(15)
                    context_parts.append(f"\n=== TOP CITIES BY REVENUE ===")
                    for city in city_stats.index:
                        total = city_stats.loc[city, ('amount_kzt', 'sum')]
                        count = city_stats.loc[city, ('amount_kzt', 'count')]
                        context_parts.append(f"{city}: {total:,.2f} KZT, {count} transactions")
                
                if 'region' in df.columns:
                    region_stats = df.groupby('region').agg({
                        'amount_kzt': ['sum', 'count']
                    }).round(2).sort_values(('amount_kzt', 'sum'), ascending=False)
                    context_parts.append(f"\n=== REGION DISTRIBUTION ===")
                    for region in region_stats.index:
                        total = region_stats.loc[region, ('amount_kzt', 'sum')]
                        count = region_stats.loc[region, ('amount_kzt', 'count')]
                        context_parts.append(f"{region}: {total:,.2f} KZT, {count} transactions")
                
                if 'payment_method' in df.columns:
                    payment_stats = df.groupby('payment_method').agg({
                        'amount_kzt': ['sum', 'count']
                    }).round(2).sort_values(('amount_kzt', 'sum'), ascending=False)
                    context_parts.append(f"\n=== PAYMENT METHOD DISTRIBUTION ===")
                    for method in payment_stats.index:
                        total = payment_stats.loc[method, ('amount_kzt', 'sum')]
                        count = payment_stats.loc[method, ('amount_kzt', 'count')]
                        pct = (total / valid_amounts.sum() * 100) if len(valid_amounts) > 0 and valid_amounts.sum() > 0 else 0
                        context_parts.append(f"{method}: {total:,.2f} KZT ({pct:.1f}%), {count} transactions")
                
                if 'customer_segment' in df.columns:
                    segment_stats = df.groupby('customer_segment').agg({
                        'amount_kzt': ['sum', 'count']
                    }).round(2).sort_values(('amount_kzt', 'sum'), ascending=False)
                    context_parts.append(f"\n=== CUSTOMER SEGMENT DISTRIBUTION ===")
                    for segment in segment_stats.index:
                        total = segment_stats.loc[segment, ('amount_kzt', 'sum')]
                        count = segment_stats.loc[segment, ('amount_kzt', 'count')]
                        context_parts.append(f"{segment}: {total:,.2f} KZT, {count} transactions")
                
                if 'date' in df.columns and not df['date'].isna().all():
                    df['year_month'] = df['date'].dt.to_period('M').astype(str)
                    monthly_trends = df.groupby('year_month').agg({
                        'amount_kzt': ['sum', 'count']
                    }).round(2)
                    context_parts.append(f"\n=== MONTHLY TRENDS ===")
                    for month in monthly_trends.index:
                        total = monthly_trends.loc[month, ('amount_kzt', 'sum')]
                        count = monthly_trends.loc[month, ('amount_kzt', 'count')]
                        context_parts.append(f"{month}: {total:,.2f} KZT, {count} transactions")
                
                if 'is_refunded' in df.columns:
                    refunded_count = df['is_refunded'].sum()
                    refunded_pct = (refunded_count / len(df) * 100) if len(df) > 0 else 0
                    context_parts.append(f"\n=== TRANSACTION STATUS ===")
                    context_parts.append(f"Refunded transactions: {refunded_count} ({refunded_pct:.2f}%)")
                
                if 'is_canceled' in df.columns:
                    canceled_count = df['is_canceled'].sum()
                    canceled_pct = (canceled_count / len(df) * 100) if len(df) > 0 else 0
                    context_parts.append(f"Canceled transactions: {canceled_count} ({canceled_pct:.2f}%)")
                
                valid_transactions = len(df[(df.get('is_refunded', 0) == 0) & (df.get('is_canceled', 0) == 0)])
                context_parts.append(f"Valid transactions: {valid_transactions} ({valid_transactions/len(df)*100:.2f}%)")
                
                if 'suspicious_flag' in df.columns:
                    suspicious_count = df['suspicious_flag'].sum()
                    suspicious_pct = (suspicious_count / len(df) * 100) if len(df) > 0 else 0
                    context_parts.append(f"Suspicious transactions: {suspicious_count} ({suspicious_pct:.2f}%)")
                
                context = "\n".join(context_parts)
                
                sources.append({
                    "content": f"Dataset summary: {len(df)} transactions from {date_range.min() if 'date' in df.columns else 'N/A'} to {date_range.max() if 'date' in df.columns else 'N/A'}",
                    "metadata": {
                        "total_transactions": len(df),
                        "date_range": f"{date_range.min()} to {date_range.max()}" if 'date' in df.columns and len(date_range) > 0 else "N/A"
                    },
                    "relevance_score": 1.0
                })
                
        except Exception as e:
            print(f"Warning: Could not get comprehensive data context: {e}")
            import traceback
            traceback.print_exc()
            try:
                data_service = get_data_service()
                relevant_data = data_service.get_relevant_data_for_question(question, limit=50)
                if relevant_data:
                    context_parts = [f"Sample of {len(relevant_data)} transactions:"]
                    for i, doc in enumerate(relevant_data[:20], 1):
                        context_parts.append(f"{i}. {doc.get('content', '')}")
                    context = "\n".join(context_parts)
            except:
                pass
        
        answer = call_deepseek_api(question, context)
        
        return QuestionResponse(
            answer=answer,
            sources=sources,
            confidence=0.9 if context else 0.7
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )

@router.post("/stream", response_model=Dict[str, Any])
async def chat_message_stream(request: QuestionRequest):
    response = await chat_message(request)
    return response.model_dump()

