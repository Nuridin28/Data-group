# ИСПРАВЛЕНИЕ: Data file not found

## Проблема
```
FileNotFoundError: Data file not found: z
```

Переменная окружения `DATA_FILE` на Render установлена неправильно (значение "z").

## Решение: Установить правильную переменную окружения

### Шаг 1: Откройте Render Dashboard
1. Зайдите на https://dashboard.render.com
2. Найдите ваш сервис
3. Нажмите на него

### Шаг 2: Откройте Environment Variables
1. В левом меню нажмите **"Environment"** (Переменные окружения)
2. Или перейдите в **Settings** → **Environment Variables**

### Шаг 3: Найдите и исправьте DATA_FILE
1. Найдите переменную **`DATA_FILE`** в списке
2. Если её нет - нажмите **"Add Environment Variable"**
3. Установите:
   - **Key:** `DATA_FILE`
   - **Value:** `data/track_1_digital_economy_kz.csv`
   
   **ВАЖНО:** Путь `data/track_1_digital_economy_kz.csv` (без `backend/` в начале), потому что Start Command делает `cd backend`, и рабочая директория уже будет `backend/`

### Шаг 4: Проверьте другие переменные
Убедитесь, что установлены все необходимые переменные:

- **API_KEY** - ваш DeepSeek API ключ (обязательно!)
- **API_BASE_URL** = `https://api.deepseek.com`
- **LLM_MODEL** = `deepseek-chat`
- **EMBEDDING_MODEL** = `text-embedding-3-small`
- **OPENAI_API_KEY** - если используете (опционально)
- **CHROMA_PERSIST_DIR** = `./vectorstore`
- **DATA_FILE** = `data/track_1_digital_economy_kz.csv` ⬅️ ЭТО ГЛАВНОЕ!
- **RAG_TOP_K** = `5`
- **TEMPERATURE** = `0.0`

### Шаг 5: Сохраните и перезапустите
1. Нажмите **"Save Changes"**
2. Render автоматически перезапустит сервис
3. Дождитесь завершения деплоя

## Альтернативные пути (если первый не работает)

Если `data/track_1_digital_economy_kz.csv` не работает, попробуйте:

**Вариант 1:** Полный путь от корня проекта
```
backend/data/track_1_digital_economy_kz.csv
```

**Вариант 2:** Абсолютный путь (если знаете структуру Render)
```
/opt/render/project/src/backend/data/track_1_digital_economy_kz.csv
```

## Проверка после исправления

После успешного деплоя проверьте логи - должно быть:
```
[OK] Data loaded: 30000 transactions
```

И проверьте эндпоинты:
- `https://data-group.onrender.com/docs`
- `https://data-group.onrender.com/health`

