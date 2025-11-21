import type { ChatMessage, AnalyticsResponse } from '../types';
import { formatCurrency, formatNumber, formatPercentage, formatDateTime } from './format';

// Helper function to escape HTML
const escapeHtml = (text: string): string => {
  const map: { [key: string]: string } = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  };
  return text.replace(/[&<>"']/g, (m) => map[m]);
};

// Convert markdown-like text to HTML
const markdownToHtml = (text: string): string => {
  let html = escapeHtml(text);
  
  // Convert headers
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
  
  // Convert bold
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Convert italic
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  
  // Convert code blocks
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  
  // Convert bullet lists
  const lines = html.split('\n');
  const processedLines: string[] = [];
  let inList = false;
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const listMatch = line.match(/^- (.+)$/);
    
    if (listMatch) {
      if (!inList) {
        processedLines.push('<ul>');
        inList = true;
      }
      processedLines.push(`<li>${listMatch[1]}</li>`);
    } else {
      if (inList) {
        processedLines.push('</ul>');
        inList = false;
      }
      processedLines.push(line);
    }
  }
  
  if (inList) {
    processedLines.push('</ul>');
  }
  
  html = processedLines.join('\n');
  
  // Convert line breaks
  html = html.replace(/\n/g, '<br>');
  
  return html;
};

export interface ReportData {
  chatHistory: ChatMessage[];
  analytics: AnalyticsResponse;
  generatedAt: Date;
  fileId?: string | null;
}

