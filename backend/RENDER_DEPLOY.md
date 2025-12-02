# Деплой на Render

## Настройки на Render

### Build Command
Если requirements.txt в корне репозитория:
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

Если requirements.txt в папке backend:
```bash
pip install --upgrade pip && pip install -r backend/requirements.txt
```

### Start Command
```bash
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

Или если корневая директория - backend:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

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

