# Проверка билда бэкенда

## Быстрая проверка

**ВАЖНО:** Всегда используйте виртуальное окружение!

Запустите скрипт проверки:
```bash
cd backend
source venv/bin/activate  # Активируйте виртуальное окружение
python check_build.py
```

Или одной командой:
```bash
cd backend && source venv/bin/activate && python check_build.py
```

## Ручная проверка

### 1. Проверка установки зависимостей
```bash
cd backend
pip install -r requirements.txt
```

### 2. Проверка импортов
```bash
python -c "from main import app; print('✅ Приложение импортировано')"
```

### 3. Проверка запуска сервера (тестовый режим)
```bash
python run.py
```

Сервер должен запуститься на http://localhost:8000

### 4. Проверка эндпоинтов
После запуска сервера проверьте:
- http://localhost:8000/docs - Swagger документация
- http://localhost:8000/health - Проверка здоровья сервиса
- http://localhost:8000/ - Главная страница API

## Проверка в режиме Render (чистая установка)

Для проверки в режиме, максимально похожем на Render:

```bash
# Создать чистое виртуальное окружение
python3.13 -m venv test_build
source test_build/bin/activate

# Обновить pip
pip install --upgrade pip

# Установить зависимости
pip install -r requirements.txt

# Проверить импорты
python check_build.py

# Запустить сервер
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Проверка конкретных компонентов

### Проверка data_service
```bash
python -c "from services.data_service import get_data_service; ds = get_data_service(); print(f'Строк: {len(ds.df)}')"
```

### Проверка prediction_service
```bash
python -c "from services.prediction_service import get_prediction_service; ps = get_prediction_service(); print('✅ Prediction service инициализирован')"
```

### Проверка RAG chain
```bash
python -c "from rag.rag_chain import get_rag_chain; chain = get_rag_chain(); print('✅ RAG chain инициализирован')"
```

## Проверка через curl

После запуска сервера:

```bash
# Проверка здоровья
curl http://localhost:8000/health

# Проверка главной страницы
curl http://localhost:8000/

# Проверка аналитики (требует POST с данными)
curl -X POST http://localhost:8000/analytics/revenue \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Типичные проблемы

1. **Ошибка импорта модуля (LangSmithParams и т.д.)**: 
   - **Причина**: Запуск без виртуального окружения или несовместимые версии пакетов
   - **Решение**: Всегда используйте `source venv/bin/activate` перед запуском
   - **Проверка**: Скрипт автоматически предупредит, если виртуальное окружение не активировано

2. **Ошибка DATA_FILE**: Проверьте, что файл существует по пути в .env

3. **Ошибка API_KEY**: Установите переменную окружения или создайте .env файл

4. **Ошибка порта**: Убедитесь, что порт 8000 свободен

5. **Конфликт версий langchain**: 
   - Убедитесь, что все langchain пакеты имеют совместимые версии
   - Используйте точные версии из requirements.txt: `langchain==1.1.0`, `langchain-core==1.1.0`, `langchain-openai==1.1.0`

