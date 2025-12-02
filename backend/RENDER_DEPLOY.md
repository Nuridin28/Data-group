# Деплой на Render

## Автоматическая настройка через render.yaml

В корне репозитория создан файл `render.yaml` с настройками деплоя. Render автоматически использует его при деплое.

## Ручная настройка на Render

Если вы не используете render.yaml, настройте вручную:

### Build Command
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

**ВАЖНО:** Убедитесь, что `requirements.txt` находится в корне репозитория, или измените путь в команде.

### Start Command
```bash
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

**КРИТИЧЕСКИ ВАЖНО:** 
- НЕ используйте `gunicorn` - это для Django/Flask
- Используйте `uvicorn` для FastAPI
- Убедитесь, что путь `cd backend` правильный относительно корня репозитория

### Environment Variables
Установите следующие переменные окружения в настройках Render:

```
API_KEY=sk-your-deepseek-api-key
API_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
EMBEDDING_MODEL=text-embedding-3-small
OPENAI_API_KEY=sk-your-openai-key (опционально, для embeddings)
CHROMA_PERSIST_DIR=./vectorstore
DATA_FILE=data/track_1_digital_economy_kz.csv
RAG_TOP_K=5
TEMPERATURE=0.0
```

### Python Version
Используется Python 3.13.4 (указано в runtime.txt в корне репозитория)

### Важно
- Убедитесь, что файл `data/track_1_digital_economy_kz.csv` находится в репозитории или загружен на сервер
- Для первого запуска может потребоваться время на создание vectorstore
- Если используете Python 3.13, обновите runtime.txt на `python-3.13.0`

