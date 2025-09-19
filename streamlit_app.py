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
API_BASE_URL = "http://localhost:1101"

# Заголовки для запросов
def get_headers():
    headers = {"Content-Type": "application/json"}
    if "access_token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    return headers

# Функции для работы с аутентификацией
def register_user(username, email, password):
    """Регистрация пользователя"""
    url = f"{API_BASE_URL}/api/auth/register"
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(url, json=data, headers=get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json() if response.content else {"detail": "Ошибка регистрации"}
            return {"error": error_data.get("detail", "Ошибка регистрации")}
    except Exception as e:
        return {"error": f"Ошибка подключения к API: {e}"}

def login_user(username, password):
    """Вход пользователя"""
    url = f"{API_BASE_URL}/api/auth/login"
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, json=data, headers=get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json() if response.content else {"detail": "Ошибка входа"}
            return {"error": error_data.get("detail", "Ошибка входа")}
    except Exception as e:
        return {"error": f"Ошибка подключения к API: {e}"}

def get_current_user():
    """Получение информации о текущем пользователе"""
    url = f"{API_BASE_URL}/api/auth/me"
    
    try:
        response = requests.get(url, headers=get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

def logout_user():
    """Выход пользователя"""
    url = f"{API_BASE_URL}/api/auth/logout"
    
    try:
        response = requests.post(url, headers=get_headers())
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        return False

# Функции для работы с API ключами
def create_api_key(name, expires_days=None):
    """Создать новый API ключ"""
    url = f"{API_BASE_URL}/api/keys"
    data = {"name": name}
    if expires_days:
        data["expires_in_days"] = expires_days

    try:
        response = requests.post(url, json=data, headers=get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json() if response.content else {"detail": "Ошибка создания ключа"}
            return {"error": error_data.get("detail", "Ошибка создания ключа")}
    except Exception as e:
        return {"error": f"Ошибка подключения к API: {e}"}

def get_api_keys():
    """Получить все API ключи пользователя"""
    url = f"{API_BASE_URL}/api/keys"
    try:
        response = requests.get(url, headers=get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        return []

def delete_api_key(key_id):
    """Удалить API ключ"""
    url = f"{API_BASE_URL}/api/keys/{key_id}"
    try:
        response = requests.delete(url, headers=get_headers())
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        return False

def toggle_api_key(key_id):
    """Включить/выключить API ключ"""
    url = f"{API_BASE_URL}/api/keys/{key_id}/toggle"
    try:
        response = requests.put(url, headers=get_headers())
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        return False

# Интерфейс входа/регистрации
def auth_page():
    """Страница аутентификации"""
    st.title("🔑 WindexRouter - Вход в систему")
    
    tab1, tab2 = st.tabs(["Вход", "Регистрация"])
    
    with tab1:
        st.header("Вход в систему")
        
        with st.form("login_form"):
            username = st.text_input("Имя пользователя", placeholder="Введите имя пользователя")
            password = st.text_input("Пароль", type="password", placeholder="Введите пароль")
            
            if st.form_submit_button("Войти", type="primary"):
                if username and password:
                    result = login_user(username, password)
                    if "error" in result:
                        st.error(f"❌ {result['error']}")
                    else:
                        st.session_state.access_token = result["access_token"]
                        st.session_state.user_info = {
                            "username": username,
                            "token": result["access_token"],
                            "expires_at": result["expires_at"]
                        }
                        st.success("✅ Успешный вход!")
                        st.rerun()
                else:
                    st.error("❌ Пожалуйста, заполните все поля")
    
    with tab2:
        st.header("Регистрация")
        
        with st.form("register_form"):
            username = st.text_input("Имя пользователя", placeholder="Введите имя пользователя")
            email = st.text_input("Email", placeholder="Введите email")
            password = st.text_input("Пароль", type="password", placeholder="Введите пароль")
            password_confirm = st.text_input("Подтвердите пароль", type="password", placeholder="Подтвердите пароль")
            
            if st.form_submit_button("Зарегистрироваться", type="primary"):
                if username and email and password and password_confirm:
                    if password != password_confirm:
                        st.error("❌ Пароли не совпадают")
                    elif len(password) < 6:
                        st.error("❌ Пароль должен содержать минимум 6 символов")
                    else:
                        result = register_user(username, email, password)
                        if "error" in result:
                            st.error(f"❌ {result['error']}")
                        else:
                            st.success("✅ Регистрация успешна! Теперь вы можете войти в систему.")
                else:
                    st.error("❌ Пожалуйста, заполните все поля")

# Личный кабинет пользователя
def user_dashboard():
    """Личный кабинет пользователя"""
    # Получаем информацию о пользователе
    user_info = get_current_user()
    if not user_info:
        st.error("❌ Ошибка получения информации о пользователе")
        return
    
    # Заголовок с информацией о пользователе
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title(f"👋 Добро пожаловать, {user_info['username']}!")
    
    with col2:
        st.metric("Email", user_info['email'])
    
    with col3:
        if st.button("🚪 Выйти", type="secondary"):
            if logout_user():
                # Очищаем сессию
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.success("✅ Успешный выход!")
                st.rerun()
            else:
                st.error("❌ Ошибка при выходе")
    
    st.divider()
    
    # Создание нового ключа
    st.header("🔑 Создать новый API ключ")
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
            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                st.success("✅ Ключ успешно создан!")
                st.code(result["key"], language="text")
                st.rerun()
        else:
            st.error("❌ Пожалуйста, введите название ключа")

    st.divider()

    # Список существующих ключей
    st.header("📋 Мои API ключи")

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
    **WindexRouter** - система управления API ключами с доступом к DeepSeek AI.

    ### Возможности:
    - 🔑 Генерация уникальных API ключей
    - 📅 Настройка срока действия ключей
    - 🔄 Активация/деактивация ключей
    - 🗑️ Удаление ненужных ключей
    - 📊 Просмотр всех созданных ключей
    - 👤 Личный кабинет пользователя
    - 🤖 **Доступ к DeepSeek AI через ваши API ключи**

    ### Использование DeepSeek API:
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

    ### Доступные модели DeepSeek:
    - **deepseek-chat** - Универсальная модель для чата
    - **deepseek-coder** - Специализированная модель для программирования

    ### Получение списка моделей:
    ```python
    response = requests.get(
        "http://localhost:1101/api/deepseek/models",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    ```
    """)

# Основная функция
def main():
    # Проверяем, авторизован ли пользователь
    if "access_token" not in st.session_state:
        auth_page()
    else:
        user_dashboard()

if __name__ == "__main__":
    main()