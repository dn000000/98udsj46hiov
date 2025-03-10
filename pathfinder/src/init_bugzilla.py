"""
Скрипт для инициализации BugZilla.

Этот скрипт запускает Docker-контейнеры с BugZilla и создает начальные данные.
"""

import os
import sys
import time
import subprocess
import requests

from bugzilla_integration import BugzillaIntegration


def check_docker_installed():
    """
    Проверяет, установлен ли Docker.
    
    Returns:
        bool: True, если Docker установлен, иначе False.
    """
    try:
        subprocess.run(["docker", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def check_docker_compose_installed():
    """
    Проверяет, установлен ли Docker Compose.
    
    Returns:
        bool: True, если Docker Compose установлен, иначе False.
    """
    try:
        subprocess.run(["docker-compose", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def start_bugzilla():
    """
    Запускает Docker-контейнеры с BugZilla.
    
    Returns:
        bool: True, если запуск успешен, иначе False.
    """
    # Путь к файлу docker-compose.yml
    compose_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../pathfinder/bugzilla/docker-compose.yml'))
    
    if not os.path.exists(compose_file):
        print(f"Файл {compose_file} не найден.")
        return False
    
    try:
        # Запускаем контейнеры
        subprocess.run(["docker-compose", "-f", compose_file, "up", "-d"], check=True)
        print("Docker-контейнеры с BugZilla запущены.")
        return True
    except subprocess.SubprocessError as e:
        print(f"Ошибка при запуске Docker-контейнеров: {str(e)}")
        return False


def wait_for_bugzilla(url="http://localhost:8080", timeout=300):
    """
    Ожидает, пока BugZilla станет доступной.
    
    Args:
        url (str): URL-адрес сервера BugZilla.
        timeout (int): Таймаут в секундах.
        
    Returns:
        bool: True, если BugZilla доступна, иначе False.
    """
    print(f"Ожидание запуска BugZilla (таймаут: {timeout} секунд)...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("BugZilla доступна.")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(5)
        print(".", end="", flush=True)
    
    print("\nТаймаут ожидания BugZilla.")
    return False


def init_bugzilla_data():
    """
    Инициализирует данные в BugZilla.
    
    Returns:
        bool: True, если инициализация успешна, иначе False.
    """
    print("Инициализация данных в BugZilla...")
    
    # Создаем объект интеграции
    bugzilla = BugzillaIntegration()
    
    # Входим в систему
    login_result = bugzilla.login("admin@example.com", "password")
    
    if "error" in login_result:
        print(f"Ошибка при входе в BugZilla: {login_result['error']}")
        return False
    
    # Создаем продукт PathFinder
    product_result = bugzilla.create_product(
        "PathFinder",
        "Приложение для поиска пути в лабиринте",
        "1.0"
    )
    
    if "error" in product_result:
        print(f"Ошибка при создании продукта: {product_result['error']}")
        return False
    
    # Создаем компоненты
    components = [
        {
            "name": "Core",
            "description": "Ядро приложения, включая алгоритмы поиска пути",
            "default_assignee": "admin@example.com"
        },
        {
            "name": "Visualization",
            "description": "Визуализация лабиринта и пути",
            "default_assignee": "admin@example.com"
        },
        {
            "name": "Equidistant",
            "description": "Алгоритм поиска равноудаленной точки",
            "default_assignee": "admin@example.com"
        }
    ]
    
    for component in components:
        result = bugzilla.create_component(
            "PathFinder",
            component["name"],
            component["description"],
            component["default_assignee"]
        )
        
        if "error" in result:
            print(f"Ошибка при создании компонента {component['name']}: {result['error']}")
            return False
    
    # Создаем несколько ошибок
    bugs = [
        {
            "product": "PathFinder",
            "component": "Core",
            "summary": "Алгоритм BFS не находит путь в некоторых случаях",
            "description": "Алгоритм BFS не находит путь, если в лабиринте есть длинные тупики.",
            "severity": "major",
            "priority": "High"
        },
        {
            "product": "PathFinder",
            "component": "Visualization",
            "summary": "Неверное отображение пути на визуализации",
            "description": "Путь на визуализации отображается с неправильными координатами.",
            "severity": "normal",
            "priority": "Normal"
        },
        {
            "product": "PathFinder",
            "component": "Equidistant",
            "summary": "Алгоритм не находит равноудаленную точку для трех героев",
            "description": "Алгоритм не находит равноудаленную точку, если в лабиринте есть три героя.",
            "severity": "critical",
            "priority": "Highest"
        },
        {
            "product": "PathFinder",
            "component": "Core",
            "summary": "Приложение падает при пустом лабиринте",
            "description": "Приложение падает с ошибкой деления на ноль при попытке запустить поиск пути в пустом лабиринте.",
            "severity": "critical",
            "priority": "Highest"
        }
    ]
    
    for bug_data in bugs:
        result = bugzilla.create_bug(**bug_data)
        
        if "error" in result:
            print(f"Ошибка при создании ошибки {bug_data['summary']}: {result['error']}")
            continue
        
        print(f"Создана ошибка: {bug_data['summary']} (ID: {result.get('id')})")
    
    print("Данные в BugZilla успешно инициализированы.")
    return True


def main():
    """
    Основная функция скрипта.
    """
    print("Инициализация BugZilla для проекта PathFinder...")
    
    # Проверяем, установлен ли Docker
    if not check_docker_installed():
        print("Docker не установлен. Пожалуйста, установите Docker и повторите попытку.")
        return
    
    # Проверяем, установлен ли Docker Compose
    if not check_docker_compose_installed():
        print("Docker Compose не установлен. Пожалуйста, установите Docker Compose и повторите попытку.")
        return
    
    # Запускаем Docker-контейнеры с BugZilla
    if not start_bugzilla():
        return
    
    # Ожидаем, пока BugZilla станет доступной
    if not wait_for_bugzilla():
        return
    
    # Инициализируем данные в BugZilla
    init_bugzilla_data()
    
    print("\nBugZilla успешно инициализирована.")
    print("Вы можете получить доступ к BugZilla по адресу: http://localhost:8080")
    print("Логин: admin@example.com")
    print("Пароль: password")


if __name__ == "__main__":
    main() 