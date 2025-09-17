import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json

# Настройки
st.set_page_config(
    page_title="WindexRouter - Управление API ключами",
    page_icon="🔑",
    layout="wide"
)

# Конфигурация API
API_BASE_URL = "http://localhost:80"

# Заголовки для запросов
HEADERS = {
    "Content-Type": "application/json"
}

# Функции для работы с API
def create_api_key(name, expires_days=None):
    """Создать новый API ключ"""
    url = f"{API_BASE_URL}/api/keys"
    data = {"name": name}
    if expires_days:
        data["expires_in_days"] = expires_days

    try:
        response = requests.post(url, json=data, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Ошибка при создании ключа: {response.text}")
            return None
    except Exception as e:
        st.error(f"Ошибка подключения к API: {e}")
        return None

def get_api_keys():
    """Получить все API ключи"""
    url = f"{API_BASE_URL}/api/keys"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Ошибка при получении ключей: {response.text}")
            return []
    except Exception as e:
        st.error(f"Ошибка подключения к API: {e}")
        return []

def delete_api_key(key_id):
    """Удалить API ключ"""
    url = f"{API_BASE_URL}/api/keys/{key_id}"
    try:
        response = requests.delete(url, headers=HEADERS)
        if response.status_code == 200:
            return True
        else:
            st.error(f"Ошибка при удалении ключа: {response.text}")
            return False
    except Exception as e:
        st.error(f"Ошибка подключения к API: {e}")
        return False

def toggle_api_key(key_id):
    """Включить/выключить API ключ"""
    url = f"{API_BASE_URL}/api/keys/{key_id}/toggle"
    try:
        response = requests.put(url, headers=HEADERS)
        if response.status_code == 200:
            return True
        else:
            st.error(f"Ошибка при изменении статуса ключа: {response.text}")
            return False
    except Exception as e:
        st.error(f"Ошибка подключения к API: {e}")
        return False

# Основной интерфейс
def main():
    st.title("🔑 WindexRouter - Управление API ключами")

    # Создание нового ключа
    st.header("Создать новый API ключ")
    col1, col2 = st.columns(2)

    with col1:
        key_name = st.text_input("Название ключа", placeholder="Например: DeepSeek API Key")

    with col2:
        expires_days = st.number_input("Срок действия (дни)", min_value=1, value=30, help="0 = без срока действия")

    if st.button("🔑 Создать ключ", type="primary"):
        if key_name.strip():
            if expires_days == 0:
                expires_days = None
            result = create_api_key(key_name.strip(), expires_days)
            if result:
                st.success("✅ Ключ успешно создан!")
                st.code(result["key"], language="text")
                st.rerun()
        else:
            st.error("❌ Пожалуйста, введите название ключа")

    st.divider()

    # Список существующих ключей
    st.header("📋 Существующие API ключи")

    keys = get_api_keys()

    if keys:
        # Преобразование в DataFrame для удобного отображения
        df_data = []
        for key in keys:
            df_data.append({
                "ID": key["id"],
                "Название": key["name"],
                "Ключ": key["key"],
                "Создан": datetime.fromisoformat(key["created_at"]).strftime("%d.%m.%Y %H:%M"),
                "Истекает": datetime.fromisoformat(key["expires_at"]).strftime("%d.%m.%Y %H:%M") if key["expires_at"] else "Бессрочно",
                "Активен": "✅ Да" if key["is_active"] else "❌ Нет"
            })

        df = pd.DataFrame(df_data)

        # Отображение таблицы
        st.dataframe(
            df,
            column_config={
                "Ключ": st.column_config.TextColumn("Ключ", width="large"),
                "ID": st.column_config.TextColumn("ID", width="small")
            },
            hide_index=True,
            use_container_width=True
        )

        # Управление ключами
        st.header("⚙️ Управление ключами")

        # Группировка ключей по состоянию
        active_keys = [k for k in keys if k["is_active"]]
        inactive_keys = [k for k in keys if not k["is_active"]]

        if active_keys:
            st.subheader("Активные ключи")
            for key in active_keys:
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

                with col1:
                    st.write(f"**{key['name']}**")
                    st.code(key["key"], language="text")

                with col2:
                    st.write(f"Создан: {datetime.fromisoformat(key['created_at']).strftime('%d.%m.%Y %H:%M')}")
                    if key["expires_at"]:
                        st.write(f"Истекает: {datetime.fromisoformat(key['expires_at']).strftime('%d.%m.%Y %H:%M')}")

                with col3:
                    if st.button("🚫 Деактивировать", key=f"deactivate_{key['id']}"):
                        if toggle_api_key(key["id"]):
                            st.success("Ключ деактивирован")
                            st.rerun()

                with col4:
                    if st.button("🗑️ Удалить", key=f"delete_active_{key['id']}", type="secondary"):
                        if delete_api_key(key["id"]):
                            st.success("Ключ удален")
                            st.rerun()

        if inactive_keys:
            st.subheader("Неактивные ключи")
            for key in inactive_keys:
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

                with col1:
                    st.write(f"**{key['name']}** (неактивен)")
                    st.code(key["key"], language="text")

                with col2:
                    st.write(f"Создан: {datetime.fromisoformat(key['created_at']).strftime('%d.%m.%Y %H:%M')}")
                    if key["expires_at"]:
                        st.write(f"Истекает: {datetime.fromisoformat(key['expires_at']).strftime('%d.%m.%Y %H:%M')}")

                with col3:
                    if st.button("✅ Активировать", key=f"activate_{key['id']}"):
                        if toggle_api_key(key["id"]):
                            st.success("Ключ активирован")
                            st.rerun()

                with col4:
                    if st.button("🗑️ Удалить", key=f"delete_inactive_{key['id']}", type="secondary"):
                        if delete_api_key(key["id"]):
                            st.success("Ключ удален")
                            st.rerun()

    else:
        st.info("📭 Пока нет созданных API ключей. Создайте первый ключ выше!")

    # Информация о проекте
    st.divider()
    st.header("ℹ️ О проекте")
    st.markdown("""
    **WindexRouter** - система управления API ключами для проектов.

    ### Возможности:
    - 🔑 Генерация уникальных API ключей
    - 📅 Настройка срока действия ключей
    - 🔄 Активация/деактивация ключей
    - 🗑️ Удаление ненужных ключей
    - 📊 Просмотр всех созданных ключей

    ### Использование в проектах:
    ```python
    # Пример использования API ключа
    headers = {"Authorization": "Bearer your_api_key_here"}
    response = requests.get("https://your-api.com/endpoint", headers=headers)
    ```
    """)

if __name__ == "__main__":
    main()
