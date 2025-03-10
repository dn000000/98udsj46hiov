"""
Скрипт для запуска тестов компонентов 3-го этапа.
"""

import sys
import os
import subprocess

def run_terrain_tests():
    """
    Запускает тесты для компонентов 3-го этапа (компоненты с учетом типов местности).
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
    os.environ['PYTHONPATH'] = os.pathsep.join([src_dir, os.environ.get('PYTHONPATH', '')])
    
    # Тестовые файлы для компонентов 3-го этапа
    terrain_test_files = [
        os.path.join(tests_dir, "test_terrain_maze.py"),
        os.path.join(tests_dir, "test_terrain_pathfinder.py"),
        os.path.join(tests_dir, "test_terrain_equidistant_finder.py")
    ]
    
    # Проверяем наличие всех тестовых файлов
    missing_files = [f for f in terrain_test_files if not os.path.exists(f)]
    if missing_files:
        print("Ошибка: Следующие тестовые файлы не найдены:")
        for f in missing_files:
            print(f"  - {f}")
        sys.exit(1)
    
    print("===================================================")
    print("Тестирование компонентов Этапа 3 проекта PathFinder")
    print("===================================================")
    print()
    
    print("Запуск модульных тестов...")
    try:
        subprocess.run([
            sys.executable, 
            "-m", "pytest", 
            *terrain_test_files,
            f"--cov={src_dir}/terrain_maze.py,{src_dir}/terrain_pathfinder.py,{src_dir}/terrain_equidistant_finder.py", 
            "--cov-report=term", 
            "-v"
        ], check=True)
        
        print("\nТесты успешно выполнены.")
        
    except subprocess.CalledProcessError as e:
        print(f"\nОшибка при выполнении тестов: {e}")
        sys.exit(1)
    
    print()
    print("===================================================")
    print("Для запуска демонстрации с разными типами местности:")
    print("python examples/terrain_demo.py")
    print()
    print("Для запуска полной демонстрации с DevOps-компонентами:")
    print("python examples/terrain_and_devops_demo.py --env development --demo all")
    print("===================================================")

if __name__ == "__main__":
    run_terrain_tests() 