#!/bin/bash
echo "🚀 Запуск KBTU Transaction Analytics"
echo ""

# Проверяем бэкенд
echo "Проверяю бэкенд..."
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Бэкенд уже запущен на http://localhost:8000"
else
    echo "⚠️  Бэкенд не запущен"
    echo "   Запустите в отдельном терминале: cd backend && python run.py"
fi

echo ""
echo "Запускаю фронтенд..."
npm run dev
