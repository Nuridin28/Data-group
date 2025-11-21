# 📤 Эндпоинт загрузки файлов

## ✅ Добавлен эндпоинт `/api/upload`

### POST `/api/upload`

Загрузка CSV файла с транзакционными данными.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` - CSV файл

**Response:**
```json
{
  "message": "Файл успешно загружен и обработан",
  "file_id": "uuid-string",
  "rows": 1000,
  "columns": ["date", "amount", "channel", ...],
  "filename": "transactions.csv"
}
```

### GET `/api/upload/{file_id}/info`

Получить информацию о загруженном файле.

**Response:**
```json
{
  "file_id": "uuid-string",
  "filename": "transactions.csv",
  "rows": 1000,
  "columns": ["date", "amount", ...],
  "uploaded_at": "2024-01-01T00:00:00",
  "file_path": "data/uploads/uuid.csv"
}
```

## 📁 Хранение файлов

- Загруженные файлы сохраняются в `data/uploads/`
- Каждый файл получает уникальный UUID
- Метаданные хранятся в `data/uploads/uploads_metadata.json`

## 🔧 Интеграция

Роутер автоматически подключен в `main.py`:
```python
from routers import upload
app.include_router(upload.router)
```

## ✅ Проверка

После запуска бэкенда эндпоинт будет доступен:
- Swagger UI: http://localhost:8000/docs
- Прямой вызов: `POST http://localhost:8000/api/upload`
