import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Box,
  Typography,
} from '@mui/material';
import { formatCurrency, formatDateTime } from '../utils/format';
import type { AnomalyData } from '../types';

interface AnomaliesTableProps {
  data: AnomalyData[];
}

const AnomaliesTable = ({ data }: AnomaliesTableProps) => {
  if (!data || data.length === 0) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">Аномалии не обнаружены</Typography>
      </Box>
    );
  }

  const getRiskColor = (risk: string) => {
    switch (risk) {
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

  const getRiskLabel = (risk: string) => {
    switch (risk) {
      case 'high':
        return 'Высокий';
      case 'medium':
        return 'Средний';
      case 'low':
        return 'Низкий';
      default:
        return risk;
    }
  };

  return (
    <Box>
      <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
        <Table size="small">
          <TableHead>
            <TableRow sx={{ bgcolor: 'background.default' }}>
              <TableCell><strong>ID Транзакции</strong></TableCell>
              <TableCell><strong>Дата</strong></TableCell>
              <TableCell align="right"><strong>Сумма</strong></TableCell>
              <TableCell align="right"><strong>Оценка аномалии</strong></TableCell>
              <TableCell><strong>Канал / Метод оплаты</strong></TableCell>
              <TableCell><strong>Причина подозрения</strong></TableCell>
              <TableCell align="center"><strong>Уровень риска</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.slice(0, 50).map((row) => (
              <TableRow 
                key={row.transaction_id} 
                hover
                sx={{ 
                  '&:nth-of-type(odd)': { bgcolor: 'action.hover' },
                  borderLeft: row.risk_level === 'high' ? '4px solid' : 'none',
                  borderLeftColor: row.risk_level === 'high' ? 'error.main' : 'transparent'
                }}
              >
                <TableCell>
                  <Typography variant="body2" fontFamily="monospace">
                    {row.transaction_id}
                  </Typography>
                </TableCell>
                <TableCell>{formatDateTime(row.date)}</TableCell>
                <TableCell align="right">
                  <Typography variant="body2" fontWeight="medium">
                    {formatCurrency(row.amount)}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 0.5 }}>
                    <Typography 
                      variant="body2" 
                      fontWeight="bold"
                      color={row.anomaly_score > 0.8 ? 'error.main' : row.anomaly_score > 0.6 ? 'warning.main' : 'info.main'}
                    >
                      {(row.anomaly_score * 100).toFixed(1)}%
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Box>
                    {row.channel && (
                      <Typography variant="caption" display="block" color="text.secondary">
                        {row.channel}
                      </Typography>
                    )}
                    {row.payment_method && (
                      <Typography variant="caption" display="block" color="text.secondary">
                        {row.payment_method}
                      </Typography>
                    )}
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" sx={{ maxWidth: 400 }}>
                    {row.reason}
                  </Typography>
                  {(row.is_refunded === 1 || row.is_canceled === 1) && (
                    <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
                      {row.is_refunded === 1 && (
                        <Chip label="Возврат" size="small" color="warning" variant="outlined" />
                      )}
                      {row.is_canceled === 1 && (
                        <Chip label="Отмена" size="small" color="error" variant="outlined" />
                      )}
                    </Box>
                  )}
                </TableCell>
                <TableCell align="center">
                  <Chip
                    label={getRiskLabel(row.risk_level)}
                    color={getRiskColor(row.risk_level) as any}
                    size="small"
                    sx={{ fontWeight: 'bold' }}
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      {data.length > 50 && (
        <Box sx={{ p: 2, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Показано 50 из {data.length} аномалий. Отсортировано по уровню риска.
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default AnomaliesTable;
