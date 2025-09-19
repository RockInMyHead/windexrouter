from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import sqlite3
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
import os
import httpx
import json

app = FastAPI(title="WindexRouter API", description="API для генерации и управления API ключами")

# CORS для работы с Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модель для пользователя
class User(BaseModel):
    id: str
    username: str
    email: str
    created_at: str
    is_active: bool = True

# Модель для регистрации
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

# Модель для входа
class UserLogin(BaseModel):
    username: str
    password: str

# Модель для токена
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_at: str

# Модель для API ключа
class APIKey(BaseModel):
    id: str
    name: str
    key: str
    created_at: str
    expires_at: Optional[str] = None
    is_active: bool = True
    user_id: str

# Модель для создания ключа
class CreateKeyRequest(BaseModel):
    name: str
    expires_in_days: Optional[int] = None

# Безопасность
security = HTTPBearer()

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('api_keys.db')
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Таблица токенов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Обновленная таблица API ключей с привязкой к пользователю
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            key TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT,
            is_active INTEGER DEFAULT 1,
            user_id TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Таблица для логирования использования API
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_usage_log (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            api_key_id TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Функции для работы с паролями
def hash_password(password: str) -> str:
    """Хеширование пароля"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}:{pwd_hash.hex()}"

def verify_password(password: str, hashed: str) -> bool:
    """Проверка пароля"""
    try:
        salt, pwd_hash = hashed.split(':')
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return pwd_hash == new_hash.hex()
    except:
        return False

# Функции для работы с токенами
def generate_token() -> str:
    """Генерация токена"""
    return secrets.token_urlsafe(32)

def get_token_expires() -> str:
    """Получение времени истечения токена (24 часа)"""
    return (datetime.now() + timedelta(hours=24)).isoformat()

# Генерация уникального API ключа
def generate_api_key():
    return f"wr_{uuid.uuid4().hex}"

# Получение даты истечения
def get_expires_date(days: int):
    return (datetime.now() + timedelta(days=days)).isoformat()

# Функция для получения текущего пользователя
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Получение текущего пользователя по токену"""
    conn = sqlite3.connect('api_keys.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.id, u.username, u.email, u.created_at, u.is_active
        FROM users u
        JOIN tokens t ON u.id = t.user_id
        WHERE t.token = ? AND t.expires_at > ? AND u.is_active = 1
    ''', (credentials.credentials, datetime.now().isoformat()))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return User(
        id=result[0],
        username=result[1],
        email=result[2],
        created_at=result[3],
        is_active=bool(result[4])
    )

# Функция для валидации API ключа
async def validate_api_key(api_key: str) -> Optional[tuple]:
    """Валидация API ключа и получение пользователя и ID ключа"""
    conn = sqlite3.connect('api_keys.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.id, u.username, u.email, u.created_at, u.is_active, ak.expires_at, ak.id
        FROM users u
        JOIN api_keys ak ON u.id = ak.user_id
        WHERE ak.key = ? AND ak.is_active = 1 AND u.is_active = 1
    ''', (api_key,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return None
    
    # Проверяем срок действия ключа
    if result[5]:  # expires_at
        expires_at = datetime.fromisoformat(result[5])
        if expires_at < datetime.now():
            return None
    
    user = User(
        id=result[0],
        username=result[1],
        email=result[2],
        created_at=result[3],
        is_active=bool(result[4])
    )
    
    return user, result[6]  # Возвращаем пользователя и ID ключа

# DeepSeek API конфигурация
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "http://localhost:1103")
# DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "http://localhost:1103/api/chat/completions")  # Local DeepSeek endpoint
#DEEPSEEK_FORWARD_URL = os.getenv("DEEPSEEK_FORWARD_URL", DEEPSEEK_API_URL)

# Инициализация БД при запуске
init_db()

# Endpoints для аутентификации
@app.post("/api/auth/register", response_model=User)
async def register_user(user_data: UserRegister):
    """Регистрация нового пользователя"""
    conn = sqlite3.connect('api_keys.db')
    cursor = conn.cursor()
    
    # Проверяем, существует ли пользователь
    cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (user_data.username, user_data.email))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Пользователь с таким именем или email уже существует")
    
    # Создаем пользователя
    user_id = str(uuid.uuid4())
    password_hash = hash_password(user_data.password)
    created_at = datetime.now().isoformat()
    
    try:
        cursor.execute('''
            INSERT INTO users (id, username, email, password_hash, created_at, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (user_id, user_data.username, user_data.email, password_hash, created_at))
        
        conn.commit()
        
        return User(
            id=user_id,
            username=user_data.username,
            email=user_data.email,
            created_at=created_at,
            is_active=True
        )
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Пользователь с таким именем или email уже существует")
    finally:
        conn.close()

@app.post("/api/auth/login", response_model=Token)
async def login_user(login_data: UserLogin):
    """Вход пользователя"""
    conn = sqlite3.connect('api_keys.db')
    cursor = conn.cursor()
    
    # Находим пользователя
    cursor.execute('SELECT id, username, email, password_hash, created_at FROM users WHERE username = ? AND is_active = 1', (login_data.username,))
    user = cursor.fetchone()
    
    if not user or not verify_password(login_data.password, user[3]):
        conn.close()
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")
    
    # Создаем токен
    token = generate_token()
    token_id = str(uuid.uuid4())
    expires_at = get_token_expires()
    created_at = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT INTO tokens (id, user_id, token, expires_at, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (token_id, user[0], token, expires_at, created_at))
    
    conn.commit()
    conn.close()
    
    return Token(
        access_token=token,
        token_type="bearer",
        expires_at=expires_at
    )

@app.get("/api/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Получение информации о текущем пользователе"""
    return current_user

@app.post("/api/auth/logout")
async def logout_user(current_user: User = Depends(get_current_user)):
    """Выход пользователя (удаление токена)"""
    conn = sqlite3.connect('api_keys.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM tokens WHERE user_id = ?', (current_user.id,))
    conn.commit()
    conn.close()
    
    return {"message": "Успешный выход"}

@app.post("/api/keys", response_model=APIKey)
async def create_api_key(request: CreateKeyRequest, current_user: User = Depends(get_current_user)):
    """Создать новый API ключ"""
    api_key_value = generate_api_key()
    key_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()

    expires_at = None
    if request.expires_in_days:
        expires_at = get_expires_date(request.expires_in_days)

    conn = sqlite3.connect('api_keys.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO api_keys (id, name, key, created_at, expires_at, is_active, user_id)
            VALUES (?, ?, ?, ?, ?, 1, ?)
        ''', (key_id, request.name, api_key_value, created_at, expires_at, current_user.id))

        conn.commit()

        return APIKey(
            id=key_id,
            name=request.name,
            key=api_key_value,
            created_at=created_at,
            expires_at=expires_at,
            is_active=True,
            user_id=current_user.id
        )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Ключ с таким значением уже существует")
    finally:
        conn.close()

@app.get("/api/keys", response_model=List[APIKey])
async def get_api_keys(current_user: User = Depends(get_current_user)):
    """Получить все API ключи пользователя"""
    conn = sqlite3.connect('api_keys.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, name, key, created_at, expires_at, is_active, user_id FROM api_keys WHERE user_id = ? ORDER BY created_at DESC', (current_user.id,))

    keys = []
    for row in cursor.fetchall():
        keys.append(APIKey(
            id=row[0],
            name=row[1],
            key=row[2],
            created_at=row[3],
            expires_at=row[4],
            is_active=bool(row[5]),
            user_id=row[6]
        ))

    conn.close()
    return keys

@app.delete("/api/keys/{key_id}")
async def delete_api_key(key_id: str, current_user: User = Depends(get_current_user)):
    """Удалить API ключ"""
    conn = sqlite3.connect('api_keys.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM api_keys WHERE id = ? AND user_id = ?', (key_id, current_user.id))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if not deleted:
        raise HTTPException(status_code=404, detail="Ключ не найден")

    return {"message": "Ключ успешно удален"}

@app.put("/api/keys/{key_id}/toggle")
async def toggle_api_key(key_id: str, current_user: User = Depends(get_current_user)):
    """Включить/выключить API ключ"""
    conn = sqlite3.connect('api_keys.db')
    cursor = conn.cursor()

    # Получить текущее состояние
    cursor.execute('SELECT is_active FROM api_keys WHERE id = ? AND user_id = ?', (key_id, current_user.id))
    result = cursor.fetchone()

    if not result:
        conn.close()
        raise HTTPException(status_code=404, detail="Ключ не найден")

    new_status = 0 if result[0] else 1
    cursor.execute('UPDATE api_keys SET is_active = ? WHERE id = ? AND user_id = ?', (new_status, key_id, current_user.id))
    conn.commit()
    conn.close()

    return {"message": f"Ключ {'активирован' if new_status else 'деактивирован'}"}

# DeepSeek API проксирование
@app.post("/api/deepseek/chat/completions")
async def deepseek_chat_completions(request: Request):
    """Проксирование запросов к DeepSeek API"""
    # Получаем API ключ из заголовка Authorization
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется API ключ в заголовке Authorization: Bearer <your-api-key>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key = auth_header[7:]  # Убираем "Bearer "
    
    # Валидируем API ключ
    validation_result = await validate_api_key(api_key)
    if not validation_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или истекший API ключ",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user, key_id = validation_result
    
    # Получаем данные запроса
    try:
        request_data = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный JSON в теле запроса"
        )
    
    # Проверяем наличие обязательных полей
    if "messages" not in request_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Отсутствует поле 'messages' в запросе"
        )
    
    # Подготавливаем запрос к локальному DeepSeek
    deepseek_url = f"{DEEPSEEK_API_BASE}/api/chat/completions"
    deepseek_headers = {"Content-Type": "application/json"}
    
    # Добавляем логирование использования
    conn = sqlite3.connect('api_keys.db')
    cursor = conn.cursor()
    log_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO api_usage_log (id, user_id, api_key_id, endpoint, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (log_id, user.id, key_id, "deepseek_chat", datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    # Отправляем запрос к DeepSeek
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                deepseek_url,
                json=request_data,
                headers=deepseek_headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Ошибка DeepSeek API: {response.text}"
                )
                
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Таймаут при обращении к DeepSeek API"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка подключения к DeepSeek API: {str(e)}"
        )

@app.get("/api/deepseek/models")
async def deepseek_models(request: Request):
    """Получение списка доступных моделей DeepSeek"""
    # Получаем API ключ из заголовка Authorization
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется API ключ в заголовке Authorization: Bearer <your-api-key>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key = auth_header[7:]  # Убираем "Bearer "
    
    # Валидируем API ключ
    validation_result = await validate_api_key(api_key)
    if not validation_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или истекший API ключ",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user, key_id = validation_result
    
    # Проксируем запрос к локальному DeepSeek
    models_url = f"{DEEPSEEK_API_BASE}/api/models"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(models_url)
            if resp.status_code == 200:
                return resp.json()
            else:
                raise HTTPException(
                    status_code=resp.status_code,
                    detail=f"DeepSeek error: {resp.text}"
                )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка подключения к DeepSeek: {str(e)}"
        )

@app.get("/")
async def root():
    """Главная страница"""
    return {"message": "WindexRouter API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1101)
