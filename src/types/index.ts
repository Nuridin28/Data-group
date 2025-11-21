export interface Transaction {
  id: string;
  date: string;
  amount: number;
  customer_id: string;
  channel: string;
  status: 'completed' | 'cancelled' | 'pending';
  product_category?: string;
  region?: string;
}

export interface RevenueData {
  date: string;
  revenue: number;
  transactions_count: number;
}

export interface CohortData {
  cohort: string;
  period: number;
  retention: number;
  retention_rate?: number;
  customers: number;
}

export interface ChannelData {
  channel: string;
  revenue: number;
  transactions: number;
  customers: number;
  roi: number;
  conversion_rate: number;
}

export interface ROIData {
  source: string;
  investment: number;
  revenue: number;
  roi: number;
  profit: number;
  transactions?: number;
  customers?: number;
  avg_transaction?: number;
  cpa?: number;
  conversion_rate?: number;
}

export interface ForecastData {
  date: string;
  predicted: number;
  lower_bound?: number;
  upper_bound?: number;
  actual?: number;
}

export interface AnomalyData {
  transaction_id: string;
  date: string;
  amount: number;
  anomaly_score: number;
  risk_score?: number;
  reason: string;
  risk_level: 'low' | 'medium' | 'high';
  city?: string;
  channel?: string;
  payment_method?: string;
  merchant_category?: string;
  is_refunded?: number;
  is_canceled?: number;
}

export interface Recommendation {
  id: string;
  type: 'discount' | 'marketing' | 'optimization';
  title: string;
  description: string;
  segment?: string;
  expected_impact: string;
  priority: 'high' | 'medium' | 'low';
  estimated_benefit?: string;
  implementation_effort?: 'low' | 'medium' | 'high';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface AnalyticsResponse {
  revenue_trend: RevenueData[];
  revenue_by_channel: ChannelData[];
  cohort_analysis: CohortData[];
  roi_metrics: ROIData[];
  forecasts?: {
    revenue_forecast: ForecastData[];
    cancellation_probability: number;
  };
  anomalies?: AnomalyData[];
  recommendations?: Recommendation[];
  summary: {
    total_revenue: number;
    total_transactions: number;
    active_customers: number;
    avg_transaction_value: number;
    cancellation_rate: number;
  };
}
