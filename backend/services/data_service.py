import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import settings

class DataService:
    
    def __init__(self, data_file: Optional[str] = None):
        self.df = None
        self.data_file = data_file or settings.DATA_FILE
        self._load_data()
    
    def _load_data(self) -> None:
        data_file = self.data_file
        if not os.path.exists(data_file):
            raise FileNotFoundError(f"Data file not found: {data_file}")
        
        self.df = pd.read_csv(data_file)
        
        if 'date' in self.df.columns:
            self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
        
        self.df = self.df.fillna("")
        
        numeric_columns = ['amount_kzt', 'is_refunded', 'is_canceled', 'suspicious_flag', 'delivery_time_hours']
        for col in numeric_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                if col in ['is_refunded', 'is_canceled', 'suspicious_flag']:
                    self.df[col] = self.df[col].fillna(0).astype(int)
                else:
                    self.df[col] = self.df[col].fillna(0)
    
    def _parse_date_filter(self, date_str: Optional[str]) -> Optional[pd.Timestamp]:
        if not date_str:
            return None
        
        date_str = str(date_str).strip()
        
        if date_str == "" or date_str.lower() in ["string", "none", "null"]:
            return None
        
        try:
            parsed = pd.to_datetime(date_str, errors='coerce')
            return parsed if pd.notna(parsed) else None
        except Exception as e:
            print(f"Warning: Could not parse date '{date_str}': {e}")
            return None
    
    def get_dataframe(self, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        df = self.df.copy()
        
        if filters:
            if 'start_date' in filters:
                start_date = self._parse_date_filter(filters.get('start_date'))
                if start_date is not None:
                    df = df[df['date'] >= start_date]
            
            if 'end_date' in filters:
                end_date = self._parse_date_filter(filters.get('end_date'))
                if end_date is not None:
                    df = df[df['date'] <= end_date]
            
            if 'region' in filters and filters.get('region'):
                region_val = str(filters['region']).strip()
                if region_val and region_val.lower() not in ['string', 'none', 'null', '']:
                    df = df[df['region'] == region_val]
            
            if 'city' in filters and filters.get('city'):
                city_val = str(filters['city']).strip()
                if city_val and city_val.lower() not in ['string', 'none', 'null', '']:
                    df = df[df['city'] == city_val]
            
            if 'merchant_category' in filters and filters.get('merchant_category'):
                category_val = str(filters['merchant_category']).strip()
                if category_val and category_val.lower() not in ['string', 'none', 'null', '']:
                    df = df[df['merchant_category'] == category_val]
            
            if 'channel' in filters and filters.get('channel'):
                channel_val = str(filters['channel']).strip()
                if channel_val and channel_val.lower() not in ['string', 'none', 'null', '']:
                    df = df[df['channel'] == channel_val]
        
        return df
    
    def get_revenue_analytics(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        df = self.get_dataframe(filters)
        
        valid_transactions = df[(df['is_refunded'] == 0) & (df['is_canceled'] == 0)]
        
        total_revenue = float(valid_transactions['amount_kzt'].sum())
        transaction_count = len(valid_transactions)
        avg_transaction = float(valid_transactions['amount_kzt'].mean()) if transaction_count > 0 else 0.0
        
        revenue_by_date = []
        if 'date' in valid_transactions.columns and not valid_transactions['date'].isna().all():
            try:
                daily_revenue = valid_transactions.groupby(valid_transactions['date'].dt.date)['amount_kzt'].agg(['sum', 'count']).reset_index()
                daily_revenue.columns = ['date', 'revenue', 'transactions']
                daily_revenue['date'] = daily_revenue['date'].astype(str)
                revenue_by_date = daily_revenue.to_dict('records')
            except Exception as e:
                print(f"Warning: Could not generate revenue by date: {e}")
                revenue_by_date = []
        
        revenue_by_city = []
        if 'city' in valid_transactions.columns:
            city_revenue = valid_transactions.groupby('city')['amount_kzt'].agg(['sum', 'count', 'mean']).reset_index()
            city_revenue.columns = ['city', 'revenue', 'transactions', 'avg_transaction']
            city_revenue = city_revenue.sort_values('revenue', ascending=False)
            revenue_by_city = city_revenue.to_dict('records')
        
        revenue_by_channel = []
        if 'channel' in valid_transactions.columns:
            channel_revenue = valid_transactions.groupby('channel')['amount_kzt'].agg(['sum', 'count', 'mean']).reset_index()
            channel_revenue.columns = ['channel', 'revenue', 'transactions', 'avg_transaction']
            channel_revenue = channel_revenue.sort_values('revenue', ascending=False)
            revenue_by_channel = channel_revenue.to_dict('records')
        
        return {
            "total_revenue": total_revenue,
            "transaction_count": transaction_count,
            "average_transaction": avg_transaction,
            "revenue_by_date": revenue_by_date,
            "revenue_by_city": revenue_by_city,
            "revenue_by_channel": revenue_by_channel
        }
    
    def get_channel_analytics(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        df = self.get_dataframe(filters)
        valid_transactions = df[(df['is_refunded'] == 0) & (df['is_canceled'] == 0)]
        
        if 'channel' not in valid_transactions.columns:
            return {"channel_performance": [], "best_channel": "", "worst_channel": ""}
        
        channel_stats = valid_transactions.groupby('channel').agg({
            'amount_kzt': ['sum', 'mean', 'count'],
            'is_refunded': 'sum',
            'is_canceled': 'sum'
        }).reset_index()
        
        channel_stats.columns = ['channel', 'total_revenue', 'avg_revenue', 'transaction_count', 'refunds', 'cancellations']
        
        channel_stats['refund_rate'] = (channel_stats['refunds'] / channel_stats['transaction_count'] * 100).fillna(0)
        channel_stats['cancellation_rate'] = (channel_stats['cancellations'] / channel_stats['transaction_count'] * 100).fillna(0)
        channel_stats['success_rate'] = 100 - channel_stats['refund_rate'] - channel_stats['cancellation_rate']
        
        channel_stats = channel_stats.sort_values('total_revenue', ascending=False)
        
        best_channel = channel_stats.iloc[0]['channel'] if len(channel_stats) > 0 else ""
        worst_channel = channel_stats.iloc[-1]['channel'] if len(channel_stats) > 0 else ""
        
        return {
            "channel_performance": channel_stats.to_dict('records'),
            "best_channel": best_channel,
            "worst_channel": worst_channel
        }
    
    def get_retention_analytics(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        df = self.get_dataframe(filters)
        valid_transactions = df[(df['is_refunded'] == 0) & (df['is_canceled'] == 0)].copy()
        
        if len(valid_transactions) == 0:
            return {
                "customer_segment_retention": [],
                "acquisition_source_performance": [],
                "retention_rate": 0.0
            }
        
        if 'date' in valid_transactions.columns:
            valid_transactions['date'] = pd.to_datetime(valid_transactions['date'], errors='coerce')
            valid_transactions = valid_transactions.dropna(subset=['date'])
        
        segment_retention = []
        
        if 'customer_segment' in valid_transactions.columns and 'date' in valid_transactions.columns and len(valid_transactions) > 0:
            segments = valid_transactions['customer_segment'].dropna().unique()
            
            date_range = (valid_transactions['date'].max() - valid_transactions['date'].min()).days if len(valid_transactions) > 0 else 0
            num_periods = max(4, min(12, date_range // 30)) if date_range > 0 else 4
            
            for segment in segments[:20]:
                segment_data = valid_transactions[valid_transactions['customer_segment'] == segment].copy()
                
                if len(segment_data) == 0:
                    continue
                
                segment_data['period'] = pd.cut(
                    (segment_data['date'] - segment_data['date'].min()).dt.days,
                    bins=num_periods,
                    labels=range(num_periods)
                )
                
                try:
                    period_stats = segment_data.groupby('period', observed=True).agg({
                        'transaction_id': 'nunique',
                        'amount_kzt': ['sum', 'mean', 'count']
                    }).reset_index()
                except Exception as e:
                    print(f"Error grouping by period: {e}")
                    period_stats = pd.DataFrame()
                
                first_period_data = segment_data[segment_data['period'] == 0] if 'period' in segment_data.columns else pd.DataFrame()
                initial_customers = first_period_data['transaction_id'].nunique() if len(first_period_data) > 0 and 'transaction_id' in first_period_data.columns else 0
                
                for period_idx in range(num_periods):
                    if len(period_stats) == 0:
                        period_data = pd.DataFrame()
                    else:
                        period_data = period_stats[period_stats['period'] == period_idx]
                    
                    current_customers = 0
                    revenue = 0.0
                    transaction_count = 0
                    
                    if len(period_data) > 0 and 'transaction_id' in period_data.columns:
                        if isinstance(period_data.columns, pd.MultiIndex):
                            current_customers = int(period_data[('transaction_id', 'nunique')].iloc[0]) if ('transaction_id', 'nunique') in period_data.columns else 0
                            revenue = float(period_data[('amount_kzt', 'sum')].iloc[0]) if ('amount_kzt', 'sum') in period_data.columns else 0.0
                            transaction_count = int(period_data[('amount_kzt', 'count')].iloc[0]) if ('amount_kzt', 'count') in period_data.columns else 0
                        else:
                            current_customers = int(period_data['transaction_id'].iloc[0]) if 'transaction_id' in period_data.columns and len(period_data) > 0 else 0
                            revenue = float(period_data.get('amount_kzt', pd.Series([0]))[0]) if 'amount_kzt' in period_data.columns and len(period_data) > 0 else 0.0
                            transaction_count = len(segment_data[segment_data['period'] == period_idx]) if 'period' in segment_data.columns else 0
                    
                    if initial_customers > 0:
                        retention = (current_customers / initial_customers * 100) if period_idx == 0 else (current_customers / max(initial_customers, 1) * 100)
                    else:
                        retention = 100.0 if current_customers > 0 else 0.0
                    
                    segment_retention.append({
                        "cohort": str(segment),
                        "segment": str(segment),
                        "period": int(period_idx),
                        "retention": float(retention),
                        "retention_rate": float(retention),
                        "customers": int(current_customers),
                        "count": int(current_customers),
                        "revenue": float(revenue),
                        "transactions": int(transaction_count)
                    })
        
        if len(segment_retention) == 0 and 'date' in valid_transactions.columns and len(valid_transactions) > 0:
            valid_transactions['cohort_month'] = valid_transactions['date'].dt.to_period('M').astype(str)
            cohorts = valid_transactions['cohort_month'].unique()[:12]
            
            for cohort_idx, cohort in enumerate(cohorts):
                cohort_data = valid_transactions[valid_transactions['cohort_month'] == cohort]
                customers = cohort_data['transaction_id'].nunique() if 'transaction_id' in cohort_data.columns else 0
                
                segment_retention.append({
                    "cohort": str(cohort),
                    "segment": str(cohort),
                    "period": int(cohort_idx),
                    "retention": 100.0 if customers > 0 else 0.0,
                    "retention_rate": 100.0 if customers > 0 else 0.0,
                    "customers": int(customers),
                    "count": int(customers),
                    "revenue": float(cohort_data['amount_kzt'].sum()) if 'amount_kzt' in cohort_data.columns else 0.0,
                    "transactions": len(cohort_data)
                })
        
        acquisition_performance = []
        if 'acquisition_source' in valid_transactions.columns:
            acquisition_stats = valid_transactions.groupby('acquisition_source').agg({
                'amount_kzt': ['sum', 'mean', 'count'],
                'transaction_id': 'nunique'
            }).reset_index()
            acquisition_stats.columns = ['acquisition_source', 'total_revenue', 'avg_transaction', 'transaction_count', 'unique_customers']
            acquisition_stats = acquisition_stats.sort_values('total_revenue', ascending=False)
            acquisition_performance = acquisition_stats.to_dict('records')
        
        total_transactions = len(df)
        refunded = df['is_refunded'].sum() if 'is_refunded' in df.columns else 0
        canceled = df['is_canceled'].sum() if 'is_canceled' in df.columns else 0
        retention_rate = ((total_transactions - refunded - canceled) / total_transactions * 100) if total_transactions > 0 else 0
        
        return {
            "customer_segment_retention": segment_retention,
            "acquisition_source_performance": acquisition_performance,
            "retention_rate": float(retention_rate)
        }
    
    def get_table_schema(self) -> Dict[str, Any]:
        schema = {
            "table_name": "transactions",
            "columns": []
        }
        
        for col in self.df.columns:
            col_info = {
                "name": col,
                "type": str(self.df[col].dtype),
                "sample_values": []
            }
            
            if self.df[col].dtype in ['int64', 'float64']:
                col_info["type"] = "numeric"
                if col in ['is_refunded', 'is_canceled', 'suspicious_flag']:
                    col_info["type"] = "boolean (0 or 1)"
                    col_info["sample_values"] = [0, 1]
                else:
                    col_info["sample_values"] = self.df[col].dropna().unique()[:10].tolist()
            elif self.df[col].dtype == 'object' or 'datetime' in str(self.df[col].dtype):
                if 'date' in col.lower():
                    col_info["type"] = "date"
                    col_info["sample_values"] = self.df[col].dropna().astype(str).unique()[:5].tolist()
                else:
                    col_info["type"] = "string"
                    col_info["sample_values"] = self.df[col].dropna().unique()[:10].tolist()
            
            schema["columns"].append(col_info)
        
        schema["total_rows"] = len(self.df)
        schema["sample_cities"] = self.df['city'].dropna().unique()[:20].tolist() if 'city' in self.df.columns else []
        schema["sample_channels"] = self.df['channel'].dropna().unique().tolist() if 'channel' in self.df.columns else []
        schema["sample_categories"] = self.df['merchant_category'].dropna().unique().tolist() if 'merchant_category' in self.df.columns else []
        
        return schema
    
    def get_relevant_data_for_question(self, question: str, limit: int = 50) -> List[Dict[str, Any]]:
        import re
        
        df = self.df.copy()
        original_count = len(df)
        
        question_lower = question.lower()
        
        cities_map = {
            'almaty': 'Almaty', 'алматы': 'Almaty', 'алмата': 'Almaty',
            'astana': 'Astana', 'астана': 'Astana', 'нур-султан': 'Astana',
            'shymkent': 'Shymkent', 'шимкент': 'Shymkent',
            'aktobe': 'Aktobe', 'актобе': 'Aktobe',
            'karaganda': 'Karaganda', 'караганда': 'Karaganda',
            'atyrau': 'Atyrau', 'атырау': 'Atyrau',
            'pavlodar': 'Pavlodar', 'павлодар': 'Pavlodar',
            'taraz': 'Taraz', 'тараз': 'Taraz',
            'oskemen': 'Oskemen', 'оскемен': 'Oskemen',
            'kostanay': 'Kostanay', 'костанай': 'Kostanay'
        }
        
        found_city = None
        for keyword, city_name in cities_map.items():
            if keyword in question_lower:
                found_city = city_name
                if 'city' in df.columns:
                    city_exact = df[df['city'].astype(str).str.strip().str.lower() == city_name.lower()]
                    if len(city_exact) > 0:
                        df = city_exact
                    else:
                        city_contains = df[df['city'].astype(str).str.contains(city_name, case=False, na=False)]
                        if len(city_contains) > 0:
                            df = city_contains
                        elif 'region' in df.columns:
                            region_filter = df['region'].astype(str).str.contains(city_name, case=False, na=False)
                            df = df[region_filter]
                break
        
        year_match = re.search(r'\b(20[0-9]{2})\b', question)
        if year_match:
            year = int(year_match.group(1))
            if 'date' in df.columns and not df['date'].isna().all():
                year_filter = df['date'].dt.year == year
                filtered_df = df[year_filter]
                if len(filtered_df) > 0:
                    df = filtered_df
        
        month_keywords = {
            'январь': 1, 'февраль': 2, 'март': 3, 'апрель': 4, 'май': 5, 'июнь': 6,
            'июль': 7, 'август': 8, 'сентябрь': 9, 'октябрь': 10, 'ноябрь': 11, 'декабрь': 12,
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        for keyword, month_num in month_keywords.items():
            if keyword in question_lower:
                if 'date' in df.columns and not df['date'].isna().all():
                    df = df[df['date'].dt.month == month_num]
                break
        
        channels = ['online_store', 'mobile_app', 'social_media', 'marketplace', 'offline_pos']
        for channel in channels:
            if channel.replace('_', ' ') in question_lower or channel in question_lower:
                if 'channel' in df.columns:
                    df = df[df['channel'].astype(str).str.contains(channel, case=False, na=False)]
                break
        
        categories = ['ecommerce', 'food_delivery', 'ride_hailing', 'retail', 'grocery', 'electronics', 'travel']
        for category in categories:
            if category.replace('_', ' ') in question_lower or category in question_lower:
                if 'merchant_category' in df.columns:
                    df = df[df['merchant_category'].astype(str).str.contains(category, case=False, na=False)]
                break
        
        if len(df) == original_count and len(df) > limit:
            if 'date' in df.columns and not df['date'].isna().all():
                df['year_month'] = df['date'].dt.to_period('M').astype(str)
                unique_periods = df['year_month'].nunique()
                
                if unique_periods > 1:
                    samples_per_period = max(1, limit // min(unique_periods, 12))
                    sampled_dfs = []
                    
                    periods = sorted(df['year_month'].dropna().unique())
                    
                    for period in periods[:12]:
                        period_data = df[df['year_month'] == period]
                        if len(period_data) > 0:
                            sample_size = min(samples_per_period, len(period_data))
                            sampled_dfs.append(period_data.sample(n=sample_size, random_state=42))
                    
                    if sampled_dfs:
                        df = pd.concat(sampled_dfs, ignore_index=True)
                        if len(df) > limit:
                            df = df.sample(n=limit, random_state=42)
                    else:
                        df = df.sample(min(limit, len(df)), random_state=42)
                else:
                    df['date_only'] = df['date'].dt.date
                    unique_dates = df['date_only'].nunique()
                    
                    if unique_dates > 1:
                        samples_per_date = max(1, limit // min(unique_dates, 30))
                        sampled_dfs = []
                        
                        dates = sorted(df['date_only'].dropna().unique())
                        if len(dates) > 30:
                            step = len(dates) // 30
                            selected_dates = dates[::step][:30]
                        else:
                            selected_dates = dates
                        
                        for date_val in selected_dates:
                            date_data = df[df['date_only'] == date_val]
                            if len(date_data) > 0:
                                sample_size = min(samples_per_date, len(date_data))
                                sampled_dfs.append(date_data.sample(n=sample_size, random_state=42))
                        
                        if sampled_dfs:
                            df = pd.concat(sampled_dfs, ignore_index=True)
                            if len(df) > limit:
                                df = df.sample(n=limit, random_state=42)
                        else:
                            df = df.sample(min(limit, len(df)), random_state=42)
                    else:
                        df = df.sample(min(limit, len(df)), random_state=42)
            else:
                df = df.sample(min(limit, len(df)), random_state=42)
        elif len(df) == 0:
            if year_match and 'date' in self.df.columns:
                df = self.df.copy()
                if found_city:
                    for keyword, city_name in cities_map.items():
                        if keyword in question_lower:
                            if 'city' in df.columns:
                                city_exact = df[df['city'].astype(str).str.strip().str.lower() == city_name.lower()]
                                if len(city_exact) > 0:
                                    df = city_exact
                                else:
                                    city_contains = df[df['city'].astype(str).str.contains(city_name, case=False, na=False)]
                                    if len(city_contains) > 0:
                                        df = city_contains
                            break
                if 'date' in df.columns and len(df) > limit:
                    df['year_month'] = df['date'].dt.to_period('M').astype(str)
                    unique_periods = df['year_month'].nunique()
                    
                    if unique_periods > 1:
                        samples_per_period = max(1, limit // min(unique_periods, 12))
                        sampled_dfs = []
                        periods = sorted(df['year_month'].dropna().unique())
                        
                        for period in periods[:12]:
                            period_data = df[df['year_month'] == period]
                            if len(period_data) > 0:
                                sample_size = min(samples_per_period, len(period_data))
                                sampled_dfs.append(period_data.sample(n=sample_size, random_state=42))
                        
                        if sampled_dfs:
                            df = pd.concat(sampled_dfs, ignore_index=True)
                            if len(df) > limit:
                                df = df.sample(n=limit, random_state=42)
                        else:
                            df = df.sample(min(limit, len(df)), random_state=42)
                    else:
                        df = df.sample(min(limit, len(df)), random_state=42)
                else:
                    df = df.head(limit) if len(df) <= limit else df.sample(n=limit, random_state=42)
        elif len(df) > limit:
            if 'date' in df.columns and not df['date'].isna().all():
                df['year_month'] = df['date'].dt.to_period('M').astype(str)
                unique_periods = df['year_month'].nunique()
                
                if unique_periods > 1:
                    samples_per_period = max(1, limit // min(unique_periods, 12))
                    sampled_dfs = []
                    periods = sorted(df['year_month'].dropna().unique())
                    
                    for period in periods[:12]:
                        period_data = df[df['year_month'] == period]
                        if len(period_data) > 0:
                            sample_size = min(samples_per_period, len(period_data))
                            sampled_dfs.append(period_data.sample(n=sample_size, random_state=42))
                    
                    if sampled_dfs:
                        df = pd.concat(sampled_dfs, ignore_index=True)
                        if len(df) > limit:
                            df = df.sample(n=limit, random_state=42)
                    else:
                        df = df.sample(min(limit, len(df)), random_state=42)
                else:
                    df = df.sample(min(limit, len(df)), random_state=42)
            else:
                df = df.sample(min(limit, len(df)), random_state=42)
        
        for col in ['date_only', 'year_month']:
            if col in df.columns:
                df = df.drop(col, axis=1)
        
        results = []
        for idx, row in df.iterrows():
            content_parts = []
            if 'transaction_id' in row:
                content_parts.append(f"Transaction ID: {row['transaction_id']}")
            if 'date' in row and pd.notna(row['date']):
                content_parts.append(f"Date: {row['date']}")
            if 'region' in row and row['region']:
                content_parts.append(f"Region: {row['region']}")
            if 'city' in row and row['city']:
                content_parts.append(f"City: {row['city']}")
            if 'merchant_category' in row and row['merchant_category']:
                content_parts.append(f"Merchant Category: {row['merchant_category']}")
            if 'channel' in row and row['channel']:
                content_parts.append(f"Channel: {row['channel']}")
            if 'payment_method' in row and row['payment_method']:
                content_parts.append(f"Payment Method: {row['payment_method']}")
            if 'amount_kzt' in row and pd.notna(row['amount_kzt']):
                content_parts.append(f"Amount: {row['amount_kzt']} KZT")
            if 'customer_segment' in row and row['customer_segment']:
                content_parts.append(f"Customer Segment: {row['customer_segment']}")
            
            content = ". ".join(content_parts) + "."
            
            result = {
                "content": content,
                "metadata": {
                    "transaction_id": int(row.get('transaction_id', idx)) if pd.notna(row.get('transaction_id', idx)) else int(idx),
                    "date": str(row.get('date', '')),
                    "city": str(row.get('city', '')),
                    "region": str(row.get('region', '')),
                    "amount_kzt": float(row.get('amount_kzt', 0)) if pd.notna(row.get('amount_kzt', 0)) else 0.0,
                    "channel": str(row.get('channel', '')),
                    "merchant_category": str(row.get('merchant_category', '')),
                    "payment_method": str(row.get('payment_method', '')),
                    "customer_segment": str(row.get('customer_segment', '')),
                    "row_index": int(idx)
                },
                "score": 1.0
            }
            results.append(result)
        
        return results

_data_service = None

def get_data_service() -> DataService:
    global _data_service
    if _data_service is None:
        _data_service = DataService()
    return _data_service

def reload_data_service(data_file: str = None) -> DataService:
    global _data_service
    
    if data_file is None:
        data_file = settings.DATA_FILE
    
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Data file not found: {data_file}")
    
    try:
        _data_service = DataService(data_file=data_file)
        print(f"Data service reloaded with file: {data_file}")
        return _data_service
    except Exception as e:
        print(f"Error reloading data service: {e}")
        raise

