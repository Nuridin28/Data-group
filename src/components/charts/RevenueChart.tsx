import { useState } from 'react';
import {
  Box,
  ToggleButton,
  ToggleButtonGroup,
  useTheme,
} from '@mui/material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { formatCurrency } from '../../utils/format';
import type { RevenueData } from '../../types';
import { Typography } from '@mui/material';

interface RevenueChartProps {
  data: RevenueData[];
}

const RevenueChart = ({ data }: RevenueChartProps) => {
  const [chartType, setChartType] = useState<'line' | 'bar'>('line');
  const theme = useTheme();

  const handleChartTypeChange = (
    _event: React.MouseEvent<HTMLElement>,
    newType: 'line' | 'bar' | null,
  ) => {
    if (newType !== null) {
      setChartType(newType);
    }
  };

  if (!data || data.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <Typography color="text.secondary">Нет данных для отображения</Typography>
      </Box>
    );
  }

  const chartData = data.map((item) => ({
    date: new Date(item.date).toLocaleDateString('ru-KZ', { month: 'short', day: 'numeric' }),
    revenue: item.revenue,
    transactions: item.transactions_count,
  }));

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        <ToggleButtonGroup
          value={chartType}
          exclusive
          onChange={handleChartTypeChange}
          size="small"
        >
          <ToggleButton value="line">Линейный</ToggleButton>
          <ToggleButton value="bar">Столбчатый</ToggleButton>
        </ToggleButtonGroup>
      </Box>
      
      <ResponsiveContainer width="100%" height={400}>
        {chartType === 'line' ? (
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis 
              tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
            />
            <Tooltip 
              formatter={(value: number) => formatCurrency(value)}
              contentStyle={{
                backgroundColor: theme.palette.background.paper,
                border: `1px solid ${theme.palette.divider}`,
              }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="revenue" 
              stroke={theme.palette.primary.main} 
              strokeWidth={2}
              name="Выручка"
              dot={{ r: 4 }}
            />
            <Line 
              type="monotone" 
              dataKey="transactions" 
              stroke={theme.palette.secondary.main} 
              strokeWidth={2}
              name="Транзакции"
              dot={{ r: 4 }}
            />
          </LineChart>
        ) : (
          <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis 
              tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
            />
            <Tooltip 
              formatter={(value: number) => formatCurrency(value)}
              contentStyle={{
                backgroundColor: theme.palette.background.paper,
                border: `1px solid ${theme.palette.divider}`,
              }}
            />
            <Legend />
            <Bar dataKey="revenue" fill={theme.palette.primary.main} name="Выручка" />
            <Bar dataKey="transactions" fill={theme.palette.secondary.main} name="Транзакции" />
          </BarChart>
        )}
      </ResponsiveContainer>
    </Box>
  );
};

export default RevenueChart;
