"""
Основной модуль приложения PathFinder.

Этот модуль обеспечивает запуск приложения и демонстрацию
его возможностей.
"""

import os
import sys
import argparse

# Импортируем классы приложения
from maze import Maze
from pathfinder import PathFinder
from visualizer import MazeVisualizer

# Импортируем модуль для отчетов об ошибках
import error_reporter


def parse_args():
    """
    Парсинг аргументов командной строки.
    
    Returns:
        argparse.Namespace: Объект с аргументами командной строки.
    """
    parser = argparse.ArgumentParser(description="PathFinder - поиск пути в лабиринте")
    parser.add_argument("--with-bugzilla", action="store_true", 
                       help="Включить интеграцию с Bugzilla для отчетов об ошибках")
    parser.add_argument("--bugzilla-headless", action="store_true", 
                       help="Запустить браузер Bugzilla в фоновом режиме")
    parser.add_argument("--force-error", action="store_true", 
                       help="Сгенерировать тестовую ошибку для проверки отчетов")
    return parser.parse_args()


@error_reporter.catch_and_report(component="UI", additional_info="Ошибка в основной функции")
def main():
    """
    Основная функция приложения.
    """
    # Парсим аргументы командной строки
    args = parse_args()
    
    # Инициализируем систему отчетов об ошибках, если это указано в аргументах
    if args.with_bugzilla:
        print("Инициализация системы отчетов об ошибках Bugzilla...")
        success = error_reporter.initialize(enabled=True, headless=args.bugzilla_headless)
        if success:
            print("Система отчетов об ошибках Bugzilla успешно инициализирована")
        else:
            print("Не удалось инициализировать систему отчетов об ошибках Bugzilla")
    
    # Если указано сгенерировать тестовую ошибку
    if args.force_error:
        print("Генерация тестовой ошибки для проверки отчетов...")
        # Используем контекстный менеджер для перехвата исключения
        with error_reporter.ErrorContext("Testing", "Тестовая ошибка для проверки системы отчетов"):
            # Вызываем исключение
            raise ValueError("Тестовая ошибка для проверки системы отчетов")
    
    # Создаем лабиринт
    maze = Maze()
    print("Лабиринт:")
    print(maze)
    
    # Создаем объект PathFinder
    finder = PathFinder(maze)
    
    # Ищем путь
    path = finder.bfs()
    
    if path:
        print(f"Найден путь длиной {len(path)} шагов:")
        for i, pos in enumerate(path):
            print(f"Шаг {i+1}: {pos}")
        
        # Получаем направления
        directions = finder.get_path_directions(path)
        print("\nПоследовательность направлений:")
        for i, direction in enumerate(directions):
            print(f"Шаг {i+1}: {direction}")
        
        # Визуализируем
        visualizer = MazeVisualizer(maze)
        visualizer.draw_maze()
        visualizer.draw_path(path)
        
        # Создаем папку visualization, если она не существует
        os.makedirs("../visualization", exist_ok=True)
        
        # Сохраняем изображение
        visualizer.save("../visualization/maze_solution.png")
        print("\nВизуализация сохранена в файл visualization/maze_solution.png")
        
        # Показываем изображение
        visualizer.show()
    else:
        print("Путь не найден!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        sys.exit(1)
    finally:
        # Закрываем соединение с Bugzilla
        error_reporter.shutdown() 