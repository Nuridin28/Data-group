import { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Typography,
  CircularProgress,
  Avatar,
  Button,
  Tooltip,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  DeleteOutline as DeleteIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { sendChatMessage } from '../services/api';
import { formatDateTime } from '../utils/format';
import type { ChatMessage, AnalyticsResponse } from '../types';

interface AIChatBotProps {
  fileId: string | null;
  data: AnalyticsResponse;
  onMessagesChange?: (messages: ChatMessage[]) => void;
}

const CHAT_STORAGE_KEY = 'chat_history_session';


const loadChatHistory = (fileId: string | null): ChatMessage[] => {
  if (!fileId) return getDefaultMessages();
  
  try {
    const stored = sessionStorage.getItem(`${CHAT_STORAGE_KEY}_${fileId}`);
    if (stored) {
      const parsed = JSON.parse(stored);
      return parsed.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp),
      }));
    }
  } catch (error) {
    console.error('Error loading chat history:', error);
  }
  return getDefaultMessages();
};

const saveChatHistory = (fileId: string | null, messages: ChatMessage[]) => {
  if (!fileId) return;
  
  try {
    sessionStorage.setItem(
      `${CHAT_STORAGE_KEY}_${fileId}`,
      JSON.stringify(messages)
    );
  } catch (error) {
    console.error('Error saving chat history:', error);
  }
};

const getDefaultMessages = (): ChatMessage[] => [
    {
      id: '1',
      role: 'assistant',
      content: 'Привет! Я AI-ассистент для анализа транзакционных данных. Задайте мне вопросы о данных, прогнозах или рекомендациях.',
      timestamp: new Date(),
    },
];

