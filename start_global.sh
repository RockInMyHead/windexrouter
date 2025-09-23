#!/bin/bash

# WindexRouter - Скрипт запуска с глобальным доступом
# Использование: ./start_global.sh

echo "🎯 Запуск WindexRouter с глобальным доступом..."
echo "=============================================="

# Проверка ngrok
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok не установлен!"
    echo "📥 Установите ngrok: https://ngrok.com/download"
    exit 1
fi

# Проверка Python зависимостей
if [ ! -f "requirements.txt" ]; then
    echo "❌ Файл requirements.txt не найден!"
    exit 1
fi

echo "📦 Проверка зависимостей..."
pip install -q -r requirements.txt

echo "🚀 Запуск сервисов..."

# Запуск FastAPI
echo "  🔧 Запуск FastAPI..."
python -m uvicorn main:app --host 0.0.0.0 --port 1101 --reload &
FASTAPI_PID=$!

# Запуск Streamlit
echo "  🌐 Запуск Streamlit..."
sleep 2
python -m streamlit run streamlit_app.py --server.port 1102 --server.address 0.0.0.0 &
STREAMLIT_PID=$!

# Запуск ngrok туннелей
echo "  🌍 Создание туннелей ngrok..."
sleep 3

# Туннель для Streamlit
ngrok http 1102 --log=stdout &
NGROK_STREAMLIT_PID=$!

# Туннель для FastAPI
sleep 2
ngrok http 1101 --log=stdout &
NGROK_FASTAPI_PID=$!

# Ждем запуска туннелей
sleep 5

echo ""
echo "=============================================="
echo "🌍 ГЛОБАЛЬНЫЙ ДОСТУП К WINDEXROUTER"
echo "=============================================="

# Получение информации о туннелях
echo ""
echo "📡 Получение информации о туннелях..."

# Ждем немного для инициализации ngrok
sleep 3

# Получаем информацию о туннелях
TUNNELS=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null || echo '{"tunnels":[]}')

if [ "$TUNNELS" != '{"tunnels":[]}' ]; then
    echo ""
    echo "🔗 Доступ к приложению:"
    
    # Извлекаем URL для Streamlit
    STREAMLIT_URL=$(echo "$TUNNELS" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for tunnel in data['tunnels']:
        if tunnel['config']['addr'] == 'http://localhost:1102':
            print(tunnel['public_url'])
            break
except:
    pass
" 2>/dev/null)
    
    # Извлекаем URL для FastAPI
    FASTAPI_URL=$(echo "$TUNNELS" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for tunnel in data['tunnels']:
        if tunnel['config']['addr'] == 'http://localhost:1101':
            print(tunnel['public_url'])
            break
except:
    pass
" 2>/dev/null)
    
    if [ ! -z "$STREAMLIT_URL" ]; then
        echo "  📱 Streamlit интерфейс: $STREAMLIT_URL"
    fi
    
    if [ ! -z "$FASTAPI_URL" ]; then
        echo "  🔧 FastAPI сервер: $FASTAPI_URL"
        echo "  📚 API документация: $FASTAPI_URL/docs"
    fi
else
    echo "❌ Туннели ngrok не найдены"
fi

echo ""
echo "🏠 Локальный доступ:"
echo "  📱 Streamlit: http://localhost:1102"
echo "  🔧 FastAPI: http://localhost:1101"
echo "  📚 API docs: http://localhost:1101/docs"

echo ""
echo "❌ Для остановки нажмите Ctrl+C"
echo "=============================================="

# Функция очистки при выходе
cleanup() {
    echo ""
    echo "🛑 Остановка всех сервисов..."
    kill $FASTAPI_PID 2>/dev/null || true
    kill $STREAMLIT_PID 2>/dev/null || true
    kill $NGROK_STREAMLIT_PID 2>/dev/null || true
    kill $NGROK_FASTAPI_PID 2>/dev/null || true
    
    # Дополнительная очистка процессов
    pkill -f "uvicorn.*main:app" 2>/dev/null || true
    pkill -f "streamlit.*streamlit_app.py" 2>/dev/null || true
    pkill -f "ngrok.*1101" 2>/dev/null || true
    pkill -f "ngrok.*1102" 2>/dev/null || true
    
    echo "✅ Все сервисы остановлены"
    exit 0
}

# Обработка сигналов
trap cleanup SIGINT SIGTERM

# Ожидание
wait

