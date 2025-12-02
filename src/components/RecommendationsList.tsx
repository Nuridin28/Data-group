import {
  Chip,
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  useTheme,
} from '@mui/material';
import {
  LocalOffer as DiscountIcon,
  Campaign as MarketingIcon,
  TrendingUp as OptimizationIcon,
  AttachMoney as MoneyIcon,
} from '@mui/icons-material';
import type { Recommendation } from '../types';

interface RecommendationsListProps {
  recommendations: Recommendation[];
}

const RecommendationsList = ({ recommendations }: RecommendationsListProps) => {
  const theme = useTheme();
  
  if (!recommendations || recommendations.length === 0) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">Рекомендации отсутствуют</Typography>
      </Box>
    );
  }

  const getIcon = (type: string) => {
    switch (type) {
      case 'discount':
        return <DiscountIcon />;
      case 'marketing':
        return <MarketingIcon />;
      case 'optimization':
        return <OptimizationIcon />;
      default:
        return <OptimizationIcon />;
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'discount':
        return 'Скидка';
      case 'marketing':
        return 'Маркетинг';
      case 'optimization':
        return 'Оптимизация';
      default:
        return type;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  const getPriorityLabel = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'Высокий';
      case 'medium':
        return 'Средний';
      case 'low':
        return 'Низкий';
      default:
        return priority;
    }
  };

  const getEffortLabel = (effort?: string) => {
    switch (effort) {
      case 'low':
        return 'Низкая';
      case 'medium':
        return 'Средняя';
      case 'high':
        return 'Высокая';
      default:
        return 'Не указана';
    }
  };

  const getEffortColor = (effort?: string) => {
    switch (effort) {
      case 'low':
        return 'success';
      case 'medium':
        return 'warning';
      case 'high':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <TableContainer>
      <Table sx={{ minWidth: 650 }}>
        <TableHead>
          <TableRow sx={{ bgcolor: 'action.hover' }}>
            <TableCell sx={{ fontWeight: 700 }}>Рекомендация</TableCell>
            <TableCell sx={{ fontWeight: 700 }} align="center">Тип</TableCell>
            <TableCell sx={{ fontWeight: 700 }} align="center">Приоритет</TableCell>
            <TableCell sx={{ fontWeight: 700 }} align="right">
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 0.5 }}>
                <MoneyIcon fontSize="small" />
                Предположительная выгода
              </Box>
            </TableCell>
            <TableCell sx={{ fontWeight: 700 }} align="center">Сложность внедрения</TableCell>
            <TableCell sx={{ fontWeight: 700 }}>Описание</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {recommendations.map((rec, index) => (
            <TableRow 
              key={rec.id} 
              sx={{ 
                '&:hover': { bgcolor: 'action.hover' },
                bgcolor: index % 2 === 0 ? 'background.paper' : 'action.hover',
              }}
            >
              <TableCell>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ color: theme.palette.primary.main }}>
              {getIcon(rec.type)}
                  </Box>
                  <Box>
                    <Typography variant="body2" fontWeight={600}>
                    {rec.title}
                  </Typography>
                    {rec.segment && (
                      <Typography variant="caption" color="text.secondary">
                        Сегмент: {rec.segment}
                      </Typography>
                    )}
                  </Box>
                </Box>
              </TableCell>
              <TableCell align="center">
                  <Chip
                    label={getTypeLabel(rec.type)}
                    size="small"
                    variant="outlined"
                  sx={{ minWidth: 100 }}
                  />
              </TableCell>
              <TableCell align="center">
                  <Chip
                    label={getPriorityLabel(rec.priority)}
                    size="small"
                    color={getPriorityColor(rec.priority) as any}
                  />
              </TableCell>
              <TableCell align="right">
                {rec.estimated_benefit ? (
                  <Typography 
                    variant="body2" 
                    fontWeight={700}
                    sx={{ 
                      color: theme.palette.success.main,
                    }}
                  >
                    {rec.estimated_benefit}
                  </Typography>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    Требует оценки
                  </Typography>
                )}
              </TableCell>
              <TableCell align="center">
                <Chip
                  label={getEffortLabel(rec.implementation_effort)}
                  size="small"
                  color={getEffortColor(rec.implementation_effort) as any}
                  variant="outlined"
                />
              </TableCell>
              <TableCell>
                <Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                    {rec.description}
                  </Typography>
                  <Typography variant="caption" color="primary" sx={{ fontStyle: 'italic' }}>
                    Эффект: {rec.expected_impact}
                  </Typography>
                </Box>
              </TableCell>
            </TableRow>
      ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default RecommendationsList;
