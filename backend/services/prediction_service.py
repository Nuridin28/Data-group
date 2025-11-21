import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.data_service import get_data_service
from config.config import settings

class PredictionService:
    
    def __init__(self):
        self.data_service = get_data_service()
        self.cancellation_model = None
        self.suspicious_model = None
        self.channel_encoder = None
        self.suspicious_feature_columns = []
        self._train_models()
    
    def _train_models(self) -> None:
        try:
            self._train_cancellation_model()
            self._train_suspicious_model()
        except Exception as e:
            print(f"Warning: Could not train all models: {e}")
    
    def _train_cancellation_model(self) -> None:
        df = self.data_service.get_dataframe()
        
        feature_columns = ['amount_kzt', 'channel', 'payment_method', 'customer_segment', 
                          'merchant_category', 'city', 'device_type']
        
        available_cols = [col for col in feature_columns if col in df.columns]
        if len(available_cols) < 3:
            return
        
        X = df[available_cols].copy()
        y = df['is_canceled'].astype(int)
        
        label_encoders = {}
        for col in X.select_dtypes(include=['object']).columns:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            label_encoders[col] = le
        
        mask = ~X.isna().any(axis=1)
        X = X[mask]
        y = y[mask]
        
        if len(X) < 100:
            return
        
        self.cancellation_model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        self.cancellation_model.fit(X, y)
        self.cancellation_label_encoders = label_encoders
        self.cancellation_feature_columns = available_cols
    
    def _train_suspicious_model(self) -> None:
        df = self.data_service.get_dataframe()
        
        # Используем только базовые числовые колонки, которые всегда есть
        feature_columns = ['amount_kzt', 'is_refunded', 'is_canceled']
        
        # Добавляем channel_encoded если есть channel
        if 'channel' in df.columns:
            try:
                le_channel = LabelEncoder()
                df_copy = df.copy()
                df_copy['channel_encoded'] = le_channel.fit_transform(df_copy['channel'].astype(str))
                feature_columns.append('channel_encoded')
                self.channel_encoder = le_channel
            except Exception as e:
                print(f"Warning: Could not encode channel: {e}")
                self.channel_encoder = None
        
        # Используем только существующие колонки
        available_cols = [col for col in feature_columns if col in df.columns or (col == 'channel_encoded' and 'channel' in df.columns)]
        
        # Создаем X с нужными колонками
        X = df.copy()
        if 'channel_encoded' in available_cols and 'channel_encoded' not in X.columns and 'channel' in X.columns:
            if hasattr(self, 'channel_encoder') and self.channel_encoder is not None:
                X['channel_encoded'] = self.channel_encoder.transform(X['channel'].astype(str))
            else:
                le_channel = LabelEncoder()
                X['channel_encoded'] = le_channel.fit_transform(X['channel'].astype(str))
                self.channel_encoder = le_channel
        
        X = X[available_cols].copy()
        mask = ~X.isna().any(axis=1)
        X = X[mask]
        
        if len(X) < 100:
            print(f"Warning: Not enough data for suspicious model training: {len(X)} rows")
            return
        
        try:
            self.suspicious_model = IsolationForest(contamination=0.1, random_state=42)
            self.suspicious_model.fit(X)
            self.suspicious_feature_columns = available_cols
        except Exception as e:
            print(f"Warning: Could not train suspicious model: {e}")
            self.suspicious_model = None
            self.suspicious_feature_columns = []
    
    def predict_transaction_volume(self, days_ahead: int = 30, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        df = self.data_service.get_dataframe(filters)
        valid_transactions = df[(df['is_refunded'] == 0) & (df['is_canceled'] == 0)]
        
        if 'date' not in valid_transactions.columns or valid_transactions['date'].isna().all():
            avg_daily = len(valid_transactions) / 365 if len(valid_transactions) > 0 else 0
            predictions = []
            for i in range(days_ahead):
                predictions.append({
                    "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
                    "predicted_volume": int(avg_daily),
                    "predicted_revenue": float(avg_daily * valid_transactions['amount_kzt'].mean() if len(valid_transactions) > 0 else 0)
                })
            
            return {
                "predicted_volume": predictions,
                "predicted_total_revenue": sum(p['predicted_revenue'] for p in predictions),
                "confidence_interval": {"lower": 0.8, "upper": 1.2}
            }
        
        daily_stats = valid_transactions.groupby(valid_transactions['date'].dt.date).agg({
            'transaction_id': 'count',
            'amount_kzt': 'sum'
        }).reset_index()
        daily_stats.columns = ['date', 'volume', 'revenue']
        
        if len(daily_stats) < 7:
            avg_volume = daily_stats['volume'].mean() if len(daily_stats) > 0 else 0
            avg_revenue = daily_stats['revenue'].mean() if len(daily_stats) > 0 else 0
        else:
            window = min(7, len(daily_stats))
            avg_volume = daily_stats['volume'].tail(window).mean()
            avg_revenue = daily_stats['revenue'].tail(window).mean()
            
            if len(daily_stats) >= 14:
                recent_avg = daily_stats['volume'].tail(7).mean()
                older_avg = daily_stats['volume'].tail(14).head(7).mean()
                trend_factor = recent_avg / older_avg if older_avg > 0 else 1.0
            else:
                trend_factor = 1.0
            
            avg_volume = avg_volume * trend_factor
            avg_revenue = avg_revenue * trend_factor
        
        predictions = []
        if len(daily_stats) > 0 and 'date' in daily_stats.columns:
            try:
                last_date = pd.to_datetime(daily_stats['date'].max()).date() if pd.notna(daily_stats['date'].max()) else datetime.now().date()
            except:
                last_date = datetime.now().date()
        else:
            last_date = datetime.now().date()
        
        std_volume = float(daily_stats['volume'].std()) if len(daily_stats) > 0 and pd.notna(daily_stats['volume'].std()) else float(avg_volume * 0.2) if avg_volume > 0 else 0.0
        
        
        for i in range(days_ahead):
            pred_date = last_date + timedelta(days=i+1)
            variation = (i % 7 - 3) * std_volume * 0.1 if std_volume > 0 else 0
            pred_volume = max(0, int(avg_volume + variation))
            pred_revenue = float(pred_volume * (avg_revenue / avg_volume if avg_volume > 0 else 0))
            
            predictions.append({
                "date": pred_date.strftime("%Y-%m-%d"),
                "predicted_volume": pred_volume,
                "predicted_revenue": pred_revenue
            })
        
        total_revenue = sum(p['predicted_revenue'] for p in predictions)
        
        return {
            "predicted_volume": predictions,
            "predicted_total_revenue": float(total_revenue),
            "confidence_interval": {"lower": 0.85, "upper": 1.15}
        }
    
    def predict_cancellation_probability(self, amount_kzt: float, channel: str, 
                                       payment_method: str, customer_segment: str,
                                       city: Optional[str] = None, 
                                       merchant_category: Optional[str] = None) -> Dict[str, Any]:
        if self.cancellation_model is None:
            df = self.data_service.get_dataframe()
            similar_transactions = df[
                (df['channel'] == channel) & 
                (df['payment_method'] == payment_method) &
                (df['customer_segment'] == customer_segment)
            ]
            
            if len(similar_transactions) > 0:
                cancellation_rate = similar_transactions['is_canceled'].mean()
            else:
                cancellation_rate = df['is_canceled'].mean()
            
            probability = float(cancellation_rate)
        else:
            try:
                features = {}
                for col in self.cancellation_feature_columns:
                    if col == 'amount_kzt':
                        features[col] = amount_kzt
                    elif col == 'channel':
                        features[col] = channel
                    elif col == 'payment_method':
                        features[col] = payment_method
                    elif col == 'customer_segment':
                        features[col] = customer_segment
                    elif col == 'city' and city:
                        features[col] = city
                    elif col == 'merchant_category' and merchant_category:
                        features[col] = merchant_category
                    else:
                        df = self.data_service.get_dataframe()
                        features[col] = df[col].mode()[0] if len(df[col].mode()) > 0 else ""
                
                X = pd.DataFrame([features])
                for col in X.select_dtypes(include=['object']).columns:
                    if col in self.cancellation_label_encoders:
                        try:
                            X[col] = self.cancellation_label_encoders[col].transform(X[col].astype(str))
                        except:
                            X[col] = 0
                
                prob = self.cancellation_model.predict_proba(X[self.cancellation_feature_columns])[0]
                probability = float(prob[1] if len(prob) > 1 else prob[0])
            except Exception as e:
                df = self.data_service.get_dataframe()
                probability = float(df['is_canceled'].mean())
        
        if probability < 0.1:
            risk_level = "low"
        elif probability < 0.3:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        df = self.data_service.get_dataframe()
        factors = []
        
        channel_cancel = df[df['channel'] == channel]['is_canceled'].mean() if channel in df['channel'].values else 0
        overall_cancel = df['is_canceled'].mean()
        if channel_cancel > overall_cancel * 1.2:
            factors.append({"factor": "channel", "impact": "high", "details": f"{channel} has higher cancellation rate"})
        
        pm_cancel = df[df['payment_method'] == payment_method]['is_canceled'].mean() if payment_method in df['payment_method'].values else 0
        if pm_cancel > overall_cancel * 1.2:
            factors.append({"factor": "payment_method", "impact": "high", "details": f"{payment_method} has higher cancellation rate"})
        
        if amount_kzt > df['amount_kzt'].quantile(0.9):
            factors.append({"factor": "amount", "impact": "medium", "details": "High-value transactions have higher cancellation risk"})
        
        return {
            "cancellation_probability": probability,
            "risk_level": risk_level,
            "factors": factors
        }
    
    def detect_suspicious_transactions(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100) -> Dict[str, Any]:
        df = self.data_service.get_dataframe(filters)
        
        if df is None or len(df) == 0:
            return {
                "suspicious_transactions": [],
                "total_suspicious": 0,
                "risk_factors": [],
                "model_insights": "No data available for analysis"
            }
        
        suspicious_indices = []
        anomaly_scores = {}
        model_reasons = {}
        
        # Calculate statistical baselines
        avg_amount = df['amount_kzt'].mean() if 'amount_kzt' in df.columns else 0
        std_amount = df['amount_kzt'].std() if 'amount_kzt' in df.columns else 0
        median_amount = df['amount_kzt'].median() if 'amount_kzt' in df.columns else 0
        
        # Use ML model if available
        if self.suspicious_model is not None and len(self.suspicious_feature_columns) > 0:
            try:
                X = df.copy()
                
                # Create channel_encoded if needed
                if 'channel_encoded' in self.suspicious_feature_columns and 'channel' in X.columns and 'channel_encoded' not in X.columns:
                    if hasattr(self, 'channel_encoder') and self.channel_encoder is not None:
                        try:
                            X['channel_encoded'] = self.channel_encoder.transform(X['channel'].astype(str))
                        except (ValueError, AttributeError):
                            from sklearn.preprocessing import LabelEncoder
                            le_channel = LabelEncoder()
                            X['channel_encoded'] = le_channel.fit_transform(X['channel'].astype(str))
                            self.channel_encoder = le_channel
                    else:
                        from sklearn.preprocessing import LabelEncoder
                        le_channel = LabelEncoder()
                        X['channel_encoded'] = le_channel.fit_transform(X['channel'].astype(str))
                        self.channel_encoder = le_channel
                
                available_cols = [col for col in self.suspicious_feature_columns if col in X.columns]
                
                if len(available_cols) > 0:
                    X = X[available_cols].copy()
                    mask = ~X.isna().any(axis=1)
                    X_clean = X[mask]
                    
                    if len(X_clean) > 0:
                        # Get predictions and decision function scores
                        predictions = self.suspicious_model.predict(X_clean)
                        
                        # Try to get anomaly scores
                        if hasattr(self.suspicious_model, 'decision_function'):
                            scores = self.suspicious_model.decision_function(X_clean)
                            # Convert to 0-1 scale where lower is more anomalous
                            min_score = scores.min()
                            max_score = scores.max()
                            if max_score > min_score:
                                normalized_scores = 1 - (scores - min_score) / (max_score - min_score)
                            else:
                                normalized_scores = [0.5] * len(scores)
                        elif hasattr(self.suspicious_model, 'score_samples'):
                            scores = self.suspicious_model.score_samples(X_clean)
                            # IsolationForest: lower scores = more anomalous
                            min_score = scores.min()
                            max_score = scores.max()
                            if max_score > min_score:
                                normalized_scores = 1 - (scores - min_score) / (max_score - min_score)
                            else:
                                normalized_scores = [0.5] * len(scores)
                        else:
                            normalized_scores = [0.7 if p == -1 else 0.3 for p in predictions]
                        
                        # Store scores and reasons
                        for idx, (orig_idx, pred, score) in enumerate(zip(X_clean.index, predictions, normalized_scores)):
                            if pred == -1:  # Anomaly
                                suspicious_indices.append(orig_idx)
                                anomaly_scores[orig_idx] = float(score)
                                
                                # Generate reason based on features
                                reasons = []
                                row = df.loc[orig_idx]
                                
                                if 'amount_kzt' in row and pd.notna(row['amount_kzt']):
                                    amount = float(row['amount_kzt'])
                                    if amount > avg_amount + 2 * std_amount:
                                        reasons.append(f"Сумма транзакции ({amount:,.0f} KZT) значительно превышает среднюю ({avg_amount:,.0f} KZT)")
                                    elif amount > median_amount * 3:
                                        reasons.append(f"Сумма транзакции в {amount/median_amount:.1f} раз выше медианной")
                                
                                if 'is_refunded' in row and row.get('is_refunded', 0) == 1:
                                    reasons.append("Транзакция была возвращена")
                                
                                if 'is_canceled' in row and row.get('is_canceled', 0) == 1:
                                    reasons.append("Транзакция была отменена")
                                
                                if 'channel' in row and pd.notna(row.get('channel')):
                                    channel = str(row.get('channel', ''))
                                    channel_refund_rate = df[df['channel'] == channel]['is_refunded'].mean() if 'is_refunded' in df.columns else 0
                                    if channel_refund_rate > 0.3:
                                        reasons.append(f"Канал '{channel}' имеет высокий процент возвратов ({channel_refund_rate*100:.1f}%)")
                                
                                if 'payment_method' in row and pd.notna(row.get('payment_method')):
                                    pm = str(row.get('payment_method', ''))
                                    pm_cancel_rate = df[df['payment_method'] == pm]['is_canceled'].mean() if 'is_canceled' in df.columns else 0
                                    if pm_cancel_rate > 0.2:
                                        reasons.append(f"Метод оплаты '{pm}' имеет высокий процент отмен ({pm_cancel_rate*100:.1f}%)")
                                
                                if not reasons:
                                    reasons.append("Модель обнаружила аномальный паттерн в данных транзакции")
                                
                                model_reasons[orig_idx] = "; ".join(reasons)
            except Exception as e:
                print(f"Error in ML suspicious detection: {e}")
        
        # Rule-based detection with detailed reasons
        suspicious_df_list = []
        
        # High amount transactions
        amount_threshold_99 = df['amount_kzt'].quantile(0.99) if 'amount_kzt' in df.columns else 0
        amount_threshold_95 = df['amount_kzt'].quantile(0.95) if 'amount_kzt' in df.columns else 0
        
        high_amount = df[df['amount_kzt'] > amount_threshold_99] if 'amount_kzt' in df.columns else pd.DataFrame()
        for idx, row in high_amount.iterrows():
            if idx not in suspicious_indices:
                suspicious_indices.append(idx)
                amount = float(row.get('amount_kzt', 0))
                percentile = (df['amount_kzt'] < amount).sum() / len(df) * 100
                anomaly_scores[idx] = min(0.95, 0.7 + (percentile - 99) / 10)
                model_reasons[idx] = f"Экстремально высокая сумма транзакции ({amount:,.0f} KZT) - выше {percentile:.1f}% всех транзакций"
                suspicious_df_list.append((idx, row))
        
        # High-value refunded transactions
        refunded_high = df[(df['is_refunded'] == 1) & (df['amount_kzt'] > amount_threshold_95)] if all(col in df.columns for col in ['is_refunded', 'amount_kzt']) else pd.DataFrame()
        for idx, row in refunded_high.iterrows():
            if idx not in suspicious_indices:
                suspicious_indices.append(idx)
                amount = float(row.get('amount_kzt', 0))
                anomaly_scores[idx] = 0.85
                model_reasons[idx] = f"Высокозначимая транзакция ({amount:,.0f} KZT) была возвращена - возможное мошенничество или ошибка"
                suspicious_df_list.append((idx, row))
        
        # High-value canceled transactions
        canceled_high = df[(df['is_canceled'] == 1) & (df['amount_kzt'] > amount_threshold_95)] if all(col in df.columns for col in ['is_canceled', 'amount_kzt']) else pd.DataFrame()
        for idx, row in canceled_high.iterrows():
            if idx not in suspicious_indices:
                suspicious_indices.append(idx)
                amount = float(row.get('amount_kzt', 0))
                anomaly_scores[idx] = 0.80
                model_reasons[idx] = f"Высокозначимая транзакция ({amount:,.0f} KZT) была отменена - подозрительная активность"
                suspicious_df_list.append((idx, row))
        
        # Rapid repeated transactions (potential card testing)
        if 'transaction_id' in df.columns and 'date' in df.columns:
            df_with_date = df.copy()
            if df_with_date['date'].dtype != 'datetime64[ns]':
                df_with_date['date'] = pd.to_datetime(df_with_date['date'], errors='coerce')
            
            # Group by potential customer identifier (if available)
            customer_col = None
            for col in ['customer_id', 'merchant_id', 'payment_method']:
                if col in df.columns:
                    customer_col = col
                    break
            
            if customer_col:
                rapid_transactions = df_with_date.groupby([customer_col, df_with_date['date'].dt.date]).size()
                rapid_customers = rapid_transactions[rapid_transactions > 10].index.get_level_values(0).unique()
                
                for customer in rapid_customers[:50]:  # Limit to avoid too many
                    customer_txns = df_with_date[df_with_date[customer_col] == customer]
                    for idx, row in customer_txns.iterrows():
                        if idx not in suspicious_indices and len(customer_txns) > 10:
                            suspicious_indices.append(idx)
                            anomaly_scores[idx] = 0.75
                            model_reasons[idx] = f"Подозрительно большое количество транзакций ({len(customer_txns)}) за короткий период - возможное тестирование карт"
                            suspicious_df_list.append((idx, row))
                            break  # Only flag one per customer
        
        # Combine all suspicious transactions
        suspicious_df = df.loc[suspicious_indices[:limit]].copy() if suspicious_indices else pd.DataFrame()
        
        suspicious_transactions = []
        for idx, row in suspicious_df.iterrows():
            score = anomaly_scores.get(idx, 0.5)
            reason = model_reasons.get(idx, "Обнаружена аномалия в данных транзакции")
            
            # Determine risk level
            if score >= 0.8:
                risk_level = "high"
            elif score >= 0.6:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            suspicious_transactions.append({
                "transaction_id": str(int(row.get('transaction_id', idx))) if pd.notna(row.get('transaction_id', idx)) else str(idx),
                "date": str(row.get('date', '')) if pd.notna(row.get('date', '')) else '',
                "city": str(row.get('city', '')) if pd.notna(row.get('city', '')) else 'Unknown',
                "channel": str(row.get('channel', '')) if pd.notna(row.get('channel', '')) else 'Unknown',
                "amount_kzt": float(row.get('amount_kzt', 0)) if pd.notna(row.get('amount_kzt', 0)) else 0.0,
                "is_refunded": int(row.get('is_refunded', 0)) if pd.notna(row.get('is_refunded', 0)) else 0,
                "is_canceled": int(row.get('is_canceled', 0)) if pd.notna(row.get('is_canceled', 0)) else 0,
                "suspicious_flag": int(row.get('suspicious_flag', 0)) if pd.notna(row.get('suspicious_flag', 0)) else 0,
                "merchant_category": str(row.get('merchant_category', '')) if pd.notna(row.get('merchant_category', '')) else 'Unknown',
                "payment_method": str(row.get('payment_method', '')) if pd.notna(row.get('payment_method', '')) else 'Unknown',
                "anomaly_score": float(score),
                "risk_score": float(score),
                "reason": reason,
                "risk_level": risk_level
            })
        
        # Sort by anomaly score descending
        suspicious_transactions.sort(key=lambda x: x.get('anomaly_score', 0), reverse=True)
        
        # Generate risk factors summary
        risk_factors = []
        if len(high_amount) > 0:
            risk_factors.append({
                "factor": "high_amount",
                "count": len(high_amount),
                "description": f"Транзакции выше 99-го перцентиля ({amount_threshold_99:,.0f} KZT)",
                "severity": "high"
            })
        if len(refunded_high) > 0:
            risk_factors.append({
                "factor": "refunded_high_value",
                "count": len(refunded_high),
                "description": f"Высокозначимые возвращенные транзакции (>{amount_threshold_95:,.0f} KZT)",
                "severity": "high"
            })
        if len(canceled_high) > 0:
            risk_factors.append({
                "factor": "canceled_high_value",
                "count": len(canceled_high),
                "description": f"Высокозначимые отмененные транзакции (>{amount_threshold_95:,.0f} KZT)",
                "severity": "medium"
            })
        
        # Calculate model insights
        model_insights = f"Проанализировано {len(df)} транзакций. Обнаружено {len(suspicious_transactions)} подозрительных операций. "
        if self.suspicious_model is not None:
            model_insights += "Использована ML-модель Isolation Forest для детекции аномалий. "
        model_insights += f"Средний score аномалии: {np.mean([t['anomaly_score'] for t in suspicious_transactions]):.2f}." if suspicious_transactions else "Аномалии не обнаружены."
        
        return {
            "suspicious_transactions": suspicious_transactions[:limit],
            "total_suspicious": len(suspicious_transactions),
            "risk_factors": risk_factors,
            "model_insights": model_insights
        }

_prediction_service = None

def get_prediction_service() -> PredictionService:
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = PredictionService()
    return _prediction_service

