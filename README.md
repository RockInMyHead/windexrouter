# 🔑 WindexRouter

**Система управления API ключами для проектов**

WindexRouter - это веб-приложение для генерации, хранения и управления API ключами. Проект состоит из FastAPI бэкенда и Streamlit веб-интерфейса, работает с SQLite базой данных.

## ✨ Возможности

- 🔑 **Генерация уникальных API ключей**
- 📅 **Настройка срока действия ключей**
- 🔄 **Активация/деактивация ключей**
- 🗑️ **Удаление ненужных ключей**
- 📊 **Просмотр всех созданных ключей**
- 🌐 **Веб-интерфейс на Streamlit**
- 📚 **REST API с документацией**

## 🚀 Быстрый запуск

### Локальная разработка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск обоих сервисов
python run.py
```

После запуска откройте:
- **Streamlit интерфейс**: http://localhost:8501
- **FastAPI сервер**: http://localhost:8000
- **API документация**: http://localhost:8000/docs

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
- Открытые порты 8000 (FastAPI) и 8501 (Streamlit)

### Переменные окружения

Можно настроить через файл `.env`:

```bash
# Порт FastAPI
FASTAPI_PORT=8000

# Порт Streamlit
STREAMLIT_PORT=8501

# Хост (по умолчанию 0.0.0.0 для всех интерфейсов)
HOST=0.0.0.0
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
2. Доступность портов 8000 и 8501
3. Наличие всех зависимостей
4. Подключение к базе данных

---

**Создано с ❤️ для управления API ключами**

