#!/usr/bin/env python3
"""
Пример использования WindexRouter API с DeepSeek AI
"""

import requests
import json

# Конфигурация
API_BASE_URL = "http://localhost:1101"
API_KEY = "wr_61d3c8e5150f414081b844d4dcd7cfca"  # Замените на ваш API ключ

def test_deepseek_models():
    """Тестирование получения списка моделей DeepSeek"""
    print("🔍 Получение списка моделей DeepSeek...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{API_BASE_URL}/api/deepseek/models", headers=headers)
    
    if response.status_code == 200:
        models = response.json()
        print("✅ Доступные модели:")
        for model in models["data"]:
            print(f"  - {model['id']}: {model['object']}")
    else:
        print(f"❌ Ошибка: {response.status_code} - {response.text}")

def test_deepseek_chat():
    """Тестирование чата с DeepSeek"""
    print("\n💬 Тестирование чата с DeepSeek...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "Привет! Расскажи коротко о себе."}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/deepseek/chat/completions",
        json=data,
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Ответ DeepSeek:")
        print(f"  {result['choices'][0]['message']['content']}")
    else:
        print(f"❌ Ошибка: {response.status_code} - {response.text}")

def test_invalid_key():
    """Тестирование с неверным API ключом"""
    print("\n🔒 Тестирование с неверным API ключом...")
    
    headers = {
        "Authorization": "Bearer invalid-key",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{API_BASE_URL}/api/deepseek/models", headers=headers)
    
    if response.status_code == 401:
        print("✅ Неверный ключ корректно отклонен")
    else:
        print(f"❌ Неожиданный ответ: {response.status_code} - {response.text}")

def main():
    """Основная функция"""
    print("🚀 Тестирование WindexRouter API с DeepSeek AI")
    print("=" * 50)
    
    try:
        # Тест 1: Получение моделей
        test_deepseek_models()
        
        # Тест 2: Чат с DeepSeek
        test_deepseek_chat()
        
        # Тест 3: Неверный ключ
        test_invalid_key()
        
        print("\n✅ Все тесты завершены!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения. Убедитесь, что сервер запущен на порту 1101")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    main()
