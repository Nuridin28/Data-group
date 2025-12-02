import { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  IconButton,
  Drawer,
  useMediaQuery,
  useTheme,
  Button,
  Tooltip,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Chat as ChatIcon,
  Close as CloseIcon,
  Download as DownloadIcon,
  Lightbulb as RecommendationsIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import RevenueChart from './charts/RevenueChart';
import ChannelComparison from './charts/ChannelComparison';
import CohortAnalysis from './charts/CohortAnalysis';
import ROIMetrics from './charts/ROIMetrics';
import SummaryCards from './SummaryCards';
import AIChatBot from './AIChatBot';
import ForecastChart from './charts/ForecastChart';
import AnomaliesTable from './AnomaliesTable';
import RecommendationsList from './RecommendationsList';
import { getAnalytics, getForecasts, getAnomalies, getRecommendations } from '../services/api';
import { downloadReport } from '../utils/report';
import type { AnalyticsResponse, ChatMessage } from '../types';

interface DashboardProps {
  data: AnalyticsResponse;
  fileId: string | null;
  onReset: () => void;
}

const Dashboard = ({ data: initialData, fileId, onReset }: DashboardProps) => {
  const [data, setData] = useState<AnalyticsResponse>(initialData);
  const [isLoading, setIsLoading] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [recommendationsOpen, setRecommendationsOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const refreshData = async () => {
    if (!fileId) return;
    setIsLoading(true);
    try {
      const [analytics, forecasts, anomalies, recommendations] = await Promise.all([
        getAnalytics(fileId),
        getForecasts(fileId),
        getAnomalies(fileId),
        getRecommendations(fileId),
      ]);
      
      setData({
        ...analytics,
        forecasts,
        anomalies,
        recommendations,
      });
    } catch (error) {
      console.error('Error refreshing data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    
    if (fileId && (!data.forecasts || !data.anomalies || !data.recommendations || (Array.isArray(data.recommendations) && data.recommendations.length === 0))) {
      console.log('[Dashboard] Loading recommendations for fileId:', fileId);
      refreshData();
    }
    
  }, [fileId]);

  const handleDownloadReport = () => {
    
    const messagesToExport = chatMessages.length > 0 ? chatMessages : [
      {
        id: '1',
        role: 'assistant' as const,
        content: 'История чата пуста',
        timestamp: new Date(),
      },
    ];
    
    downloadReport({
      chatHistory: messagesToExport,
      analytics: data,
      generatedAt: new Date(),
      fileId,
    });
  };

  const handleChatMessagesChange = (messages: ChatMessage[]) => {
    setChatMessages(messages);
  };

  return (
    <Box sx={{ position: 'relative' }}>
      {}
      <Box 
        sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          mb: 3,
          p: 3,
          background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)',
          borderRadius: 3,
          border: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Box>
          <Typography 
            variant="h4" 
            component="h1" 
            sx={{ 
              fontWeight: 700,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: 0.5,
            }}
          >
            Аналитический дашборд
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Комплексный анализ транзакционных данных
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Tooltip title="Скачать отчет">
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={handleDownloadReport}
              sx={{
                textTransform: 'none',
                borderRadius: 2,
                px: 2,
                borderColor: 'primary.main',
                color: 'primary.main',
                '&:hover': {
                  borderColor: 'primary.dark',
                  bgcolor: 'primary.main',
                  color: 'white',
                },
              }}
            >
              Отчет
            </Button>
          </Tooltip>
          <Tooltip title="Обновить данные">
            <IconButton 
              onClick={refreshData} 
              disabled={isLoading} 
              sx={{
                bgcolor: 'background.paper',
                border: '1px solid',
                borderColor: 'divider',
                '&:hover': {
                  bgcolor: 'action.hover',
                  transform: 'rotate(180deg)',
                  transition: 'transform 0.3s',
                },
                transition: 'all 0.3s',
              }}
            >
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Показать рекомендации">
            <IconButton
              onClick={() => setRecommendationsOpen(!recommendationsOpen)}
              sx={{
                bgcolor: recommendationsOpen ? 'warning.main' : 'background.paper',
                color: recommendationsOpen ? 'white' : 'warning.main',
                border: '1px solid',
                borderColor: recommendationsOpen ? 'warning.main' : 'divider',
                '&:hover': {
                  bgcolor: recommendationsOpen ? 'warning.dark' : 'action.hover',
                  transform: 'scale(1.05)',
                },
                transition: 'all 0.3s',
              }}
            >
              <RecommendationsIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="AI Ассистент">
            <IconButton
              onClick={() => setChatOpen(!chatOpen)}
              sx={{
                bgcolor: chatOpen ? 'primary.main' : 'background.paper',
                color: chatOpen ? 'white' : 'primary.main',
                border: '1px solid',
                borderColor: chatOpen ? 'primary.main' : 'divider',
                '&:hover': {
                  bgcolor: chatOpen ? 'primary.dark' : 'action.hover',
                  transform: 'scale(1.05)',
                },
                transition: 'all 0.3s',
              }}
            >
              <ChatIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Загрузить новый файл">
            <IconButton 
              onClick={onReset}
              sx={{
                bgcolor: 'background.paper',
                border: '1px solid',
                borderColor: 'divider',
                '&:hover': {
                  bgcolor: 'error.light',
                  color: 'white',
                  borderColor: 'error.main',
                },
                transition: 'all 0.3s',
              }}
            >
              <CloseIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {}
        <Grid item xs={12}>
          <SummaryCards summary={data.summary} />
        </Grid>

        {}
        <Grid item xs={12} lg={chatOpen && !isMobile ? 8 : 12}>
          <Paper 
            sx={{ 
              p: 3, 
              height: '100%',
              background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.02) 0%, rgba(118, 75, 162, 0.02) 100%)',
              border: '1px solid',
              borderColor: 'divider',
            }}
          >
            <Typography 
              variant="h6" 
              gutterBottom 
              sx={{ 
                fontWeight: 700,
                color: 'primary.main',
                mb: 2,
              }}
            >
              Динамика выручки
            </Typography>
            <RevenueChart data={data.revenue_trend} />
          </Paper>
        </Grid>

        {}
        {data.forecasts && data.forecasts.revenue_forecast && data.forecasts.revenue_forecast.length > 0 && (
          <Grid item xs={12} lg={chatOpen && !isMobile ? 8 : 12}>
            <Paper 
              sx={{ 
                p: 3, 
                height: '100%',
                background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.02) 0%, rgba(5, 150, 105, 0.02) 100%)',
                border: '1px solid',
                borderColor: 'divider',
              }}
            >
              <Typography 
                variant="h6" 
                gutterBottom 
                sx={{ 
                  fontWeight: 700,
                  color: 'success.main',
                  mb: 2,
                }}
              >
                Прогноз выручки
              </Typography>
              <ForecastChart data={data.forecasts.revenue_forecast} />
            </Paper>
          </Grid>
        )}

        {}
        <Grid item xs={12} md={12} lg={chatOpen && !isMobile ? 4 : 12}>
          <Paper 
            sx={{ 
              p: 3, 
              height: '100%',
              border: '1px solid',
              borderColor: 'divider',
            }}
          >
            <Typography 
              variant="h6" 
              gutterBottom 
              sx={{ 
                fontWeight: 700,
                color: 'text.primary',
                mb: 2,
              }}
            >
              Сравнение каналов привлечения
            </Typography>
            <ChannelComparison data={data.revenue_by_channel} />
          </Paper>
        </Grid>

        {}
