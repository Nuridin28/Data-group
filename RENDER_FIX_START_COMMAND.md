# КАК ИСПРАВИТЬ START COMMAND НА RENDER

## Проблема
Render использует дефолтный Start Command: `gunicorn your_application.wsgi`
Это для Django/Flask, но у вас FastAPI приложение!

## Решение: Изменить Start Command вручную

### Шаг 1: Откройте Render Dashboard
1. Зайдите на https://dashboard.render.com
2. Найдите ваш сервис (например, "data-group" или "kbtu-backend")
3. Нажмите на него

### Шаг 2: Откройте настройки
1. В левом меню нажмите **"Settings"** (Настройки)
2. Прокрутите вниз до раздела **"Build & Deploy"**

### Шаг 3: Измените Start Command
1. Найдите поле **"Start Command"**
2. УДАЛИТЕ текущее значение: `gunicorn your_application.wsgi`
3. ВСТАВЬТЕ новое значение:
   ```
   cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

### Шаг 4: Проверьте Build Command
Убедитесь, что **Build Command** установлен:
```
pip install --upgrade pip && pip install -r requirements.txt
```

### Шаг 5: Сохраните и перезапустите
1. Нажмите **"Save Changes"** (Сохранить изменения)
2. Render автоматически начнет новый деплой
3. Дождитесь завершения деплоя

## Альтернативный Start Command (если первый не работает)

Если `cd backend` не работает, попробуйте:

**Вариант 1:** Без cd (если Root Directory = backend)
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Вариант 2:** С полным путем
```
cd /opt/render/project/src/backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Вариант 3:** Через Python модуль
```
cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Проверка после исправления

После успешного деплоя проверьте:
- `https://data-group.onrender.com/docs` - Swagger документация
- `https://data-group.onrender.com/health` - Проверка здоровья

## Скриншот того, что должно быть:

```
Build Command:
pip install --upgrade pip && pip install -r requirements.txt

Start Command:
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Если все еще не работает

1. Проверьте логи деплоя в Render Dashboard
2. Убедитесь, что `uvicorn` установлен (он должен быть в requirements.txt как `uvicorn[standard]`)
3. Проверьте, что путь `backend/main.py` существует
4. Убедитесь, что все переменные окружения установлены

