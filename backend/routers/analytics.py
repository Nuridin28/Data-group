from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional, List
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.schemas import (
    AnalyticsRequest, RevenueResponse, ChannelResponse, RetentionResponse, TransactionListItem,
    RecommendationsResponse, RecommendationItem, ROIMetricsResponse
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
        
        question = f"""Проанализируй данные по выручке на русском языке:
- Общая выручка: {revenue_data['total_revenue']:,.2f} KZT
- Количество транзакций: {revenue_data['transaction_count']}
- Средняя транзакция: {revenue_data['average_transaction']:,.2f} KZT
- Топ городов: {revenue_data['revenue_by_city'][:5] if revenue_data['revenue_by_city'] else 'N/A'}
- Топ каналов: {revenue_data['revenue_by_channel'][:5] if revenue_data['revenue_by_channel'] else 'N/A'}

Предоставь анализ трендов выручки, эффективности городов и каналов. Определи возможности для роста. ОТВЕТЬ НА РУССКОМ ЯЗЫКЕ."""
        
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
        
        question = f"""Проанализируй эффективность каналов на русском языке:
{channel_data['channel_performance']}

Лучший канал: {channel_data['best_channel']}
Худший канал: {channel_data['worst_channel']}

Предоставь рекомендации по оптимизации каналов и распределению маркетингового бюджета. ОТВЕТЬ НА РУССКОМ ЯЗЫКЕ."""
        
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
        
        question = f"""Проанализируй ретеншн клиентов на русском языке:
- Общий уровень ретеншна: {retention_data['retention_rate']:.2f}%
- Эффективность сегментов клиентов: {retention_data['customer_segment_retention'][:5] if retention_data['customer_segment_retention'] else 'N/A'}
- Эффективность источников привлечения: {retention_data['acquisition_source_performance'][:5] if retention_data['acquisition_source_performance'] else 'N/A'}

Предоставь анализ трендов ретеншна и рекомендации по улучшению лояльности клиентов. ОТВЕТЬ НА РУССКОМ ЯЗЫКЕ."""
        
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
        
        transactions = df.head(limit).to_dict('records')
        
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

@router.post("/recommendations", response_model=RecommendationsResponse)
async def get_ai_recommendations(request: AnalyticsRequest = AnalyticsRequest()) -> RecommendationsResponse:
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
        
        revenue_data = data_service.get_revenue_analytics(filters)
        channel_data = data_service.get_channel_analytics(filters)
        retention_data = data_service.get_retention_analytics(filters)
        
        df = data_service.get_dataframe(filters)
        valid_transactions = df[(df['is_refunded'] == 0) & (df['is_canceled'] == 0)]
        
        best_channel_revenue = 0
        if channel_data.get('channel_performance'):
            for ch in channel_data.get('channel_performance', []):
                ch_revenue = float(ch.get('total_revenue', ch.get('revenue', 0)) or 0)
                if ch_revenue > best_channel_revenue:
                    best_channel_revenue = ch_revenue
        
        context = f"""ДАННЫЕ ДЛЯ АНАЛИЗА:

ВЫРУЧКА:
- Общая выручка: {revenue_data['total_revenue']:,.2f} KZT
- Транзакций: {revenue_data['transaction_count']}
- Средний чек: {revenue_data['average_transaction']:,.2f} KZT

КАНАЛЫ ПРИВЛЕЧЕНИЯ:
{chr(10).join([f"- {ch.get('channel', 'N/A')}: {float(ch.get('total_revenue', ch.get('revenue', 0)) or 0):,.0f} KZT, {ch.get('transaction_count', ch.get('transactions', 0))} транзакций" for ch in channel_data.get('channel_performance', [])[:10]])}

Лучший канал: {channel_data.get('best_channel', 'N/A')}
Худший канал: {channel_data.get('worst_channel', 'N/A')}

РЕТЕНШН:
- Уровень ретеншна: {retention_data['retention_rate']:.2f}%
- Активных клиентов: {len(valid_transactions['transaction_id'].unique()) if 'transaction_id' in valid_transactions.columns else 0}

ДОПОЛНИТЕЛЬНАЯ СТАТИСТИКА:
- Процент возвратов: {(df['is_refunded'].sum() / len(df) * 100) if 'is_refunded' in df.columns and len(df) > 0 else 0:.2f}%
- Процент отмен: {(df['is_canceled'].sum() / len(df) * 100) if 'is_canceled' in df.columns and len(df) > 0 else 0:.2f}%"""

        question = f"""{context}

ТЫ ЭКСПЕРТ ПО БИЗНЕС-АНАЛИТИКЕ И ОПТИМИЗАЦИИ. ОБЯЗАТЕЛЬНО ОТВЕТЬ НА РУССКОМ ЯЗЫКЕ.

Создай структурированные рекомендации в следующем формате JSON (только JSON, без дополнительного текста):

{{
  "recommendations": [
    {{
      "id": "rec_1",
      "type": "marketing|optimization|discount",
      "title": "Краткое название рекомендации",
      "description": "Детальное описание рекомендации с конкретными числами и метриками",
      "expected_impact": "Ожидаемый эффект с конкретными цифрами",
      "priority": "high|medium|low",
      "segment": "целевой сегмент если применимо",
      "estimated_benefit": "Предположительная выгода в KZT или процентах",
      "implementation_effort": "low|medium|high"
    }}
  ],
  "analysis": "Общий анализ ситуации и обоснование рекомендаций на русском языке"
}}

КРИТИЧЕСКИ ВАЖНЫЕ ТРЕБОВАНИЯ:
1. ОБЯЗАТЕЛЬНО создай МИНИМУМ 5 конкретных, actionable рекомендаций для оптимизации бизнес-процессов
2. ОБЯЗАТЕЛЬНО используй конкретные числа из данных выше - НЕ придумывай данные
3. ОБЯЗАТЕЛЬНО определи приоритеты на основе потенциального impact
4. ОБЯЗАТЕЛЬНО укажи ожидаемый эффект с конкретными цифрами из данных
5. КРИТИЧЕСКИ ВАЖНО: ОБЯЗАТЕЛЬНО укажи estimated_benefit с конкретными числами в формате "+XXX,XXX KZT" или "+XX%". НЕ используй 0, "0 KZT" или пустые значения! Рассчитай на основе реальных данных.
6. Рассчитай estimated_benefit на основе данных: общая выручка {revenue_data.get('total_revenue', 0):,.0f} KZT, лучший канал показывает {best_channel_revenue:,.0f} KZT. ИСПОЛЬЗУЙ ЭТИ ЧИСЛА ДЛЯ РАСЧЕТА!
7. ОБЯЗАТЕЛЬНО укажи implementation_effort (low/medium/high) - сложность внедрения
8. ВСЕ тексты ОБЯЗАТЕЛЬНО на русском языке
9. ВЕРНИ ТОЛЬКО валидный JSON без markdown форматирования, без дополнительного текста до или после JSON
10. Если не можешь создать рекомендации на основе данных, все равно создай минимум 3 общие рекомендации с estimated_benefit на основе общей выручки {revenue_data.get('total_revenue', 0):,.0f} KZT

ФОРМАТ ОТВЕТА - ТОЛЬКО JSON:
{{"recommendations": [...], "analysis": "..."}}"""

        try:
            ai_result = rag_chain.query_with_analytics(question, {
                "revenue_data": revenue_data,
                "channel_data": channel_data,
                "retention_data": retention_data
            })
            answer = ai_result.get("answer", "")
            print(f"[Recommendations] LLM response length: {len(answer) if answer else 0}")
        except Exception as e:
            print(f"[Recommendations] Error calling LLM: {str(e)}")
            answer = ""
            ai_result = {"answer": ""}
        
        import json
        import re
        
        recommendations = []
        ai_analysis = answer
        
        total_revenue = float(revenue_data.get('total_revenue', 0) or 0)
        
        json_match = re.search(r'\{[\s\S]*\}', answer) if answer else None
        if json_match:
            try:
                json_str = json_match.group()
                print(f"[Recommendations] Found JSON in response, length: {len(json_str)}")
                parsed = json.loads(json_str)
                if 'recommendations' in parsed and isinstance(parsed['recommendations'], list):
                    print(f"[Recommendations] Parsed {len(parsed['recommendations'])} recommendations from LLM")
                    for rec in parsed['recommendations']:
                        estimated_benefit = rec.get('estimated_benefit', '').strip()
                        if not estimated_benefit or estimated_benefit == '0' or '0 KZT' in str(estimated_benefit) or estimated_benefit == '':
                            if 'маркетинг' in rec.get('type', '').lower() or 'marketing' in rec.get('type', '').lower():
                                if best_channel_revenue > 0:
                                    benefit_value = best_channel_revenue * 0.2
                                    estimated_benefit = f"+{benefit_value:,.0f} KZT выручки"
                                elif total_revenue > 0:
                                    benefit_value = total_revenue * 0.15
                                    estimated_benefit = f"+{benefit_value:,.0f} KZT выручки"
                                else:
                                    estimated_benefit = "Требует оценки на основе данных"
                            elif total_revenue > 0:
                                benefit_value = total_revenue * 0.1
                                estimated_benefit = f"+{benefit_value:,.0f} KZT выручки"
                            else:
                                estimated_benefit = "Требует оценки на основе данных"
                        
                        if not estimated_benefit or estimated_benefit.strip() == '' or '0 KZT' in estimated_benefit:
                            if total_revenue > 0:
                                estimated_benefit = f"+{total_revenue * 0.05:,.0f} KZT выручки"
                            else:
                                estimated_benefit = "Требует оценки"
                        
                        recommendations.append(RecommendationItem(
                            id=rec.get('id', f"rec_{len(recommendations)+1}"),
                            type=rec.get('type', 'optimization'),
                            title=rec.get('title', 'Рекомендация'),
                            description=rec.get('description', ''),
                            expected_impact=rec.get('expected_impact', ''),
                            priority=rec.get('priority', 'medium'),
                            segment=rec.get('segment'),
                            estimated_benefit=estimated_benefit,
                            implementation_effort=rec.get('implementation_effort', 'medium')
                        ))
                if 'analysis' in parsed:
                    ai_analysis = parsed['analysis']
            except json.JSONDecodeError as e:
                print(f"[Recommendations] JSON decode error: {str(e)}")
                print(f"[Recommendations] Response preview: {answer[:500] if answer else 'empty'}")
                pass
            except Exception as e:
                print(f"[Recommendations] Error parsing JSON: {str(e)}")
                pass
        
        if not recommendations and ai_analysis and len(ai_analysis) > 50:
            print(f"[Recommendations] Trying to extract recommendations from AI text analysis, length: {len(ai_analysis)}")
            lines = ai_analysis.split('\n')
            rec_count = 0
            for line in lines:
                if any(keyword in line.lower() for keyword in ['рекоменд', 'совет', 'увелич', 'оптимиз', 'улучш', 'сниж']):
                    if rec_count < 10:
                        rec_type = 'optimization'
                        if any(kw in line.lower() for kw in ['канал', 'маркетинг', 'реклам']):
                            rec_type = 'marketing'
                        elif any(kw in line.lower() for kw in ['скид', 'цена', 'стоимость']):
                            rec_type = 'discount'
                        
                        priority = 'medium'
                        if any(kw in line.lower() for kw in ['критич', 'сроч', 'немедлен', 'важн']):
                            priority = 'high'
                        elif any(kw in line.lower() for kw in ['долгосроч', 'постепен']):
                            priority = 'low'
                        
                        if rec_type == 'marketing' and best_channel_revenue > 0:
                            estimated_benefit = f"+{best_channel_revenue * 0.2:,.0f} KZT выручки"
                        elif total_revenue > 0:
                            estimated_benefit = f"+{total_revenue * 0.1:,.0f} KZT выручки"
                        else:
                            estimated_benefit = "Требует оценки на основе данных"
                        
                        recommendations.append(RecommendationItem(
                            id=f"rec_{rec_count+1}",
                            type=rec_type,
                            title=line[:100] if len(line) > 100 else line,
                            description=line,
                            expected_impact="Улучшение показателей на основе анализа данных",
                            priority=priority,
                            estimated_benefit=estimated_benefit,
                            implementation_effort=priority
                        ))
                        rec_count += 1
        
        if not recommendations or len(recommendations) == 0:
            print(f"[Recommendations] LLM returned no recommendations, creating fallback. Answer length: {len(answer) if answer else 0}")
            best_channel_revenue_fallback = 0
            if channel_data.get('best_channel') and channel_data.get('channel_performance'):
                for ch in channel_data.get('channel_performance', []):
                    if ch.get('channel') == channel_data['best_channel']:
                        best_channel_revenue_fallback = float(ch.get('total_revenue', ch.get('revenue', 0)) or 0)
                        break
            
            final_best_channel_revenue = best_channel_revenue if best_channel_revenue > 0 else best_channel_revenue_fallback
            final_total_revenue = float(revenue_data.get('total_revenue', 0) or 0)
            
            if final_best_channel_revenue > 0 and channel_data.get('best_channel'):
                estimated_benefit_value = final_best_channel_revenue * 0.2
                estimated_benefit = f"+{estimated_benefit_value:,.0f} KZT выручки" if estimated_benefit_value > 0 else "+10,000 KZT выручки"
                recommendations.append(RecommendationItem(
                    id="rec_1",
                    type="marketing",
                    title=f"Увеличить инвестиции в канал {channel_data['best_channel']}",
                    description=f"Канал {channel_data['best_channel']} показывает лучшие результаты по выручке ({final_best_channel_revenue:,.0f} KZT)",
                    expected_impact=f"Потенциальное увеличение выручки на 15-25%",
                    priority="high",
                    estimated_benefit=estimated_benefit,
                    implementation_effort="medium"
                ))
            
            if final_total_revenue > 0:
                estimated_benefit_value = final_total_revenue * 0.15
                estimated_benefit = f"+{estimated_benefit_value:,.0f} KZT выручки"
                recommendations.append(RecommendationItem(
                    id="rec_2",
                    type="optimization",
                    title="Оптимизировать работу с низкоэффективными каналами",
                    description=f"Перераспределить бюджет с низкоэффективных каналов на более успешные. Текущая выручка: {final_total_revenue:,.0f} KZT",
                    expected_impact="Улучшение ROI на 10-20%",
                    priority="medium",
                    estimated_benefit=estimated_benefit,
                    implementation_effort="low"
                ))
            
            if final_total_revenue > 0 or len(channel_data.get('channel_performance', [])) > 0:
                estimated_benefit_val = final_total_revenue * 0.1 if final_total_revenue > 0 else 50000
                estimated_benefit = f"+{estimated_benefit_val:,.0f} KZT выручки"
                recommendations.append(RecommendationItem(
                    id="rec_3",
                    type="optimization",
                    title="Улучшить аналитику и мониторинг каналов",
                    description="Внедрить систему постоянного мониторинга эффективности каналов привлечения для быстрой оптимизации",
                    expected_impact="Улучшение принятия решений на 20-30%",
                    priority="medium",
                    estimated_benefit=estimated_benefit,
                    implementation_effort="medium"
                ))
        
        final_recommendations = recommendations[:10] if len(recommendations) > 0 else []
        
        print(f"[Recommendations] Total recommendations before final check: {len(final_recommendations)}")
        
        if len(final_recommendations) == 0:
            print("[Recommendations] Creating fallback recommendation")
            total_rev = float(revenue_data.get('total_revenue', 0) or 0)
            estimated_benefit = f"+{total_rev * 0.1:,.0f} KZT выручки" if total_rev > 0 else "+50,000 KZT выручки"
            final_recommendations.append(RecommendationItem(
                id="rec_fallback",
                type="optimization",
                title="Проанализировать данные и оптимизировать процессы",
                description="На основе загруженных данных рекомендуется провести детальный анализ для выявления возможностей оптимизации",
                expected_impact="Улучшение показателей на основе данных",
                priority="medium",
                estimated_benefit=estimated_benefit,
                implementation_effort="medium"
            ))
        
        print(f"[Recommendations] Returning {len(final_recommendations)} recommendations")
        
        return RecommendationsResponse(
            recommendations=final_recommendations,
            ai_analysis=ai_analysis if ai_analysis else "Анализ данных для генерации рекомендаций"
        )
        
    except Exception as e:
        print(f"[Recommendations] Exception in get_recommendations: {str(e)}")
        try:
            data_service = get_data_service()
            revenue_data = data_service.get_revenue_analytics({})
            channel_data = data_service.get_channel_analytics({})
            total_rev = float(revenue_data.get('total_revenue', 0) or 0)
            
            fallback_recommendations = [
                RecommendationItem(
                    id="rec_error_1",
                    type="optimization",
                    title="Проанализировать данные и оптимизировать процессы",
                    description="На основе загруженных данных рекомендуется провести детальный анализ для выявления возможностей оптимизации",
                    expected_impact="Улучшение показателей на основе данных",
                    priority="medium",
                    estimated_benefit=f"+{total_rev * 0.1:,.0f} KZT выручки" if total_rev > 0 else "+50,000 KZT выручки",
                    implementation_effort="medium"
                )
            ]
            
            if channel_data.get('best_channel'):
                best_channel = channel_data['best_channel']
                fallback_recommendations.append(
                    RecommendationItem(
                        id="rec_error_2",
                        type="marketing",
                        title=f"Увеличить инвестиции в канал {best_channel}",
                        description=f"Канал {best_channel} показывает лучшие результаты",
                        expected_impact="Потенциальное увеличение выручки на 15-25%",
                        priority="high",
                        estimated_benefit=f"+{total_rev * 0.15:,.0f} KZT выручки" if total_rev > 0 else "+75,000 KZT выручки",
                        implementation_effort="medium"
                    )
                )
            
            print(f"[Recommendations] Returning {len(fallback_recommendations)} fallback recommendations due to error")
            return RecommendationsResponse(
                recommendations=fallback_recommendations,
                ai_analysis=f"Ошибка при генерации AI рекомендаций: {str(e)[:200]}. Показаны базовые рекомендации на основе данных."
            )
        except Exception as fallback_error:
            print(f"[Recommendations] Fallback also failed: {str(fallback_error)}")
            return RecommendationsResponse(
                recommendations=[
                    RecommendationItem(
                        id="rec_emergency",
                        type="optimization",
                        title="Требуется анализ данных",
                        description="Загрузите данные для получения детальных рекомендаций",
                        expected_impact="Улучшение показателей",
                        priority="medium",
                        estimated_benefit="Требует оценки",
                        implementation_effort="medium"
                    )
                ],
                ai_analysis="Не удалось сгенерировать рекомендации. Проверьте данные и настройки API."
            )

@router.post("/roi", response_model=ROIMetricsResponse)
async def get_roi_metrics(request: AnalyticsRequest = AnalyticsRequest()) -> ROIMetricsResponse:
    try:
        data_service = get_data_service()
        rag_chain = get_rag_chain()
        
        filters = {}
        if request.start_date:
            filters['start_date'] = request.start_date
        if request.end_date:
            filters['end_date'] = request.end_date
        
        df = data_service.get_dataframe(filters)
        valid_transactions = df[(df['is_refunded'] == 0) & (df['is_canceled'] == 0)]
        
        roi_metrics = []
        
        if 'acquisition_source' in valid_transactions.columns:
            source_stats = valid_transactions.groupby('acquisition_source').agg({
                'amount_kzt': ['sum', 'count', 'mean'],
                'transaction_id': 'nunique' if 'transaction_id' in valid_transactions.columns else 'count'
            }).reset_index()
            
            if isinstance(source_stats.columns, pd.MultiIndex):
                source_stats.columns = ['source', 'revenue', 'transactions', 'avg_transaction', 'customers']
            else:
                if len(source_stats.columns) >= 5:
                    source_stats.columns = ['source', 'revenue', 'transactions', 'avg_transaction', 'customers']
            
            for _, row in source_stats.iterrows():
                try:
                    source = str(row['source']) if pd.notna(row.get('source')) else 'unknown'
                    revenue = float(row['revenue']) if pd.notna(row.get('revenue')) and row.get('revenue') != '' else 0.0
                    transactions = int(row['transactions']) if pd.notna(row.get('transactions')) and row.get('transactions') != '' else 0
                    customers = int(row['customers']) if pd.notna(row.get('customers')) and row.get('customers') != '' else 0
                    avg_transaction = float(row['avg_transaction']) if pd.notna(row.get('avg_transaction')) and row.get('avg_transaction') != '' else 0.0
                    
                    if revenue <= 0 or pd.isna(revenue) or not pd.isfinite(revenue):
                        continue
                except (ValueError, KeyError, TypeError) as e:
                    print(f"Warning: Error processing row in ROI calculation: {e}")
                    continue
                
                investment_multipliers = {
                    'organic': 0.05,
                    'google_ads': 0.25,
                    'instagram': 0.15,
                    'facebook': 0.15,
                    'tiktok': 0.12,
                    'youtube': 0.18,
                    'email': 0.08,
                    'referral': 0.10,
                    'direct': 0.03,
                }
                
                multiplier = investment_multipliers.get(source.lower().strip(), 0.15)
                investment = revenue * multiplier
                
                if investment > 0 and revenue > 0:
                    roi = ((revenue - investment) / investment) * 100
                    if pd.isna(roi) or not pd.isfinite(roi):
                        roi = 0.0
                else:
                    roi = 0.0
                
                profit = revenue - investment
                
                cpa = investment / customers if customers > 0 else (investment / transactions if transactions > 0 else 0)
                
                conversion_rate = (customers / transactions * 100) if transactions > 0 else 0
                
                roi_metrics.append({
                    "source": source,
                    "investment": investment,
                    "revenue": revenue,
                    "roi": roi,
                    "profit": profit,
                    "transactions": transactions,
                    "customers": customers,
                    "avg_transaction": avg_transaction,
                    "cpa": cpa,
                    "conversion_rate": conversion_rate
                })
        else:
            channel_data = data_service.get_channel_analytics(filters)
            for channel in channel_data.get('channel_performance', []):
                revenue = float(channel.get('total_revenue', channel.get('revenue', 0)) or 0)
                transactions = int(channel.get('transaction_count', channel.get('transactions', 0)) or 0)
                
                if revenue <= 0:
                    continue
                
                investment = revenue * 0.15
                if investment > 0 and revenue > 0:
                    roi = ((revenue - investment) / investment) * 100
                    if pd.isna(roi) or not pd.isfinite(roi):
                        roi = 0.0
                else:
                    roi = 0.0
                profit = revenue - investment
                
                roi_metrics.append({
                    "source": channel.get('channel', 'Unknown'),
                    "investment": investment,
                    "revenue": revenue,
                    "roi": roi,
                    "profit": profit,
                    "transactions": transactions,
                    "customers": transactions,
                    "avg_transaction": revenue / transactions if transactions > 0 else 0,
                    "cpa": investment / transactions if transactions > 0 else 0,
                    "conversion_rate": 0
                })
        
        if len(roi_metrics) > 0:
            roi_metrics.sort(key=lambda x: x.get('roi', 0), reverse=True)
        else:
            channel_data_fallback = data_service.get_channel_analytics(filters)
            for channel in channel_data_fallback.get('channel_performance', [])[:5]:
                revenue = float(channel.get('total_revenue', channel.get('revenue', 0)) or 0)
                if revenue > 0:
                    transactions = int(channel.get('transaction_count', channel.get('transactions', 0)) or 0)
                    investment = revenue * 0.15
                    roi = ((revenue - investment) / investment * 100) if investment > 0 else 0
                    profit = revenue - investment
                    
                    roi_metrics.append({
                        "source": channel.get('channel', 'Unknown'),
                        "investment": investment,
                        "revenue": revenue,
                        "roi": roi,
                        "profit": profit,
                        "transactions": transactions,
                        "customers": transactions,
                        "avg_transaction": revenue / transactions if transactions > 0 else 0,
                        "cpa": investment / transactions if transactions > 0 else 0,
                        "conversion_rate": 0
                    })
        
        revenue_data = data_service.get_revenue_analytics(filters)
        
        context = f"""МЕТРИКИ ROI ПО ИСТОЧНИКАМ ПРИВЛЕЧЕНИЯ КЛИЕНТОВ (МАРКЕТИНГ):

{chr(10).join([f"- {m['source']}: Инвестиции {m['investment']:,.0f} KZT, Выручка {m['revenue']:,.0f} KZT, ROI {m['roi']:.1f}%, Прибыль {m['profit']:,.0f} KZT, Клиентов {m.get('customers', 0)}, CPA {m.get('cpa', 0):,.0f} KZT" for m in roi_metrics[:15]])}

ОБЩАЯ СТАТИСТИКА:
- Общая выручка: {revenue_data.get('total_revenue', 0):,.0f} KZT
- Всего транзакций: {revenue_data.get('transaction_count', 0)}
- Лучший источник по ROI: {roi_metrics[0]['source'] if roi_metrics else 'N/A'}
- Общие маркетинговые инвестиции: {sum(m.get('investment', 0) for m in roi_metrics):,.0f} KZT"""

        question = f"""{context}

ТЫ ЭКСПЕРТ ПО МАРКЕТИНГОВОЙ АНАЛИТИКЕ И ROI ОПТИМИЗАЦИИ ИСТОЧНИКОВ ПРИВЛЕЧЕНИЯ КЛИЕНТОВ. ОБЯЗАТЕЛЬНО ОТВЕТЬ НА РУССКОМ ЯЗЫКЕ.

Проанализируй ROI метрики по источникам привлечения клиентов и предоставь:
1. Детальный анализ эффективности каждого маркетингового источника
2. Конкретные рекомендации по перераспределению маркетингового бюджета
3. Определи лучшие возможности для увеличения инвестиций
4. Оцени потенциальный ROI и прибыль от оптимизации бюджета
5. Укажи конкретные цифры: сколько перераспределить, какой ожидаемый эффект
6. Проанализируй CPA (стоимость привлечения клиента) по источникам

Ответ должен быть на русском языке с конкретными рекомендациями, числами и расчетами."""

        ai_result = rag_chain.query_with_analytics(question, {
            "roi_metrics": roi_metrics,
            "revenue_data": revenue_data,
            "channel_data": channel_data
        })
        
        ai_analysis = ai_result.get("answer", "Анализ ROI метрик")
        best_opportunity = roi_metrics[0]['source'] if roi_metrics else None
        
        if ai_analysis and roi_metrics:
            for metric in roi_metrics[:3]:
                if metric['source'].lower() in ai_analysis.lower():
                    best_opportunity = metric['source']
                    break
        
        return ROIMetricsResponse(
            roi_metrics=roi_metrics,
            ai_analysis=ai_analysis,
            best_investment_opportunity=best_opportunity
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating ROI metrics: {str(e)}")

