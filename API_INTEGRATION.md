# API Integration Guide

Данный документ описывает ожидаемые endpoints и форматы данных для интеграции фронтенда с бэкендом.

## Base URL

По умолчанию: `http://localhost:8000`

Можно настроить через переменную окружения `VITE_API_URL` в файле `.env`

## Endpoints

### 1. Загрузка CSV файла

**POST** `/api/upload`

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` - CSV файл с транзакционными данными

**Response:**
```json
{
  "message": "File uploaded successfully",
  "file_id": "unique-file-id"
}
```

### 2. Получение аналитики

**GET** `/api/analytics`

**Query Parameters:**
- `file_id` (optional) - ID загруженного файла

**Response:**
```json
{
  "revenue_trend": [
    {
      "date": "2024-01-01",
      "revenue": 150000,
      "transactions_count": 120
    }
  ],
  "revenue_by_channel": [
    {
      "channel": "Kaspi QR",
      "revenue": 500000,
      "transactions": 400,
      "customers": 350,
      "roi": 25.5,
      "conversion_rate": 12.3
    }
  ],
  "cohort_analysis": [
    {
      "cohort": "2024-01",
      "period": 0,
      "retention": 100,
      "customers": 1000
    }
  ],
  "roi_metrics": [
    {
      "source": "Kaspi QR",
      "investment": 100000,
      "revenue": 500000,
      "roi": 400,
      "profit": 400000
    }
  ],
  "summary": {
    "total_revenue": 5000000,
    "total_transactions": 10000,
    "active_customers": 5000,
    "avg_transaction_value": 500,
    "cancellation_rate": 5.2
  }
}
```

### 3. Получение прогнозов

**GET** `/api/forecasts`

**Query Parameters:**
- `file_id` (optional) - ID загруженного файла
- `days` (optional, default: 30) - Количество дней для прогноза

**Response:**
```json
{
  "revenue_forecast": [
    {
      "date": "2024-02-01",
      "predicted": 160000,
      "lower_bound": 140000,
      "upper_bound": 180000,
      "actual": null
    }
  ],
  "cancellation_probability": 5.2
}
```

### 4. Получение аномалий

**GET** `/api/anomalies`

**Query Parameters:**
- `file_id` (optional) - ID загруженного файла

**Response:**
```json
[
  {
    "transaction_id": "txn_123",
    "date": "2024-01-15T10:30:00",
    "amount": 50000,
    "anomaly_score": 0.85,
    "reason": "Необычно высокая сумма транзакции",
    "risk_level": "high"
  }
]
```

### 5. Получение рекомендаций

**GET** `/api/recommendations`

**Query Parameters:**
- `file_id` (optional) - ID загруженного файла

**Response:**
```json
[
  {
    "id": "rec_1",
    "type": "discount",
    "title": "Персональная скидка для сегмента VIP",
    "description": "Предложить скидку 15% клиентам с высоким LTV",
    "segment": "VIP",
    "expected_impact": "Увеличение конверсии на 20%",
    "priority": "high"
  }
]
```

### 6. AI Чат-бот

**POST** `/api/chat`

**Request Body:**
```json
{
  "message": "Какие каналы привлечения наиболее эффективны?",
  "file_id": "unique-file-id",
  "history": [
    {
      "role": "user",
      "content": "Привет"
    },
    {
      "role": "assistant",
      "content": "Привет! Чем могу помочь?"
    }
  ]
}
```

**Response:**
```json
{
  "response": "Наиболее эффективными каналами привлечения являются Kaspi QR с ROI 400% и marketplace с конверсией 12.3%."
}
```

## Формат CSV файла

Ожидаемые колонки в CSV файле:

- `id` или `transaction_id` - уникальный ID транзакции
- `date` или `timestamp` - дата транзакции
- `amount` - сумма транзакции
- `customer_id` - ID клиента
- `channel` - канал привлечения (Kaspi QR, marketplace, соцсети и т.д.)
- `status` - статус транзакции (completed, cancelled, pending)
- `product_category` (optional) - категория продукта
- `region` (optional) - регион

Пример:
```csv
id,date,amount,customer_id,channel,status
txn_1,2024-01-01,5000,cust_1,Kaspi QR,completed
txn_2,2024-01-01,3000,cust_2,marketplace,completed
```

## Обработка ошибок

Все endpoints должны возвращать ошибки в следующем формате:

```json
{
  "detail": "Описание ошибки"
}
```

Статус коды:
- `200` - Успешный запрос
- `400` - Ошибка валидации
- `404` - Ресурс не найден
- `500` - Внутренняя ошибка сервера
