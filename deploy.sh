#!/bin/bash

# WindexRouter - Скрипт развертывания на сервере
# Использование: ./deploy.sh

set -e  # Останавливаемся при первой ошибке

# Конфигурация
SERVER_HOST="77.37.146.116"
SERVER_PORT="204"
SERVER_USER="rvs"
PROJECT_NAME="WindexRouter"
REMOTE_PATH="/home/rvs/${PROJECT_NAME}"

echo "🚀 Начинаем развертывание WindexRouter на сервер..."

# 1. Создание архива проекта
echo "📦 Создание архива проекта..."
cd ..
tar -czf ${PROJECT_NAME}.tar.gz \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='*.sqlite3' \
    --exclude='.git' \
    --exclude='api_keys.db' \
    --exclude='*.log' \
    --exclude='${PROJECT_NAME}.tar.gz' \
    ${PROJECT_NAME}
cd ${PROJECT_NAME}

echo "✅ Архив создан: ${PROJECT_NAME}.tar.gz"

# 2. Копирование на сервер
echo "📤 Копирование на сервер..."
scp -P ${SERVER_PORT} ../${PROJECT_NAME}.tar.gz ${SERVER_USER}@${SERVER_HOST}:/tmp/

# 3. Развертывание на сервере
echo "🔧 Развертывание на сервере..."
ssh -p ${SERVER_PORT} ${SERVER_USER}@${SERVER_HOST} << EOF
    set -e

    echo "🧹 Очистка предыдущей версии..."
    rm -rf ${REMOTE_PATH}
    mkdir -p ${REMOTE_PATH}

    echo "📦 Распаковка проекта..."
    tar -xzf /tmp/${PROJECT_NAME}.tar.gz -C ${REMOTE_PATH}
    cd ${REMOTE_PATH}

    echo "🐍 Установка Python зависимостей..."
    python3 -m pip install --user -r requirements.txt

    echo "📊 Инициализация базы данных..."
    python3 main.py &
    sleep 3
    kill %1 2>/dev/null || true

    echo "✅ Развертывание завершено!"
EOF

# 4. Запуск сервисов
echo "🎯 Запуск сервисов..."
ssh -p ${SERVER_PORT} ${SERVER_USER}@${SERVER_HOST} << EOF
    cd ${REMOTE_PATH}

    echo "🛑 Остановка предыдущих процессов..."
    pkill -f "uvicorn" || true
    pkill -f "streamlit" || true
    sleep 2

    echo "🚀 Запуск FastAPI..."
    nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > fastapi.log 2>&1 &

    echo "🌐 Запуск Streamlit..."
    sleep 3
    nohup python3 -m streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 > streamlit.log 2>&1 &

    echo "✅ Сервисы запущены!"
    echo "📊 FastAPI: http://77.37.146.116:8000"
    echo "🌐 Streamlit: http://77.37.146.116:8501"
    echo "📚 API документация: http://77.37.146.116:8000/docs"
EOF

# 5. Очистка
echo "🧹 Очистка временных файлов..."
rm -f ../${PROJECT_NAME}.tar.gz

echo ""
echo "🎉 Развертывание завершено успешно!"
echo ""
echo "🌐 Доступ к приложению:"
echo "   Streamlit: http://77.37.146.116:8501"
echo "   FastAPI: http://77.37.146.116:8000"
echo "   API docs: http://77.37.146.116:8000/docs"
echo ""
echo "📋 Для просмотра логов на сервере:"
echo "   ssh -p 204 rvs@77.37.146.116 'cd ${REMOTE_PATH} && tail -f *.log'"




