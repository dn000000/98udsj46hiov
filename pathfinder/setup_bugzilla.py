import requests
from bs4 import BeautifulSoup
import time
import sys

def setup_bugzilla():
    """Настройка Bugzilla через веб-интерфейс"""
    base_url = "http://localhost:8080"
    
    # Шаг 1: Проверка доступности Bugzilla
    print("Шаг 1: Проверка доступности Bugzilla...")
    try:
        response = requests.get(f"{base_url}/index.cgi")
        if response.status_code != 200:
            print(f"Ошибка: Bugzilla недоступна. Статус код: {response.status_code}")
            return False
        
        print("Bugzilla доступна!")
    except Exception as e:
        print(f"Ошибка при подключении к Bugzilla: {e}")
        return False
    
    # Шаг 2: Создание учетной записи администратора
    print("\nШаг 2: Создание учетной записи администратора...")
    try:
        # Открываем страницу создания учетной записи
        response = requests.get(f"{base_url}/createaccount.cgi")
        if response.status_code != 200:
            print(f"Ошибка: Не удалось открыть страницу создания учетной записи. Статус код: {response.status_code}")
            return False
        
        # Извлекаем токен CSRF
        soup = BeautifulSoup(response.text, 'html.parser')
        token = soup.find('input', {'name': 'token'})
        if not token:
            print("Ошибка: Не удалось найти токен CSRF")
            return False
        
        token_value = token.get('value')
        
        # Создаем учетную запись
        data = {
            'token': token_value,
            'email': 'admin@example.com',
            'realname': 'Administrator',
            'password': 'admin123',
            'password2': 'admin123'
        }
        
        response = requests.post(f"{base_url}/createaccount.cgi", data=data)
        
        if "account has been created" in response.text:
            print("Учетная запись администратора создана успешно!")
        else:
            print("Предупреждение: Возможно, учетная запись уже существует или произошла ошибка.")
            print(f"Статус код: {response.status_code}")
    except Exception as e:
        print(f"Ошибка при создании учетной записи: {e}")
        return False
    
    # Шаг 3: Вход в систему
    print("\nШаг 3: Вход в систему...")
    try:
        # Открываем страницу входа
        response = requests.get(f"{base_url}/index.cgi")
        
        # Извлекаем токен CSRF
        soup = BeautifulSoup(response.text, 'html.parser')
        token = soup.find('input', {'name': 'token'})
        if not token:
            print("Ошибка: Не удалось найти токен CSRF")
            return False
        
        token_value = token.get('value')
        
        # Выполняем вход
        data = {
            'token': token_value,
            'Bugzilla_login': 'admin@example.com',
            'Bugzilla_password': 'admin123'
        }
        
        session = requests.Session()
        response = session.post(f"{base_url}/index.cgi", data=data)
        
        if "Log out" in response.text:
            print("Вход выполнен успешно!")
        else:
            print("Ошибка: Не удалось войти в систему.")
            return False
    except Exception as e:
        print(f"Ошибка при входе в систему: {e}")
        return False
    
    # Шаг 4: Проверка API
    print("\nШаг 4: Проверка API...")
    try:
        # Проверяем версию API
        response = requests.get(f"{base_url}/rest.cgi/version")
        print(f"Статус код API: {response.status_code}")
        
        if response.status_code == 200:
            print("API Bugzilla доступен!")
            
            # Проверяем авторизацию через API
            auth_data = {
                'login': 'admin@example.com',
                'password': 'admin123'
            }
            auth_response = requests.get(f"{base_url}/rest.cgi/login", params=auth_data)
            
            if auth_response.status_code == 200 and 'token' in auth_response.json():
                print("Авторизация через API успешна!")
                print(f"Токен API: {auth_response.json()['token']}")
            else:
                print(f"Ошибка авторизации через API: {auth_response.status_code}")
                print(auth_response.text)
        else:
            print(f"Ошибка доступа к API: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Ошибка при проверке API: {e}")
        return False
    
    print("\nНастройка Bugzilla завершена успешно!")
    return True

if __name__ == "__main__":
    success = setup_bugzilla()
    sys.exit(0 if success else 1) 