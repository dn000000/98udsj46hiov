"""
Скрипт для запуска тестов с отчетом о покрытии.
"""

import sys
import os
import subprocess
import argparse

def run_tests(only_hex_tests=False, test_pattern=None):
    """
    Запускает все тесты с отчетом о покрытии кода.
    
    Args:
        only_hex_tests (bool): Если True, запускает только тесты для гексагональной карты
                              и расовых особенностей
        test_pattern (str): Паттерн для фильтрации тестов (опция -k в pytest)
    """
    # Определяем пути к директориям
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.join(current_dir, "tests")
    src_dir = os.path.join(current_dir, "src")
    
    # Проверяем, что директории существуют
    if not os.path.exists(tests_dir):
        print(f"Ошибка: Директория с тестами '{tests_dir}' не найдена.")
        sys.exit(1)
    
    if not os.path.exists(src_dir):
        print(f"Ошибка: Директория с исходным кодом '{src_dir}' не найдена.")
        sys.exit(1)
    
    # Добавляем путь к src в PYTHONPATH для решения ошибки 'No module named maze'
    sys.path.append(src_dir)
    
    # Проверяем доступность модулей
    try:
        # Проверяем, можем ли мы импортировать базовые модули
        __import__('maze')
        __import__('pathfinder')
        __import__('equidistant_finder')
        
        # Проверяем модули 3-го этапа
        __import__('terrain_maze')
        __import__('terrain_pathfinder')
        __import__('terrain_equidistant_finder')
        
        # Проверяем модули 4-го этапа (гексагональная карта и расовые особенности)
        try:
            from hex import hex_coordinate, hex_terrain_type, hex_cell, hex_map
            from races import race, human, elf, dwarf, orc
            from pathfinding import hex_a_star
            print("Модули 4-го этапа (гексагональная карта и расовые особенности) доступны.")
        except ImportError as e:
            print(f"Ошибка импорта модулей 4-го этапа: {e}")
            print("Некоторые тесты для гексагональной карты и расовых особенностей могут не выполниться.")
        
        print("Все необходимые модули доступны для импорта.")
    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        print("Добавляем путь к src в PYTHONPATH...")
        # Для запуска через subprocess также нужно установить PYTHONPATH
        os.environ['PYTHONPATH'] = os.pathsep.join([src_dir, os.environ.get('PYTHONPATH', '')])
    
    print(f"Запуск тестов из директории: {tests_dir}")
    print(f"Проверка покрытия кода в директории: {src_dir}")
    
    try:
        # Путь к тесту гексагональной карты
        hex_race_test = os.path.join(tests_dir, "test_hex_and_races.py")
        
        # Если запрошены только тесты для гексагональной карты
        if only_hex_tests:
            if os.path.exists(hex_race_test):
                print("\nЗапуск тестов для гексагональной карты и расовых особенностей:")
                cmd = [
                    sys.executable,
                    "-m", "pytest",
                    hex_race_test,
                    "-v"
                ]
                
                # Добавляем опцию -k, если указан паттерн для фильтрации тестов
                if test_pattern:
                    cmd.extend(["-k", test_pattern])
                    print(f"Фильтрация тестов по паттерну: {test_pattern}")
                
                subprocess.run(cmd, check=True)
                print("\nТесты для гексагональной карты и расовых особенностей успешно выполнены.")
            else:
                print(f"\nФайл тестов '{hex_race_test}' не найден. Тесты для гексагональной карты и расовых особенностей не могут быть выполнены.")
                sys.exit(1)
        else:
            # Запуск всех тестов с отчетом о покрытии
            cmd = [
                sys.executable, 
                "-m", "pytest", 
                tests_dir, 
                f"--cov={src_dir}", 
                "--cov-report=term", 
                "--cov-report=html:coverage_report",
                "-v"
            ]
            
            # Добавляем опцию -k, если указан паттерн для фильтрации тестов
            if test_pattern:
                cmd.extend(["-k", test_pattern])
                print(f"Фильтрация тестов по паттерну: {test_pattern}")
                
            subprocess.run(cmd, check=True)
            
            print("\nТесты успешно выполнены.")
            
            # Запуск конкретных тестов для гексагональной карты и расовых особенностей
            if os.path.exists(hex_race_test) and not test_pattern:  # Не запускаем отдельно, если уже применен фильтр
                print("\nЗапуск тестов для гексагональной карты и расовых особенностей:")
                subprocess.run([
                    sys.executable,
                    "-m", "pytest",
                    hex_race_test,
                    "-v"
                ], check=True)
                print("\nТесты для гексагональной карты и расовых особенностей успешно выполнены.")
            elif not os.path.exists(hex_race_test) and not test_pattern:
                print(f"\nФайл тестов '{hex_race_test}' не найден. Тесты для гексагональной карты и расовых особенностей пропущены.")
            
            print("Отчет о покрытии кода сохранен в директории 'coverage_report'.")
        
    except subprocess.CalledProcessError as e:
        print(f"\nОшибка при выполнении тестов: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Запуск тестов PathFinder")
    parser.add_argument("--hex", action="store_true", help="Запуск только тестов для гексагональной карты и рас")
    parser.add_argument("--test-pattern", help="Паттерн для фильтрации тестов (опция -k в pytest)")
    args = parser.parse_args()
    
    run_tests(only_hex_tests=args.hex, test_pattern=args.test_pattern) 