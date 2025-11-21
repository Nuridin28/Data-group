import { useState, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Alert,
  Paper,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Description as DescriptionIcon,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { uploadCSV, getAnalytics } from '../services/api';
import type { AnalyticsResponse } from '../types';

interface FileUploadProps {
  onUploaded: (data: AnalyticsResponse, fileId: string) => void;
  onUploadStart: () => void;
  isLoading: boolean;
}

const FileUpload = ({ onUploaded, onUploadStart, isLoading }: FileUploadProps) => {
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [fileName, setFileName] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      setError('Пожалуйста, загрузите CSV файл');
      return;
    }

    setError(null);
    setFileName(file.name);
    onUploadStart();
    setUploadProgress(0);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const uploadResponse = await uploadCSV(file);
      console.log('Upload response:', uploadResponse);
      setUploadProgress(95);
      clearInterval(progressInterval);

      // Небольшая задержка для обработки на бэкенде
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Fetch analytics
      console.log('Fetching analytics for file_id:', uploadResponse.file_id);
      setUploadProgress(98);
      const analyticsData = await getAnalytics(uploadResponse.file_id);
      console.log('Analytics data received:', analyticsData);
      
      setUploadProgress(100);
      onUploaded(analyticsData, uploadResponse.file_id);
    } catch (err: any) {
      console.error('Upload error:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Ошибка при загрузке файла';
      setError(errorMessage);
      setUploadProgress(0);
      setFileName(null);
    }
  }, [onUploaded, onUploadStart]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
    multiple: false,
    disabled: isLoading,
  });

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '80vh',
        background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.02) 0%, rgba(118, 75, 162, 0.02) 100%)',
      }}
    >
      <Card 
        sx={{ 
          maxWidth: 600, 
          width: '100%',
          border: '1px solid',
          borderColor: 'divider',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        }}
      >
        <CardContent sx={{ p: 4 }}>
          <Typography 
            variant="h4" 
            gutterBottom 
            align="center" 
            sx={{ 
              mb: 2,
              fontWeight: 700,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Анализ транзакционных данных
          </Typography>
          <Typography 
            variant="body2" 
            color="text.secondary" 
            align="center" 
            sx={{ mb: 4 }}
          >
            Загрузите CSV файл с транзакционными данными для анализа
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Paper
            {...getRootProps()}
            sx={{
              p: 4,
              border: '2px dashed',
              borderColor: isDragActive ? 'primary.main' : 'divider',
              bgcolor: isDragActive 
                ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)' 
                : 'background.paper',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              textAlign: 'center',
              transition: 'all 0.3s ease',
              borderRadius: 3,
              '&:hover': {
                borderColor: 'primary.main',
                bgcolor: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)',
                transform: 'translateY(-2px)',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
              },
            }}
          >
            <input {...getInputProps()} />
            <CloudUploadIcon 
              sx={{ 
                fontSize: 64, 
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 2,
                transition: 'transform 0.3s ease',
                ...(isDragActive && { transform: 'scale(1.1)' }),
              }} 
            />
            <Typography 
              variant="h6" 
              gutterBottom
              sx={{ 
                fontWeight: 600,
                color: isDragActive ? 'primary.main' : 'text.primary',
              }}
            >
              {isDragActive
                ? 'Отпустите файл здесь'
                : 'Перетащите CSV файл или нажмите для выбора'}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Поддерживаются файлы CSV до 100MB
            </Typography>
            <Button 
              variant="contained" 
              disabled={isLoading}
              sx={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                boxShadow: 'none',
                '&:hover': {
                  background: 'linear-gradient(135deg, #5568d3 0%, #653a8f 100%)',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                },
                '&:disabled': {
                  background: 'action.disabledBackground',
                },
                transition: 'all 0.3s ease',
              }}
            >
              Выбрать файл
            </Button>
          </Paper>

          {fileName && (
            <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
              <DescriptionIcon color="primary" />
              <Typography variant="body2">{fileName}</Typography>
            </Box>
          )}

          {isLoading && (
            <Box sx={{ mt: 3 }}>
              <LinearProgress variant="determinate" value={uploadProgress} />
              <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
                Загрузка и обработка данных... {uploadProgress}%
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default FileUpload;
