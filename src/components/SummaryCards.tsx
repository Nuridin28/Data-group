import { Grid, Paper, Typography, Box } from '@mui/material';
import {
  AttachMoney as AttachMoneyIcon,
  ShoppingCart as ShoppingCartIcon,
  People as PeopleIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import { formatCurrency, formatNumber, formatPercentage } from '../utils/format';

interface Summary {
  total_revenue: number;
  total_transactions: number;
  active_customers: number;
  avg_transaction_value: number;
  cancellation_rate: number;
}

interface SummaryCardsProps {
  summary: Summary;
}

const SummaryCards = ({ summary }: SummaryCardsProps) => {
  const cards = [
    {
      title: 'Общая выручка',
      value: formatCurrency(summary.total_revenue),
      icon: <AttachMoneyIcon />,
      color: '#1976d2',
    },
    {
      title: 'Всего транзакций',
      value: formatNumber(summary.total_transactions),
      icon: <ShoppingCartIcon />,
      color: '#2e7d32',
    },
    {
      title: 'Активных клиентов',
      value: formatNumber(summary.active_customers),
      icon: <PeopleIcon />,
      color: '#9c27b0',
    },
    {
      title: 'Средний чек',
      value: formatCurrency(summary.avg_transaction_value),
      icon: <TrendingUpIcon />,
      color: '#ed6c02',
    },
    {
      title: 'Процент отмен',
      value: formatPercentage(summary.cancellation_rate),
      icon: <TrendingUpIcon />,
      color: summary.cancellation_rate > 10 ? '#d32f2f' : '#2e7d32',
    },
  ];

  return (
    <Grid container spacing={3}>
      {cards.map((card, index) => (
        <Grid item xs={12} sm={6} md={4} lg={2.4} key={index}>
          <Paper
            sx={{
              p: 3,
              height: '100%',
              background: `linear-gradient(135deg, ${card.color}15 0%, ${card.color}05 100%)`,
              borderLeft: `4px solid ${card.color}`,
              border: '1px solid',
              borderColor: 'divider',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: `0 10px 15px -3px ${card.color}30, 0 4px 6px -2px ${card.color}20`,
                borderLeftWidth: '6px',
              },
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
              <Box
                sx={{
                  color: card.color,
                  mr: 1.5,
                  display: 'flex',
                  alignItems: 'center',
                  p: 1,
                  borderRadius: 2,
                  bgcolor: `${card.color}10`,
                }}
              >
                {card.icon}
              </Box>
              <Typography 
                variant="body2" 
                color="text.secondary" 
                sx={{ 
                  fontSize: '0.875rem',
                  fontWeight: 500,
                }}
              >
                {card.title}
              </Typography>
            </Box>
            <Typography 
              variant="h5" 
              sx={{ 
                fontWeight: 700, 
                color: card.color,
                lineHeight: 1.2,
              }}
            >
              {card.value}
            </Typography>
          </Paper>
        </Grid>
      ))}
    </Grid>
  );
};

export default SummaryCards;
