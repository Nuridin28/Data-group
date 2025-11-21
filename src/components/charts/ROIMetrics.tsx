import { useTheme, Box, Typography } from '@mui/material';
import {
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Line,
  ComposedChart,
} from 'recharts';
import { formatCurrency, formatPercentage } from '../../utils/format';
import type { ROIData } from '../../types';

interface ROIMetricsProps {
  data: ROIData[];
}

const ROIMetrics = ({ data }: ROIMetricsProps) => {
  const theme = useTheme();

  if (!data || data.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 350 }}>
        <Typography color="text.secondary">Нет данных для отображения</Typography>
      </Box>
    );
  }

  const chartData = data.map((item) => ({
    source: item.source,
    roi: item.roi || 0,
    revenue: item.revenue || 0,
    investment: item.investment || 0,
    profit: item.profit || 0,
    customers: item.customers || 0,
    cpa: item.cpa || 0,
  }));

  return (
    <ResponsiveContainer width="100%" height={350}>
      <ComposedChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="source" angle={-45} textAnchor="end" height={80} />
        <YAxis yAxisId="left" tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`} />
        <YAxis yAxisId="right" orientation="right" tickFormatter={(value) => `${value}%`} />
        <Tooltip 
          formatter={(value: number, name: string) => {
            if (name === 'roi') {
              return formatPercentage(value);
            }
            if (name === 'cpa') {
              return `${formatCurrency(value)} на клиента`;
            }
            return formatCurrency(value);
          }}
          contentStyle={{
            backgroundColor: theme.palette.background.paper,
            border: `1px solid ${theme.palette.divider}`,
          }}
          labelFormatter={(label) => `Источник: ${label}`}
        />
        <Legend />
        <Bar 
          yAxisId="left" 
          dataKey="revenue" 
          fill={theme.palette.primary.main} 
          name="Выручка" 
        />
        <Bar 
          yAxisId="left" 
          dataKey="investment" 
          fill={theme.palette.warning.main} 
          name="Инвестиции" 
        />
        <Line 
          yAxisId="right" 
          type="monotone" 
          dataKey="roi" 
          stroke={theme.palette.success.main} 
          strokeWidth={3}
          name="ROI %"
          dot={{ r: 5 }}
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
};

export default ROIMetrics;
