import {
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Box,
  Typography,
  Paper,
} from '@mui/material';
import {
  LocalOffer as DiscountIcon,
  Campaign as MarketingIcon,
  TrendingUp as OptimizationIcon,
} from '@mui/icons-material';
import type { Recommendation } from '../types';

interface RecommendationsListProps {
  recommendations: Recommendation[];
}

const RecommendationsList = ({ recommendations }: RecommendationsListProps) => {
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

  return (
    <List>
      {recommendations.map((rec) => (
        <Paper key={rec.id} sx={{ mb: 2, p: 2 }} variant="outlined">
          <ListItem disableGutters>
            <ListItemIcon sx={{ minWidth: 40 }}>
              {getIcon(rec.type)}
            </ListItemIcon>
            <ListItemText
              primary={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                  <Typography variant="subtitle1" fontWeight={600}>
                    {rec.title}
                  </Typography>
                  <Chip
                    label={getTypeLabel(rec.type)}
                    size="small"
                    variant="outlined"
                  />
                  <Chip
                    label={getPriorityLabel(rec.priority)}
                    size="small"
                    color={getPriorityColor(rec.priority) as any}
                  />
                </Box>
              }
              secondary={
                <Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                    {rec.description}
                  </Typography>
                  {rec.segment && (
                    <Typography variant="caption" color="text.secondary">
                      Сегмент: {rec.segment}
                    </Typography>
                  )}
                  <Typography variant="caption" display="block" color="primary" sx={{ mt: 0.5 }}>
                    Ожидаемый эффект: {rec.expected_impact}
                  </Typography>
                </Box>
              }
            />
          </ListItem>
        </Paper>
      ))}
    </List>
  );
};

export default RecommendationsList;
