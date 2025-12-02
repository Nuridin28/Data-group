import { useTheme, Box, Typography } from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { formatPercentage } from '../../utils/format';
import type { CohortData } from '../../types';

interface CohortAnalysisProps {
  data: CohortData[];
}

const CohortAnalysis = ({ data }: CohortAnalysisProps) => {
  const theme = useTheme();

  if (!data || data.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <Typography color="text.secondary">Нет данных для отображения</Typography>
      </Box>
    );
  }

  
  const cohortMap = new Map<string, CohortData[]>();
  data.forEach((item) => {
    const cohortKey = item.cohort || 'Unknown';
    if (!cohortMap.has(cohortKey)) {
      cohortMap.set(cohortKey, []);
    }
    cohortMap.get(cohortKey)!.push(item);
  });

  
  const cohorts = Array.from(cohortMap.keys()).slice(0, 10); 
  const maxPeriod = data.length > 0 ? Math.max(...data.map((d) => d.period || 0), 0) : 0;

  const chartData = Array.from({ length: Math.max(maxPeriod + 1, 1) }, (_, period) => {
    const entry: any = { period: `Период ${period}` };
    cohorts.forEach((cohort) => {
      const cohortData = cohortMap.get(cohort)?.find((d) => (d.period || 0) === period);
      entry[cohort] = cohortData ? (cohortData.retention || cohortData.retention_rate || 0) : 0;
    });
    return entry;
  });

  const COLORS = [
    theme.palette.primary.main,
    theme.palette.secondary.main,
    theme.palette.success.main,
    theme.palette.warning.main,
    theme.palette.error.main,
  ];

  const getColor = (value: number) => {
    if (value >= 80) return theme.palette.success.main;
    if (value >= 50) return theme.palette.warning.main;
    if (value >= 20) return theme.palette.error.light;
    return theme.palette.error.main;
  };

  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="period" />
        <YAxis tickFormatter={(value) => `${value}%`} />
        <Tooltip 
          formatter={(value: number) => formatPercentage(value)}
          contentStyle={{
            backgroundColor: theme.palette.background.paper,
            border: `1px solid ${theme.palette.divider}`,
          }}
        />
        <Legend />
        {cohorts.map((cohort, index) => (
          <Bar key={cohort} dataKey={cohort} stackId="a" fill={COLORS[index % COLORS.length]}>
            {chartData.map((entry, idx) => (
              <Cell key={`cell-${idx}`} fill={getColor(entry[cohort] || 0)} />
            ))}
          </Bar>
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
};

export default CohortAnalysis;
