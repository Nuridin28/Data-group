import { useState } from 'react';
import { Box, Container } from '@mui/material';
import FileUpload from './components/FileUpload';
import Dashboard from './components/Dashboard';
import { AnalyticsResponse } from './types';

function App() {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsResponse | null>(null);
  const [fileId, setFileId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileUploaded = (data: AnalyticsResponse, id: string) => {
    setAnalyticsData(data);
    setFileId(id);
    setIsLoading(false);
  };

  const handleUploadStart = () => {
    setIsLoading(true);
  };

  return (
    <Box 
      sx={{ 
        minHeight: '100vh', 
        bgcolor: 'background.default',
        background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.01) 0%, rgba(118, 75, 162, 0.01) 100%)',
      }}
    >
      <Container maxWidth={false} sx={{ py: 3 }}>
        {!analyticsData ? (
          <FileUpload 
            onUploaded={handleFileUploaded} 
            onUploadStart={handleUploadStart}
            isLoading={isLoading}
          />
        ) : (
          <Dashboard 
            data={analyticsData} 
            fileId={fileId}
            onReset={() => {
              setAnalyticsData(null);
              setFileId(null);
            }}
          />
        )}
      </Container>
    </Box>
  );
}

export default App;
