# Quick Start Guide

## Быстрый старт

### 1. Установка зависимостей

```bash
npm install
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
VITE_API_URL=http://localhost:8000
```

Или используйте `.env.example` как шаблон.

### 3. Запуск бэкенда

Убедитесь, что ваш бэкенд API запущен на `http://localhost:8000` (или другом порту, указанном в `.env`).

Бэкенд должен предоставлять следующие endpoints:
- `POST /api/upload` - загрузка CSV
- `GET /api/analytics` - получение аналитики
- `GET /api/forecasts` - прогнозы
- `GET /api/anomalies` - аномалии
- `GET /api/recommendations` - рекомендации
- `POST /api/chat` - AI чат-бот

Подробнее см. `API_INTEGRATION.md`

### 4. Запуск фронтенда

```bash
npm run dev
```

Приложение будет доступно по адресу `http://localhost:3000`

### 5. Использование

1. Откройте браузер и перейдите на `http://localhost:3000`
2. Загрузите CSV файл с транзакционными данными
3. Дождитесь обработки данных
4. Изучите аналитический дашборд
5. Используйте AI чат-бот для вопросов о данных

## Сборка для продакшена

```bash
npm run build
```

Собранные файлы будут в папке `dist/`

## Структура проекта

```
kbtu/
├── src/
│   ├── components/          # React компоненты
│   │   ├── charts/         # Компоненты графиков
│   │   ├── AIChatBot.tsx   # AI чат-бот
│   │   ├── Dashboard.tsx   # Главный дашборд
│   │   └── FileUpload.tsx  # Загрузка файлов
│   ├── services/           # API сервисы
│   ├── types/              # TypeScript типы
│   ├── utils/              # Утилиты
│   └── App.tsx             # Главный компонент
├── public/                 # Статические файлы
├── package.json
└── vite.config.ts
```

## Технологии

- **React 18** + **TypeScript**
- **Vite** - быстрый сборщик
- **Material UI** - UI компоненты
- **Recharts** - интерактивные графики
- **Axios** - HTTP клиент
