from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import uuid
from datetime import datetime
import os

app = FastAPI(title="WindexRouter API", description="API для генерации и управления API ключами")

# CORS для работы с Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модель для API ключа
class APIKey(BaseModel):
    id: str
    name: str
    key: str
    created_at: str
    expires_at: Optional[str] = None
    is_active: bool = True

# Модель для создания ключа
class CreateKeyRequest(BaseModel):
    name: str
    expires_in_days: Optional[int] = None

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('api_keys.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            key TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT,
            is_active INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

# Генерация уникального API ключа
def generate_api_key():
    return f"wr_{uuid.uuid4().hex}"

# Получение даты истечения
def get_expires_date(days: int):
    from datetime import timedelta
    return (datetime.now() + timedelta(days=days)).isoformat()

# Инициализация БД при запуске
init_db()

@app.post("/api/keys", response_model=APIKey)
async def create_api_key(request: CreateKeyRequest):
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
            INSERT INTO api_keys (id, name, key, created_at, expires_at, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (key_id, request.name, api_key_value, created_at, expires_at))

        conn.commit()

        return APIKey(
            id=key_id,
            name=request.name,
            key=api_key_value,
            created_at=created_at,
            expires_at=expires_at,
            is_active=True
        )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Ключ с таким значением уже существует")
    finally:
        conn.close()

@app.get("/api/keys", response_model=List[APIKey])
async def get_api_keys():
    """Получить все API ключи"""
    conn = sqlite3.connect('api_keys.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, name, key, created_at, expires_at, is_active FROM api_keys ORDER BY created_at DESC')

    keys = []
    for row in cursor.fetchall():
        keys.append(APIKey(
            id=row[0],
            name=row[1],
            key=row[2],
            created_at=row[3],
            expires_at=row[4],
            is_active=bool(row[5])
        ))

    conn.close()
    return keys

@app.delete("/api/keys/{key_id}")
async def delete_api_key(key_id: str):
    """Удалить API ключ"""
    conn = sqlite3.connect('api_keys.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM api_keys WHERE id = ?', (key_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if not deleted:
        raise HTTPException(status_code=404, detail="Ключ не найден")

    return {"message": "Ключ успешно удален"}

@app.put("/api/keys/{key_id}/toggle")
async def toggle_api_key(key_id: str):
    """Включить/выключить API ключ"""
    conn = sqlite3.connect('api_keys.db')
    cursor = conn.cursor()

    # Получить текущее состояние
    cursor.execute('SELECT is_active FROM api_keys WHERE id = ?', (key_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        raise HTTPException(status_code=404, detail="Ключ не найден")

    new_status = 0 if result[0] else 1
    cursor.execute('UPDATE api_keys SET is_active = ? WHERE id = ?', (new_status, key_id))
    conn.commit()
    conn.close()

    return {"message": f"Ключ {'активирован' if new_status else 'деактивирован'}"}

@app.get("/")
async def root():
    """Главная страница"""
    return {"message": "WindexRouter API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
