#!/usr/bin/env python3
"""
WindexRouter - Скрипт запуска
Запускает FastAPI сервер и Streamlit приложение
"""

import subprocess
import sys
import time
import signal
import os

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

def main():
    print("🎯 Запуск WindexRouter...")
    print("=" * 50)

    # Запуск FastAPI
    fastapi_process = run_fastapi()

    # Запуск Streamlit
    streamlit_process = run_streamlit()

    print("\n✅ Сервисы запущены!")
    print("📊 FastAPI: http://localhost:1101")
    print("🌐 Streamlit: http://localhost:1102")
    print("📚 API документация: http://localhost:1101/docs")
    print("\n❌ Для остановки нажмите Ctrl+C\n")

    def signal_handler(sig, frame):
        print("\n🛑 Остановка сервисов...")
        fastapi_process.terminate()
        streamlit_process.terminate()
        fastapi_process.wait()
        streamlit_process.wait()
        print("✅ Все сервисы остановлены")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Ожидание завершения процессов
        fastapi_process.wait()
        streamlit_process.wait()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()


