# Инструкция по деплою на Render

## Проблема: "gunicorn: command not found"

Render пытается использовать `gunicorn` (для Django/Flask), но это FastAPI приложение, которое использует `uvicorn`.

## Решение

### Вариант 1: Использовать render.yaml (рекомендуется)

Файл `render.yaml` уже создан в корне репозитория. При подключении репозитория к Render, он автоматически подхватит настройки.

### Вариант 2: Ручная настройка на Render Dashboard

Если render.yaml не работает, настройте вручную в Dashboard Render:

1. **Build Command:**
   ```
   pip install --upgrade pip && pip install -r requirements.txt
   ```

2. **Start Command (КРИТИЧЕСКИ ВАЖНО!):**
   ```
   cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
   
   **НЕ используйте:**
   - ❌ `gunicorn your_application.wsgi` (это для Django)
   - ❌ `python run.py` (не будет работать с переменной $PORT)
   
   **Используйте:**
   - ✅ `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Root Directory (если нужно):**
   Оставьте пустым или установите в корень репозитория

4. **Environment Variables:**
   Установите все переменные из `backend/env.example`:
   - `API_KEY` - ваш DeepSeek API ключ
   - `API_BASE_URL=https://api.deepseek.com`
   - `LLM_MODEL=deepseek-chat`
   - `EMBEDDING_MODEL=text-embedding-3-small`
   - `OPENAI_API_KEY` - если используете OpenAI для embeddings
   - `CHROMA_PERSIST_DIR=./vectorstore`
   - `DATA_FILE=backend/data/track_1_digital_economy_kz.csv`
   - `RAG_TOP_K=5`
   - `TEMPERATURE=0.0`

## Проверка после деплоя

После успешного деплоя проверьте:
- `https://your-app.onrender.com/docs` - Swagger документация
- `https://your-app.onrender.com/health` - Проверка здоровья сервиса

## Если все еще не работает

1. Проверьте логи в Render Dashboard
2. Убедитесь, что `requirements.txt` находится в корне репозитория
3. Убедитесь, что путь `cd backend` правильный
4. Проверьте, что все переменные окружения установлены