/}

        {}
        <Grid item xs={12} lg={chatOpen && !isMobile ? 8 : 12}>
          <Paper 
            sx={{ 
              p: 3, 
              height: '100%',
              border: '1px solid',
              borderColor: 'divider',
            }}
          >
            <Typography 
              variant="h6" 
              gutterBottom 
              sx={{ 
                fontWeight: 700,
                color: 'text.primary',
                mb: 2,
              }}
            >
              Ретеншн клиентов по сегментам
            </Typography>
            <CohortAnalysis data={data.cohort_analysis} />
          </Paper>
        </Grid>

        {}
        {data.anomalies && Array.isArray(data.anomalies) && data.anomalies.length > 0 && (
          <Grid item xs={12} lg={chatOpen && !isMobile ? 8 : 12}>
            <Paper 
              sx={{ 
                p: 3,
                border: '1px solid',
                borderColor: 'divider',
                background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.02) 0%, rgba(220, 38, 38, 0.02) 100%)',
              }}
            >
              <Typography 
                variant="h6" 
                gutterBottom 
                sx={{ 
                  fontWeight: 700,
                  color: 'error.main',
                  mb: 2,
                }}
              >
                Выявленные аномалии и мошенничество
              </Typography>
              <AnomaliesTable data={data.anomalies} />
            </Paper>
          </Grid>
        )}

        {}
        {recommendationsOpen && (
          <Grid item xs={12} lg={chatOpen && !isMobile ? 8 : 12}>
            <Paper 
              sx={{ 
                p: 3,
                border: '1px solid',
                borderColor: 'divider',
                background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.02) 0%, rgba(217, 119, 6, 0.02) 100%)',
              }}
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Box>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      fontWeight: 700,
                      color: 'warning.main',
                      mb: 0.5,
                    }}
                  >
                    AI Рекомендации для оптимизации процессов
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Рекомендации по улучшению и оптимизации с предположительной выгодой
                  </Typography>
                </Box>
                <IconButton
                  onClick={() => setRecommendationsOpen(false)}
                  size="small"
                  sx={{
                    color: 'text.secondary',
                    '&:hover': {
                      bgcolor: 'action.hover',
                    },
                  }}
                >
                  <ExpandLessIcon />
                </IconButton>
              </Box>
              <RecommendationsList recommendations={data.recommendations || []} />
            </Paper>
          </Grid>
        )}
      </Grid>

      {}
      <Drawer
        anchor="right"
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        PaperProps={{
          sx: {
            width: { xs: '100%', sm: 400, md: 500 },
            p: 0,
            display: 'flex',
            flexDirection: 'column',
          },
        }}
      >
        <Box 
          sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            p: 2,
            borderBottom: '1px solid',
            borderColor: 'divider',
            background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)',
          }}
        >
          <Box>
            <Typography 
              variant="h6" 
              sx={{ 
                fontWeight: 700,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              AI Ассистент
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {chatMessages.length > 1 ? `${chatMessages.length - 1} сообщений` : 'Готов к общению'}
            </Typography>
          </Box>
          <IconButton 
            onClick={() => setChatOpen(false)} 
            size="small"
            sx={{
              '&:hover': {
                bgcolor: 'error.light',
                color: 'white',
              },
            }}
          >
            <CloseIcon />
          </IconButton>
        </Box>
        <Box sx={{ flex: 1, overflow: 'hidden' }}>
          <AIChatBot 
            fileId={fileId} 
            data={data} 
            onMessagesChange={handleChatMessagesChange}
          />
        </Box>
      </Drawer>
    </Box>
  );
};

export default Dashboard;
