# 🔧 Настройка DeepSeek API

## ✅ Обновлено для работы с DeepSeek

Ваше приложение использует **DeepSeek** для LLM (чат и генерация SQL), но **embeddings требуют OpenAI API**.

## 📝 Конфигурация .env

```env
# DeepSeek для LLM (чат, SQL генерация, рекомендации)
API_KEY=sk-b78cada5a61c42188e095daf0ce76c5f
API_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat

# OpenAI для embeddings (vectorstore) - ОПЦИОНАЛЬНО
# Если не указан, vectorstore не будет работать, но есть CSV fallback
OPENAI_API_KEY=your-openai-key-here
EMBEDDING_MODEL=text-embedding-3-small
```

## 🔑 Важно понимать

### DeepSeek API Key используется для:
- ✅ LLM чат-бот (`/ask` endpoint)
- ✅ Генерация SQL запросов
- ✅ AI рекомендации и insights
- ✅ Анализ данных через RAG

### OpenAI API Key нужен ТОЛЬКО для:
- ⚠️ Embeddings (создание vectorstore)
- ⚠️ Semantic search в данных

**Без OpenAI ключа:**
- ✅ Приложение работает нормально
- ✅ Используется CSV fallback вместо vectorstore
- ✅ Все функции доступны
- ⚠️ Только semantic search будет менее точным

## 📊 Сообщения в логах

Если видите:
```
Note: Embeddings service unavailable (needs OpenAI API key for vectorstore). Using CSV fallback.
```

Это **НОРМАЛЬНО** - означает что:
- DeepSeek работает для LLM ✅
- Vectorstore недоступен (нужен OpenAI для embeddings)
- Используется CSV fallback ✅
- Приложение работает полностью ✅

## 🚀 Запуск

Приложение работает с DeepSeek ключом БЕЗ OpenAI:
```bash
cd backend
python run.py
```

Все функции доступны, только semantic search будет через CSV вместо vectorstore.