const AIChatBot = ({ fileId, data: _data, onMessagesChange }: AIChatBotProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>(() => 
    loadChatHistory(fileId)
  );
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  
  useEffect(() => {
    if (fileId) {
      const loadedMessages = loadChatHistory(fileId);
      setMessages(loadedMessages);
    } else {
      setMessages(getDefaultMessages());
    }
  }, [fileId]);

  
  useEffect(() => {
    saveChatHistory(fileId, messages);
    if (onMessagesChange) {
      onMessagesChange(messages);
    }
  }, [messages, fileId, onMessagesChange]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage(input, fileId || undefined, messages);
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Ошибка: ${error.response?.data?.detail || error.message || 'Не удалось получить ответ'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearHistory = () => {
    if (window.confirm('Очистить историю чата?')) {
      const defaultMessages = getDefaultMessages();
      setMessages(defaultMessages);
      if (fileId) {
        sessionStorage.removeItem(`${CHAT_STORAGE_KEY}_${fileId}`);
      }
    }
  };

  const suggestedQuestions = [
    'Какие каналы привлечения наиболее эффективны?',
    'Какой прогноз выручки на следующий месяц?',
    'Какие рекомендации по оптимизации маркетинга?',
    'Сколько аномальных транзакций обнаружено?',
    'Какой уровень ретеншна клиентов?',
  ];

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 120px)' }}>
      {}
      {messages.length > 1 && (
        <Box 
          sx={{ 
            display: 'flex', 
            justifyContent: 'flex-end', 
            px: 2, 
            py: 1.5, 
            borderBottom: 1, 
            borderColor: 'divider',
            background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.02) 0%, rgba(118, 75, 162, 0.02) 100%)',
          }}
        >
          <Tooltip title="Очистить историю чата">
            <Button
              size="small"
              startIcon={<DeleteIcon />}
              onClick={handleClearHistory}
              sx={{ 
                textTransform: 'none',
                color: 'error.main',
                '&:hover': {
                  bgcolor: 'error.light',
                  color: 'white',
                },
              }}
            >
              Очистить
            </Button>
          </Tooltip>
        </Box>
      )}

      {}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          p: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
          '&::-webkit-scrollbar': {
            width: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: 'transparent',
          },
          '&::-webkit-scrollbar-thumb': {
            background: 'rgba(0,0,0,0.2)',
            borderRadius: '4px',
            '&:hover': {
              background: 'rgba(0,0,0,0.3)',
            },
          },
        }}
      >
        {messages.map((message) => (
          <Box
            key={message.id}
            sx={{
              display: 'flex',
              gap: 1,
              justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
            }}
          >
            {message.role === 'assistant' && (
              <Avatar 
                sx={{ 
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  width: 40, 
                  height: 40,
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                }}
              >
                <BotIcon fontSize="small" />
              </Avatar>
            )}
            <Paper
              sx={{
                p: 2.5,
                maxWidth: '75%',
                ...(message.role === 'user' 
                  ? {
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      color: 'white',
                    }
                  : {
                      bgcolor: 'background.paper',
                      color: 'text.primary',
                      border: '1px solid',
                      borderColor: 'divider',
                    }
                ),
                boxShadow: message.role === 'assistant' 
                  ? '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)' 
                  : '0 2px 4px rgba(102, 126, 234, 0.2)',
                borderRadius: 2,
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: message.role === 'assistant' 
                    ? '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)' 
                    : '0 4px 8px rgba(102, 126, 234, 0.3)',
                },
              }}
            >
              {message.role === 'assistant' ? (
                <Box
                  sx={{
                    '& > *': {
                      mb: 1,
                      '&:last-child': { mb: 0 },
                    },
                    '& h1, & h2, & h3, & h4, & h5, & h6': {
                      mt: 2,
                      mb: 1,
                      fontWeight: 600,
                      color: 'text.primary',
                      '&:first-of-type': { mt: 0 },
                    },
                    '& h1': { 
                      fontSize: '1.5rem', 
                      borderBottom: '2px solid', 
                      borderColor: 'divider', 
                      pb: 0.5,
                      color: 'primary.main',
                      fontWeight: 700,
                    },
                    '& h2': { 
                      fontSize: '1.25rem', 
                      borderBottom: '1px solid', 
                      borderColor: 'divider', 
                      pb: 0.5,
                      color: 'text.primary',
                      fontWeight: 600,
                    },
                    '& h3': { 
                      fontSize: '1.1rem',
                      color: 'text.primary',
                      fontWeight: 600,
                    },
                    '& h4': { 
                      fontSize: '1rem',
                      fontWeight: 600,
                    },
                    '& p': {
                      mb: 1.5,
                      lineHeight: 1.6,
                      '&:last-child': { mb: 0 },
                    },
                    '& ul, & ol': {
                      pl: 2.5,
                      mb: 1.5,
                      '& li': {
                        mb: 0.75,
                        lineHeight: 1.7,
                        '&::marker': {
                          color: 'primary.main',
                        },
                        '& p': {
                          mb: 0.5,
                          '&:last-child': { mb: 0 },
                        },
                      },
                    },
                    '& strong': {
                      fontWeight: 600,
                      color: 'text.primary',
                    },
                    '& em': {
                      fontStyle: 'italic',
                    },
                    '& code': {
                      bgcolor: 'action.hover',
                      px: 0.5,
                      py: 0.25,
                      borderRadius: 0.5,
                      fontSize: '0.875em',
                      fontFamily: 'monospace',
                    },
                    '& pre': {
                      bgcolor: 'action.hover',
                      p: 1.5,
                      borderRadius: 1,
                      overflow: 'auto',
                      '& code': {
                        bgcolor: 'transparent',
                        p: 0,
                      },
                    },
                    '& blockquote': {
                      borderLeft: '3px solid',
                      borderColor: 'primary.main',
                      pl: 2,
                      ml: 0,
                      fontStyle: 'italic',
                      color: 'text.secondary',
                    },
                    '& hr': {
                      border: 'none',
                      borderTop: '1px solid',
                      borderColor: 'divider',
                      my: 2,
                    },
                    '& table': {
                      width: '100%',
                      borderCollapse: 'collapse',
                      mb: 2,
                      fontSize: '0.9rem',
                      '& th, & td': {
                        border: '1px solid',
                        borderColor: 'divider',
                        px: 1.5,
                        py: 0.75,
                        textAlign: 'left',
                      },
                      '& th': {
                        bgcolor: 'action.hover',
                        fontWeight: 600,
                        color: 'text.primary',
                      },
                      '& tr:nth-of-type(even)': {
                        bgcolor: 'action.hover',
                      },
                    },
                    '& a': {
                      color: 'primary.main',
                      textDecoration: 'none',
                      '&:hover': {
                        textDecoration: 'underline',
                      },
                    },
                  }}
                >
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {message.content}
                  </ReactMarkdown>
                </Box>
              ) : (
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                  {message.content}
                </Typography>
              )}
              <Typography
                variant="caption"
                sx={{
                  display: 'block',
                  mt: 1.5,
                  opacity: 0.7,
                  fontSize: '0.7rem',
                }}
              >
                {formatDateTime(message.timestamp)}
              </Typography>
            </Paper>
            {message.role === 'user' && (
              <Avatar 
                sx={{ 
                  background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
                  width: 40, 
                  height: 40,
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                }}
              >
                <PersonIcon fontSize="small" />
              </Avatar>
            )}
          </Box>
        ))}
        {isLoading && (
          <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-start' }}>
            <Avatar 
              sx={{ 
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                width: 40, 
                height: 40,
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              }}
            >
              <BotIcon fontSize="small" />
            </Avatar>
            <Paper 
              sx={{ 
                p: 2,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 2,
              }}
            >
              <CircularProgress size={20} sx={{ color: 'primary.main' }} />
            </Paper>
          </Box>
        )}
        <div ref={messagesEndRef} />
      </Box>

      {}
      {messages.length === 1 && (
        <Box 
          sx={{ 
            p: 2, 
            borderTop: 1, 
            borderColor: 'divider',
            background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.02) 0%, rgba(118, 75, 162, 0.02) 100%)',
          }}
        >
          <Typography 
            variant="caption" 
            color="text.secondary" 
            sx={{ 
              mb: 1.5, 
              display: 'block',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
            }}
          >
            Примеры вопросов:
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {suggestedQuestions.map((question, index) => (
              <Paper
                key={index}
                sx={{
                  p: 1.5,
                  bgcolor: 'background.paper',
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 1.5,
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  '&:hover': { 
                    bgcolor: 'primary.main',
                    color: 'white',
                    transform: 'translateX(4px)',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  },
                }}
                onClick={() => setInput(question)}
              >
                <Typography variant="body2" sx={{ fontSize: '0.875rem' }}>
                {question}
              </Typography>
              </Paper>
            ))}
          </Box>
        </Box>
      )}

      {}
      <Box 
        sx={{ 
          p: 2, 
          borderTop: 1, 
          borderColor: 'divider',
          background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.02) 0%, rgba(118, 75, 162, 0.02) 100%)',
        }}
      >
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            size="small"
            placeholder="Задайте вопрос о данных..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            multiline
            maxRows={3}
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: 'background.paper',
                '&:hover': {
                  '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'primary.main',
                  },
                },
              },
            }}
          />
          <IconButton
            color="primary"
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            sx={{ 
              alignSelf: 'flex-end',
              bgcolor: input.trim() && !isLoading ? 'primary.main' : 'action.disabledBackground',
              color: input.trim() && !isLoading ? 'white' : 'action.disabled',
              '&:hover': {
                bgcolor: input.trim() && !isLoading ? 'primary.dark' : 'action.disabledBackground',
                transform: 'scale(1.05)',
              },
              transition: 'all 0.3s ease',
            }}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Box>
    </Box>
  );
};

export default AIChatBot;
