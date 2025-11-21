import { Box } from '@mui/material';
import { useTheme } from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { formatCurrency, formatPercentage } from '../../utils/format';
import type { ChannelData } from '../../types';
import { Typography } from '@mui/material';

interface ChannelComparisonProps {
  data: ChannelData[];
}

const ChannelComparison = ({ data }: ChannelComparisonProps) => {
  const theme = useTheme();

  if (!data || data.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
        <Typography color="text.secondary">Нет данных для отображения</Typography>
      </Box>
    );
  }

  const chartData = data.map((item) => ({
    name: item.channel,
    revenue: item.revenue,
    transactions: item.transactions,
    customers: item.customers,
    roi: item.roi,
    conversion: item.conversion_rate,
  }));

  const pieData = data.map((item) => ({
    name: item.channel,
    value: item.revenue,
  }));

  const COLORS = [
    theme.palette.primary.main,
    theme.palette.secondary.main,
    theme.palette.success.main,
    theme.palette.warning.main,
    theme.palette.error.main,
  ];

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
          <YAxis tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`} />
          <Tooltip 
            formatter={(value: number, name: string) => {
              if (name === 'roi' || name === 'conversion') {
                return formatPercentage(value);
              }
              return formatCurrency(value);
            }}
            contentStyle={{
              backgroundColor: theme.palette.background.paper,
              border: `1px solid ${theme.palette.divider}`,
            }}
          />
          <Legend />
          <Bar dataKey="revenue" fill={theme.palette.primary.main} name="Выручка" />
          <Bar dataKey="transactions" fill={theme.palette.secondary.main} name="Транзакции" />
        </BarChart>
      </ResponsiveContainer>

      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={pieData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {pieData.map((_entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value: number) => formatCurrency(value)}
            contentStyle={{
              backgroundColor: theme.palette.background.paper,
              border: `1px solid ${theme.palette.divider}`,
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default ChannelComparison;