# 🔑 WindexRouter

**Система управления API ключами с доступом к DeepSeek AI**

WindexRouter - это веб-приложение для генерации, хранения и управления API ключами с возможностью использования DeepSeek AI. Проект состоит из FastAPI бэкенда и Streamlit веб-интерфейса, работает с SQLite базой данных.

## ✨ Возможности

- 🔑 **Генерация уникальных API ключей**
- 📅 **Настройка срока действия ключей**
- 🔄 **Активация/деактивация ключей**
- 🗑️ **Удаление ненужных ключей**
- 📊 **Просмотр всех созданных ключей**
- 🌐 **Веб-интерфейс на Streamlit**
- 📚 **REST API с документацией**
- 🤖 **Доступ к DeepSeek AI через ваши API ключи**

## 🚀 Быстрый запуск

### Локальная разработка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск обоих сервисов
python run.py
```

После запуска откройте:
- **Streamlit интерфейс**: http://localhost:1102
- **FastAPI сервер**: http://localhost:1101
- **API документация**: http://localhost:1101/docs

### 🌍 Глобальный доступ через ngrok

Для доступа к приложению из любой точки мира:

```bash
# Автоматический запуск с ngrok туннелями
./start_global.sh

# Или через Python скрипт
python start_global.py
```

После запуска вы получите публичные URL для доступа к приложению из интернета:
- **Streamlit интерфейс**: `https://xxxxx.ngrok-free.app`
- **FastAPI сервер**: `https://xxxxx.ngrok-free.app`
- **API документация**: `https://xxxxx.ngrok-free.app/docs`

> **Примечание**: Для использования ngrok необходимо:
> 1. Установить ngrok: https://ngrok.com/download
> 2. Зарегистрироваться и получить токен авторизации
> 3. Выполнить: `ngrok config add-authtoken YOUR_TOKEN`

### Развертывание на сервере

```bash
# Развертывание на сервере
./deploy.sh
```

После развертывания приложение будет доступно по адресам:
- **Streamlit интерфейс**: http://77.37.146.116:8501
- **FastAPI сервер**: http://77.37.146.116:8000
- **API документация**: http://77.37.146.116:8000/docs

## 📋 API Endpoints

### Создание API ключа
```http
POST /api/keys
Content-Type: application/json

{
  "name": "DeepSeek API Key",
  "expires_in_days": 30
}
```

### Получение всех ключей
```http
GET /api/keys
```

### Удаление ключа
```http
DELETE /api/keys/{key_id}
```

### Активация/деактивация ключа
```http
PUT /api/keys/{key_id}/toggle
```

## 🤖 DeepSeek AI Integration

### Использование DeepSeek через WindexRouter

```python
import requests

# Ваш API ключ из WindexRouter
api_key = "wr_your_api_key_here"

# Запрос к DeepSeek через WindexRouter
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "user", "content": "Привет! Как дела?"}
    ],
    "max_tokens": 100
}

response = requests.post(
    "http://localhost:1101/api/deepseek/chat/completions",
    json=data,
    headers=headers
)

if response.status_code == 200:
    result = response.json()
    print(result["choices"][0]["message"]["content"])
else:
    print(f"Ошибка: {response.text}")
```

### Доступные модели DeepSeek

- **deepseek-chat** - Универсальная модель для чата
- **deepseek-coder** - Специализированная модель для программирования

### Получение списка моделей

```python
response = requests.get(
    "http://localhost:1101/api/deepseek/models",
    headers={"Authorization": f"Bearer {api_key}"}
)
```

### Настройка DeepSeek API

Для работы с DeepSeek AI необходимо:

1. Получить API ключ от DeepSeek: https://platform.deepseek.com/
2. Установить переменную окружения:
```bash
export DEEPSEEK_API_KEY="sk-your-deepseek-api-key"
```

3. Перезапустить сервер

## 🛠️ Структура проекта

```
WindexRouter/
├── main.py                 # FastAPI приложение
├── streamlit_app.py        # Streamlit веб-интерфейс
├── run.py                  # Скрипт запуска для разработки
├── deploy.sh              # Скрипт развертывания
├── requirements.txt       # Зависимости Python
├── .gitignore            # Исключаемые файлы
├── api_keys.db           # SQLite база данных (создается автоматически)
└── README.md             # Документация
```

## 🐍 Зависимости

- **FastAPI** - веб-фреймворк для API
- **Uvicorn** - ASGI сервер
- **Streamlit** - веб-фреймворк для интерфейса
- **SQLite3** - встроенная база данных
- **httpx** - HTTP клиент для проксирования запросов к DeepSeek

## 📊 Использование API ключей

В ваших проектах используйте созданные ключи следующим образом:

```python
import requests

# Использование API ключа
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = requests.get("https://your-api.com/endpoint", headers=headers)
```

## 🔧 Настройка сервера

### Требования к серверу

- Python 3.8+
- SSH доступ
- Открытые порты 1101 (FastAPI) и 1102 (Streamlit)
- Переменная окружения DEEPSEEK_API_KEY для работы с DeepSeek AI

### Переменные окружения

Можно настроить через файл `.env`:

```bash
# Порт FastAPI
FASTAPI_PORT=1101

# Порт Streamlit
STREAMLIT_PORT=1102

# Хост (по умолчанию 0.0.0.0 для всех интерфейсов)
HOST=0.0.0.0

# DeepSeek API базовый URL (локальный instance)
DEEPSEEK_API_BASE=http://localhost:1103

# (Опционально) внешний DeepSeek ключ
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
```

## 📝 Логи

Логи сохраняются в файлах:
- `fastapi.log` - логи FastAPI сервера
- `streamlit.log` - логи Streamlit приложения

### Просмотр логов на сервере

```bash
ssh -p 204 rvs@77.37.146.116 'cd WindexRouter && tail -f *.log'
```

## 🔒 Безопасность

- API ключи генерируются с использованием UUID
- SQLite база данных хранится локально
- CORS настроен для работы с Streamlit
- Валидация входных данных через Pydantic
- Логирование всех запросов к DeepSeek API
- Валидация ключей при каждом запросе
- Поддержка срока действия ключей

## 🤝 Разработка

### Добавление новых функций

1. API endpoints добавляются в `main.py`
2. Интерфейс обновляется в `streamlit_app.py`
3. Новые зависимости добавляются в `requirements.txt`

### Тестирование

```bash
# Запуск FastAPI сервера
python -m uvicorn main:app --reload

# Запуск Streamlit
streamlit run streamlit_app.py
```

## 📄 Лицензия

Проект предназначен для личного использования.

## 📞 Поддержка

При возникновении проблем проверьте:
1. Логи приложений
2. Доступность портов 1101 и 1102
3. Наличие всех зависимостей
4. Подключение к базе данных
5. Настройку переменной окружения DEEPSEEK_API_KEY
6. Валидность DeepSeek API ключа

---

**Создано с ❤️ для управления API ключами**