export const generateReport = (data: ReportData): string => {
  const { chatHistory, analytics, generatedAt, fileId } = data;
  
  const html = `
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Аналитический отчет - ${formatDateTime(generatedAt)}</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
      line-height: 1.6;
      color: #333;
      background: #f5f7fa;
      padding: 20px;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
      background: white;
      border-radius: 12px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      overflow: hidden;
    }
    .header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 40px;
      text-align: center;
    }
    .header h1 {
      font-size: 2.5em;
      margin-bottom: 10px;
      font-weight: 700;
    }
    .header p {
      opacity: 0.9;
      font-size: 1.1em;
    }
    .content {
      padding: 40px;
    }
    .section {
      margin-bottom: 40px;
    }
    .section-title {
      font-size: 1.8em;
      color: #667eea;
      margin-bottom: 20px;
      padding-bottom: 10px;
      border-bottom: 3px solid #667eea;
      font-weight: 600;
    }
    .summary-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }
    .summary-card {
      background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
      padding: 20px;
      border-radius: 8px;
      border-left: 4px solid #667eea;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .summary-card h3 {
      font-size: 0.9em;
      color: #666;
      margin-bottom: 8px;
      font-weight: 500;
    }
    .summary-card .value {
      font-size: 1.8em;
      font-weight: 700;
      color: #667eea;
    }
    .chat-message {
      margin-bottom: 20px;
      padding: 15px;
      border-radius: 8px;
      background: #f8f9fa;
    }
    .chat-message.user {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      margin-left: 40px;
    }
    .chat-message.assistant {
      background: white;
      border: 1px solid #e0e0e0;
      margin-right: 40px;
    }
    .chat-message .role {
      font-weight: 600;
      font-size: 0.9em;
      margin-bottom: 8px;
      opacity: 0.8;
    }
    .chat-message .content {
      line-height: 1.6;
    }
    .chat-message .timestamp {
      font-size: 0.8em;
      opacity: 0.6;
      margin-top: 8px;
    }
    .chat-message.user .content {
      white-space: pre-wrap;
    }
    .chat-message.assistant .content {
      color: #333;
    }
    .chat-message.assistant .content h1,
    .chat-message.assistant .content h2,
    .chat-message.assistant .content h3 {
      color: #667eea;
      margin-top: 16px;
      margin-bottom: 8px;
    }
    .chat-message.assistant .content h1 {
      font-size: 1.5em;
      border-bottom: 2px solid #667eea;
      padding-bottom: 4px;
    }
    .chat-message.assistant .content h2 {
      font-size: 1.3em;
    }
    .chat-message.assistant .content ul,
    .chat-message.assistant .content ol {
      margin-left: 20px;
      margin-bottom: 12px;
    }
    .chat-message.assistant .content li {
      margin-bottom: 6px;
    }
    .chat-message.assistant .content strong {
      color: #667eea;
    }
    .chat-message.assistant .content code {
      background: #f0f0f0;
      padding: 2px 6px;
      border-radius: 4px;
      font-family: 'Courier New', monospace;
    }
    .data-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .data-table th {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 12px;
      text-align: left;
      font-weight: 600;
    }
    .data-table td {
      padding: 12px;
      border-bottom: 1px solid #e0e0e0;
    }
    .data-table tr:hover {
      background: #f8f9fa;
    }
    .footer {
      background: #f8f9fa;
      padding: 20px 40px;
      text-align: center;
      color: #666;
      font-size: 0.9em;
    }
    .no-data {
      text-align: center;
      padding: 40px;
      color: #999;
      font-style: italic;
    }
    .risk-high {
      color: #d32f2f;
      font-weight: 600;
    }
    .risk-medium {
      color: #ed6c02;
      font-weight: 600;
    }
    .risk-low {
      color: #2e7d32;
      font-weight: 600;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Аналитический отчет</h1>
      <p>Сгенерировано: ${formatDateTime(generatedAt instanceof Date ? generatedAt : new Date(generatedAt))}</p>
      ${fileId ? `<p style="font-size: 0.9em; opacity: 0.8;">ID файла: ${escapeHtml(String(fileId))}</p>` : ''}
    </div>
    
    <div class="content">
      <!-- Summary Section -->
      <div class="section">
        <h2 class="section-title">Ключевые метрики</h2>
        <div class="summary-grid">
          <div class="summary-card">
            <h3>Общая выручка</h3>
            <div class="value">${formatCurrency(Number(analytics.summary?.total_revenue || 0))}</div>
          </div>
          <div class="summary-card">
            <h3>Всего транзакций</h3>
            <div class="value">${formatNumber(Number(analytics.summary?.total_transactions || 0))}</div>
          </div>
          <div class="summary-card">
            <h3>Активных клиентов</h3>
            <div class="value">${formatNumber(Number(analytics.summary?.active_customers || 0))}</div>
          </div>
          <div class="summary-card">
            <h3>Средний чек</h3>
            <div class="value">${formatCurrency(Number(analytics.summary?.avg_transaction_value || 0))}</div>
          </div>
          <div class="summary-card">
            <h3>Процент отмен</h3>
            <div class="value">${formatPercentage(Number(analytics.summary?.cancellation_rate || 0))}</div>
          </div>
        </div>
      </div>

      <!-- Top Channels -->
      ${analytics.revenue_by_channel && Array.isArray(analytics.revenue_by_channel) && analytics.revenue_by_channel.length > 0 ? `
      <div class="section">
        <h2 class="section-title">Топ каналов привлечения</h2>
        <table class="data-table">
          <thead>
            <tr>
              <th>Канал</th>
              <th>Выручка</th>
              <th>Транзакции</th>
              <th>Клиенты</th>
              <th>ROI</th>
            </tr>
          </thead>
          <tbody>
            ${analytics.revenue_by_channel.slice(0, 10).map(channel => `
              <tr>
                <td><strong>${escapeHtml(String(channel.channel || ''))}</strong></td>
                <td>${formatCurrency(Number(channel.revenue || 0))}</td>
                <td>${formatNumber(Number(channel.transactions || 0))}</td>
                <td>${formatNumber(Number(channel.customers || 0))}</td>
                <td>${formatPercentage(Number(channel.roi || 0))}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
      ` : ''}

      <!-- Anomalies -->
      ${analytics.anomalies && Array.isArray(analytics.anomalies) && analytics.anomalies.length > 0 ? `
      <div class="section">
        <h2 class="section-title">Выявленные аномалии (${analytics.anomalies.length})</h2>
        <table class="data-table">
          <thead>
            <tr>
              <th>ID транзакции</th>
              <th>Дата</th>
              <th>Сумма</th>
              <th>Уровень риска</th>
              <th>Причина</th>
            </tr>
          </thead>
          <tbody>
            ${analytics.anomalies.slice(0, 50).map(anomaly => `
              <tr>
                <td>${escapeHtml(String(anomaly.transaction_id || ''))}</td>
                <td>${formatDateTime(anomaly.date)}</td>
                <td>${formatCurrency(Number(anomaly.amount || 0))}</td>
                <td class="risk-${anomaly.risk_level || 'medium'}">${(anomaly.risk_level || 'medium').toUpperCase()}</td>
                <td>${escapeHtml(String(anomaly.reason || ''))}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
      ` : ''}

      <!-- Recommendations -->
      ${analytics.recommendations && Array.isArray(analytics.recommendations) && analytics.recommendations.length > 0 ? `
      <div class="section">
        <h2 class="section-title">AI Рекомендации</h2>
        <table class="data-table">
            <thead>
            <tr>
              <th>Тип</th>
              <th>Рекомендация</th>
              <th>Ожидаемый эффект</th>
              <th>Приоритет</th>
              <th>Предположительная выгода</th>
              <th>Сложность внедрения</th>
            </tr>
          </thead>
          <tbody>
            ${analytics.recommendations.map(rec => `
              <tr>
                <td>${escapeHtml(String(rec.type || ''))}</td>
                <td><strong>${escapeHtml(String(rec.title || ''))}</strong><br><small>${escapeHtml(String(rec.description || ''))}</small></td>
                <td>${escapeHtml(String(rec.expected_impact || ''))}</td>
                <td class="risk-${rec.priority || 'medium'}">${(rec.priority || 'medium').toUpperCase()}</td>
                <td style="color: #10b981; font-weight: 600;">${escapeHtml(String(rec.estimated_benefit || 'Требует оценки'))}</td>
                <td>${escapeHtml(String(rec.implementation_effort || 'medium'))}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
      ` : ''}

      <!-- Chat History -->
      <div class="section">
        <h2 class="section-title">История чата с AI (${chatHistory.length - 1} сообщений)</h2>
        ${chatHistory && chatHistory.length > 1 ? chatHistory.slice(1).map((msg) => {
          const content = msg.role === 'assistant' 
            ? markdownToHtml(String(msg.content || ''))
            : escapeHtml(String(msg.content || '')).replace(/\n/g, '<br>');
          
          const timestamp = msg.timestamp instanceof Date 
            ? msg.timestamp 
            : new Date(msg.timestamp);
          
          return `
          <div class="chat-message ${msg.role}">
            <div class="role">${msg.role === 'user' ? '👤 Пользователь' : '🤖 AI Ассистент'}</div>
            <div class="content">${content}</div>
            <div class="timestamp">${formatDateTime(timestamp)}</div>
          </div>
        `;
        }).join('') : '<div class="no-data">История чата пуста</div>'}
      </div>
    </div>
    
    <div class="footer">
      <p>Отчет сгенерирован автоматически системой анализа транзакционных данных</p>
    </div>
  </div>
</body>
</html>
  `;
  
  return html;
};

export const downloadReport = (data: ReportData, filename?: string) => {
  const html = generateReport(data);
  const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename || `analytics_report_${new Date().toISOString().split('T')[0]}.html`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

