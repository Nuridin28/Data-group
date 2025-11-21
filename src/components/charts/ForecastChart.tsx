import { useTheme, Box, Typography } from '@mui/material';
import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';
import { formatCurrency } from '../../utils/format';
import type { ForecastData } from '../../types';

interface ForecastChartProps {
  data: ForecastData[];
}

const ForecastChart = ({ data }: ForecastChartProps) => {
  const theme = useTheme();

  if (!data || data.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <Typography color="text.secondary">Нет данных для отображения</Typography>
      </Box>
    );
  }

  const chartData = data.map((item) => ({
    date: new Date(item.date).toLocaleDateString('ru-KZ', { month: 'short', day: 'numeric' }),
    predicted: item.predicted,
    lower_bound: item.lower_bound,
    upper_bound: item.upper_bound,
    actual: item.actual,
  }));

  return (
    <ResponsiveContainer width="100%" height={400}>
      <AreaChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <defs>
          <linearGradient id="colorPredicted" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={theme.palette.primary.main} stopOpacity={0.3}/>
            <stop offset="95%" stopColor={theme.palette.primary.main} stopOpacity={0}/>
          </linearGradient>
          <linearGradient id="colorConfidence" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={theme.palette.warning.main} stopOpacity={0.2}/>
            <stop offset="95%" stopColor={theme.palette.warning.main} stopOpacity={0}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`} />
        <Tooltip 
          formatter={(value: number) => formatCurrency(value)}
          contentStyle={{
            backgroundColor: theme.palette.background.paper,
            border: `1px solid ${theme.palette.divider}`,
          }}
        />
        <Legend />
        {data[0]?.lower_bound !== undefined && data[0]?.upper_bound !== undefined && (
          <Area
            type="monotone"
            dataKey="upper_bound"
            stroke="none"
            fillOpacity={0}
            fill="url(#colorConfidence)"
          />
        )}
        {data[0]?.lower_bound !== undefined && data[0]?.upper_bound !== undefined && (
          <Area
            type="monotone"
            dataKey="lower_bound"
            stroke="none"
            fillOpacity={0}
            fill="url(#colorConfidence)"
          />
        )}
        <Area
          type="monotone"
          dataKey="predicted"
          stroke={theme.palette.primary.main}
          strokeWidth={2}
          fill="url(#colorPredicted)"
          name="Прогноз"
        />
        {data[0]?.actual !== undefined && (
          <Line
            type="monotone"
            dataKey="actual"
            stroke={theme.palette.success.main}
            strokeWidth={2}
            name="Факт"
            dot={{ r: 4 }}
          />
        )}
      </AreaChart>
    </ResponsiveContainer>
  );
};

export default ForecastChart;
