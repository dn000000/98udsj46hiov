"""
Скрипт для запуска всех тестов и проверки зависимостей.
"""

import os
import sys
import subprocess
import importlib
import pkg_resources


def check_dependencies():
    """
    Проверяет наличие всех необходимых зависимостей.
    
    Returns:
        bool: True, если все зависимости установлены, иначе False.
    """
    print("Проверка зависимостей...")
    
    required_packages = [
        "numpy",
        "matplotlib",
        "pytest",
        "sphinx",
        "pylint",
        "requests",
        "flake8",
        "selenium"
        #здесь должен был быть pytest-cov, но из за некоторых магических ps-обстоятельств, оно не может его найти в моих пакетах, когда он есть.
        #я все еще думаю, что его забрал демогоргон. 
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package}")
    
    if missing_packages:
        print("\nОтсутствуют следующие пакеты:")
        for package in missing_packages:
            print(f"- {package}")
        
        print("\nУстановите их с помощью команды:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("\nВсе зависимости установлены.")
    return True


def run_tests():
    """
    Запускает все тесты с отчетом о покрытии.
    
    Returns:
        bool: True, если все тесты прошли успешно, иначе False.
    """
    print("\nЗапуск тестов...")
    
    # Устанавливаем путь к директории с тестами
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
    src_dir = os.path.join(os.path.dirname(__file__), 'src')
    
    # Запускаем тесты и генерируем отчет о покрытии
    try:
        result = subprocess.run([
            sys.executable, 
            "-m", "pytest", 
            tests_dir, 
            f"--cov={src_dir}", 
            "--cov-report=term", 
            "--cov-report=html:coverage_report",
            "-v"
        ], check=False)
        
        if result.returncode == 0:
            print("\nВсе тесты успешно пройдены.")
            print("Отчет о покрытии кода сохранен в директории 'coverage_report'.")
            return True
        else:
            print("\nНекоторые тесты не пройдены.")
            return False
        
    except Exception as e:
        print(f"\nОшибка при выполнении тестов: {e}")
        return False


def run_lint():
    """
    Запускает статический анализ кода.
    
    Returns:
        bool: True, если анализ прошел успешно, иначе False.
    """
    print("\nЗапуск статического анализа кода...")
    
    src_dir = os.path.join(os.path.dirname(__file__), 'src')
    
    try:
        result = subprocess.run([
            sys.executable, 
            "-m", "pylint", 
            src_dir
        ], check=False)
        
        if result.returncode == 0:
            print("\nСтатический анализ кода успешно пройден.")
            return True
        else:
            print("\nСтатический анализ кода выявил проблемы.")
            return False
        
    except Exception as e:
        print(f"\nОшибка при выполнении статического анализа кода: {e}")
        return False


def main():
    """
    Основная функция скрипта.
    """
    print("=" * 80)
    print("Запуск тестов и проверка зависимостей для проекта PathFinder")
    print("=" * 80)
    
    # Проверяем зависимости
    if not check_dependencies():
        print("\nУстановите необходимые зависимости перед запуском тестов.")
        return
    
    # Запускаем тесты
    tests_passed = run_tests()
    
    # Запускаем статический анализ кода
    lint_passed = run_lint()
    
    # Выводим итоговый результат
    print("\n" + "=" * 80)
    print("Итоговый результат:")
    print(f"- Тесты: {'ПРОЙДЕНЫ' if tests_passed else 'НЕ ПРОЙДЕНЫ'}")
    print(f"- Статический анализ кода: {'ПРОЙДЕН' if lint_passed else 'НЕ ПРОЙДЕН'}")
    print("=" * 80)


if __name__ == "__main__":
    main() 