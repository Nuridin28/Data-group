# DeepSeek API Integration

## Настройка для DeepSeek

Проект был адаптирован для работы с DeepSeek API вместо OpenAI.

### Конфигурация в `.env`

```env
# API Configuration - DeepSeek
API_KEY=sk-b78cada5a61c42188e095daf0ce76c5f
API_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat

# Embeddings (DeepSeek не предоставляет embeddings API)
# Используется OpenAI для embeddings
EMBEDDING_MODEL=text-embedding-3-small
```

### Важные замечания

1. **LLM (Chat)**: Использует DeepSeek API
   - Модель: `deepseek-chat` или `deepseek-coder`
   - Base URL: `https://api.deepseek.com`
   - Использует ваш DeepSeek API ключ

2. **Embeddings**: Использует OpenAI API
   - DeepSeek не предоставляет embeddings API
   - Используется OpenAI `text-embedding-3-small`
   - Если ваш DeepSeek ключ не работает с OpenAI embeddings, 
     установите отдельный `OPENAI_API_KEY` для embeddings

### Переменные окружения

- `API_KEY` - основной API ключ (DeepSeek)
- `API_BASE_URL` - базовый URL API (для DeepSeek: https://api.deepseek.com)
- `LLM_MODEL` - модель для LLM (deepseek-chat)
- `EMBEDDING_MODEL` - модель для embeddings (OpenAI)
- `OPENAI_API_KEY` - опционально, для embeddings если нужен отдельный ключ

### Модели DeepSeek

- `deepseek-chat` - основная модель для чата
- `deepseek-coder` - специализированная модель для кода

### Переключение обратно на OpenAI

Чтобы использовать OpenAI вместо DeepSeek:

```env
API_KEY=sk-your-openai-key
API_BASE_URL=  # оставить пустым или https://api.openai.com/v1
LLM_MODEL=gpt-4-turbo-preview
```

Или просто удалите `API_BASE_URL` и используйте `OPENAI_API_KEY`.

