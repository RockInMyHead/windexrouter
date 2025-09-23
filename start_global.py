#!/usr/bin/env python3
"""
WindexRouter - Скрипт запуска с глобальным доступом через ngrok
"""

import subprocess
import sys
import time
import signal
import os
import requests
import json

def check_ngrok_installed():
    """Проверка установки ngrok"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def get_ngrok_tunnels():
    """Получение информации о активных туннелях ngrok"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('tunnels', [])
    except:
        pass
    return []

def run_fastapi():
    """Запуск FastAPI сервера"""
    print("🚀 Запуск FastAPI сервера...")
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", "0.0.0.0",
        "--port", "1101",
        "--reload"
    ])

def run_streamlit():
    """Запуск Streamlit приложения"""
    print("🌐 Запуск Streamlit приложения...")
    time.sleep(2)  # Ждем запуска FastAPI
    return subprocess.Popen([
        sys.executable, "-m", "streamlit", "run",
        "streamlit_app.py",
        "--server.port", "1102",
        "--server.address", "0.0.0.0"
    ])

def run_ngrok_streamlit():
    """Запуск ngrok туннеля для Streamlit"""
    print("🌍 Создание ngrok туннеля для Streamlit...")
    return subprocess.Popen([
        "ngrok", "http", "1102", "--log=stdout"
    ])

def run_ngrok_fastapi():
    """Запуск ngrok туннеля для FastAPI"""
    print("🌍 Создание ngrok туннеля для FastAPI...")
    time.sleep(3)  # Ждем запуска первого туннеля
    return subprocess.Popen([
        "ngrok", "http", "1101", "--log=stdout"
    ])

def print_tunnel_info():
    """Вывод информации о туннелях"""
    print("\n" + "="*60)
    print("🌍 ГЛОБАЛЬНЫЙ ДОСТУП К WINDEXROUTER")
    print("="*60)
    
    tunnels = get_ngrok_tunnels()
    if tunnels:
        print("\n📡 Активные туннели:")
        for tunnel in tunnels:
            public_url = tunnel['public_url']
            local_addr = tunnel['config']['addr']
            print(f"  🌐 {public_url} -> {local_addr}")
        
        print("\n🔗 Доступ к приложению:")
        for tunnel in tunnels:
            if tunnel['config']['addr'] == 'http://localhost:1102':
                print(f"  📱 Streamlit интерфейс: {tunnel['public_url']}")
            elif tunnel['config']['addr'] == 'http://localhost:1101':
                print(f"  🔧 FastAPI сервер: {tunnel['public_url']}")
                print(f"  📚 API документация: {tunnel['public_url']}/docs")
    else:
        print("\n❌ Туннели ngrok не найдены")
    
    print("\n🏠 Локальный доступ:")
    print("  📱 Streamlit: http://localhost:1102")
    print("  🔧 FastAPI: http://localhost:1101")
    print("  📚 API docs: http://localhost:1101/docs")
    
    print("\n❌ Для остановки нажмите Ctrl+C")
    print("="*60)

def main():
    print("🎯 Запуск WindexRouter с глобальным доступом...")
    
    # Проверка ngrok
    if not check_ngrok_installed():
        print("❌ ngrok не установлен!")
        print("📥 Установите ngrok: https://ngrok.com/download")
        sys.exit(1)
    
    # Запуск сервисов
    fastapi_process = run_fastapi()
    streamlit_process = run_streamlit()
    
    # Запуск туннелей
    ngrok_streamlit_process = run_ngrok_streamlit()
    ngrok_fastapi_process = run_ngrok_fastapi()
    
    # Ждем запуска туннелей
    time.sleep(5)
    
    # Вывод информации
    print_tunnel_info()
    
    def signal_handler(sig, frame):
        print("\n🛑 Остановка всех сервисов...")
        fastapi_process.terminate()
        streamlit_process.terminate()
        ngrok_streamlit_process.terminate()
        ngrok_fastapi_process.terminate()
        
        fastapi_process.wait()
        streamlit_process.wait()
        ngrok_streamlit_process.wait()
        ngrok_fastapi_process.wait()
        
        print("✅ Все сервисы остановлены")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Ожидание завершения процессов
        fastapi_process.wait()
        streamlit_process.wait()
        ngrok_streamlit_process.wait()
        ngrok_fastapi_process.wait()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()

