#!/usr/bin/env python
"""
@file terrain_and_devops_demo.py
@brief Демонстрационный скрипт для тестирования всех компонентов проекта.

@details
Этот скрипт демонстрирует работу алгоритмов поиска пути с учетом типов местности,
а также DevOps компоненты проекта (конфигурацию, отчеты об ошибках, уведомления).
"""

import sys
import os
import logging
import argparse
import traceback
from datetime import datetime

# Добавляем путь к исходному коду
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
# Добавляем корневой каталог проекта для импорта модулей pathfinder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Создаем файлы __init__.py, если их нет
config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../config'))
error_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../error_reporting'))
notify_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../notifications'))

for directory in [config_dir, error_dir, notify_dir]:
    if os.path.exists(directory) and not os.path.exists(os.path.join(directory, '__init__.py')):
        with open(os.path.join(directory, '__init__.py'), 'w') as f:
            f.write('# Инициализационный файл для модуля\n')

from terrain_maze import TerrainMaze
from terrain_pathfinder import TerrainPathFinder
from terrain_equidistant_finder import TerrainEquidistantFinder
from terrain_visualizer import TerrainVisualizer
from terrain_maps import (
    SMALL_TERRAIN_MAP, MEDIUM_TERRAIN_MAP, LARGE_TERRAIN_MAP, 
    CITY_TERRAIN_MAP, HEROES_MAP, HERO_POSITIONS, HERO_SPEEDS,
    map_with_heroes
)

# Пробуем импортировать модули DevOps
try:
    from pathfinder.config.config import Config, Environment
    from pathfinder.error_reporting.error_context import ErrorContext
    from pathfinder.error_reporting.error_api import ErrorAPI
    from pathfinder.notifications.telegram_notifier import TelegramNotifier
except ImportError:
    # Альтернативный импорт с прямыми путями
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from config.config import Config, Environment
    from error_reporting.error_context import ErrorContext
    from error_reporting.error_api import ErrorAPI
    from notifications.telegram_notifier import TelegramNotifier

def setup_parser():
    """
    @brief Настраивает парсер аргументов командной строки.
    
    @return Настроенный парсер аргументов.
    """
    parser = argparse.ArgumentParser(description="Демонстрация работы проекта PathFinder")
    
    parser.add_argument("--env", "-e", type=str, choices=["development", "testing", "production"],
                        default="development", help="Окружение для запуска")
    
    parser.add_argument("--demo", "-d", type=str, choices=["path", "gathering", "comparison", "error", "notification", "all"],
                        default="all", help="Тип демонстрации")
    
    parser.add_argument("--map", "-m", type=str, choices=["small", "medium", "large", "city", "heroes"],
                        default="small", help="Тип карты для демонстрации")
    
    return parser

def get_map_by_name(map_name):
    """
    @brief Возвращает карту по имени.
    
    @param map_name Имя карты.
    
    @return Карта в виде списка строк.
    """
    if map_name == "small":
        return SMALL_TERRAIN_MAP
    elif map_name == "medium":
        return MEDIUM_TERRAIN_MAP
    elif map_name == "large":
        return LARGE_TERRAIN_MAP
    elif map_name == "city":
        return CITY_TERRAIN_MAP
    elif map_name == "heroes":
        return map_with_heroes()
    else:
        return SMALL_TERRAIN_MAP

def demo_path_finding(map_name):
    """
    @brief Демонстрирует поиск пути с учетом типов местности.
    
    @param map_name Имя карты для демонстрации.
    """
    print("Демонстрация поиска пути с учетом типов местности")
    print("=" * 50)
    
    # Получаем карту по имени
    map_grid = get_map_by_name(map_name)
    
    # Создаем объекты для поиска пути и визуализации
    maze = TerrainMaze(grid=map_grid)
    pathfinder = TerrainPathFinder(maze)
    visualizer = TerrainVisualizer(maze)
    
    # Отображаем карту
    print(f"Исходная карта ({map_name}) с различными типами местности:")
    visualizer.display_maze()
    
    # Ищем путь с учетом стоимости перемещения
    path = pathfinder.dijkstra()
    
    if path:
        # Выводим информацию о найденном пути
        print(f"Найден путь длиной {len(path)} ячеек")
        
        # Вычисляем и выводим стоимость пути
        path_cost = pathfinder.get_path_cost(path)
        print(f"Общая стоимость пути: {path_cost}")
        
        # Получаем и выводим список направлений и стоимостей
        directions = pathfinder.get_path_directions_with_costs(path)
        
        print("Пошаговые инструкции:")
        for i, (direction, cost) in enumerate(directions):
            print(f"Шаг {i+1}: {direction} (стоимость: {cost})")
            
        # Отображаем путь на карте
        visualizer.display_path(path)
    else:
        print("Путь не найден!")
        
        # Отправляем отчет об ошибке
        error_context = ErrorContext.current()
        error_api = ErrorAPI()
        error_api.report_error(
            "Путь не найден",
            f"Не удалось найти путь на карте {map_name}",
            error_context
        )

def demo_gathering_point(map_name):
    """
    @brief Демонстрирует поиск оптимальной точки сбора для команды героев.
    
    @param map_name Имя карты для демонстрации.
    """
    print("\nДемонстрация поиска оптимальной точки сбора")
    print("=" * 50)
    
    # Для демонстрации точки сбора используем карту с героями
    maze = TerrainMaze(grid=map_with_heroes())
    
    # Создаем объекты для поиска точки сбора и визуализации
    finder = TerrainEquidistantFinder(maze)
    visualizer = TerrainVisualizer(maze)
    
    # Отображаем карту с позициями героев
    print("Карта с позициями героев:")
    visualizer.display_gathering_point(HERO_POSITIONS, None, HERO_SPEEDS, 
                                     title="Позиции героев с разными скоростями")
    
    # Ищем оптимальную точку сбора с учетом скорости перемещения
    gathering_point = finder.find_optimal_gathering_point(HERO_POSITIONS, HERO_SPEEDS)
    
    if gathering_point:
        # Выводим информацию о найденной точке сбора
        print(f"Найдена оптимальная точка сбора: {gathering_point}")
        
        # Получаем время прибытия каждого героя
        arrival_times = finder.get_arrival_times(gathering_point, HERO_POSITIONS, HERO_SPEEDS)
        
        print("Время прибытия героев:")
        for i, time in enumerate(arrival_times):
            print(f"Герой {i+1} (скорость: {HERO_SPEEDS[i]}): {time:.2f} единиц времени")
            
        # Вычисляем максимальное время прибытия
        max_time = finder.get_max_arrival_time(gathering_point, HERO_POSITIONS, HERO_SPEEDS)
        print(f"Максимальное время прибытия: {max_time:.2f} единиц времени")
        
        # Отображаем точку сбора на карте
        visualizer.display_gathering_point(HERO_POSITIONS, gathering_point, HERO_SPEEDS, 
                                          title="Оптимальная точка сбора")
        
        # Находим пути для каждого героя к точке сбора
        paths = []
        pathfinder = TerrainPathFinder(maze)
        
        for pos in HERO_POSITIONS:
            # Устанавливаем текущую позицию героя как начальную точку
            maze.set_start_position(pos)
            # Устанавливаем точку сбора как конечную точку
            maze.set_end_position(gathering_point)
            # Ищем путь
            path = pathfinder.dijkstra()
            paths.append(path)
            
        # Отображаем пути героев к точке сбора
        visualizer.display_paths_to_gathering_point(HERO_POSITIONS, gathering_point, 
                                                  paths, HERO_SPEEDS,
                                                  title="Пути героев к точке сбора")
    else:
        print("Оптимальная точка сбора не найдена!")
        
        # Отправляем отчет об ошибке
        error_context = ErrorContext.current()
        error_api = ErrorAPI()
        error_api.report_error(
            "Точка сбора не найдена",
            "Не удалось найти оптимальную точку сбора для команды героев",
            error_context
        )

def demo_comparison(map_name):
    """
    @brief Демонстрирует сравнение обычного BFS и алгоритма Дейкстры с учетом стоимости.
    
    @param map_name Имя карты для демонстрации.
    """
    print("\nСравнение алгоритмов BFS и Дейкстры")
    print("=" * 50)
    
    # Получаем карту по имени
    map_grid = get_map_by_name(map_name)
    
    # Создаем объекты для поиска пути и визуализации
    maze = TerrainMaze(grid=map_grid)
    pathfinder = TerrainPathFinder(maze)
    visualizer = TerrainVisualizer(maze)
    
    # Отображаем карту
    print(f"Исходная карта ({map_name}):")
    visualizer.display_maze()
    
    # Ищем путь с помощью BFS (без учета стоимости)
    bfs_path = pathfinder.bfs()
    
    if bfs_path:
        print(f"BFS нашел путь длиной {len(bfs_path)} ячеек")
        
        # Вычисляем и выводим стоимость пути, найденного BFS
        bfs_cost = pathfinder.get_path_cost(bfs_path)
        print(f"Стоимость пути, найденного BFS: {bfs_cost}")
        
        # Отображаем путь, найденный BFS
        visualizer.display_path(bfs_path, title="Путь, найденный BFS (без учета стоимости)")
    else:
        print("BFS не нашел путь!")
    
    # Ищем путь с помощью алгоритма Дейкстры (с учетом стоимости)
    dijkstra_path = pathfinder.dijkstra()
    
    if dijkstra_path:
        print(f"Дейкстра нашел путь длиной {len(dijkstra_path)} ячеек")
        
        # Вычисляем и выводим стоимость пути, найденного Дейкстрой
        dijkstra_cost = pathfinder.get_path_cost(dijkstra_path)
        print(f"Стоимость пути, найденного Дейкстрой: {dijkstra_cost}")
        
        # Отображаем путь, найденный Дейкстрой
        visualizer.display_path(dijkstra_path, title="Путь, найденный Дейкстрой (с учетом стоимости)")
    else:
        print("Дейкстра не нашел путь!")
    
    # Сравниваем результаты
    if bfs_path and dijkstra_path:
        if dijkstra_cost < bfs_cost:
            print(f"Дейкстра нашел путь с меньшей стоимостью: {dijkstra_cost} < {bfs_cost}")
        elif dijkstra_cost > bfs_cost:
            print(f"BFS случайно нашел путь с меньшей стоимостью: {bfs_cost} < {dijkstra_cost}")
        else:
            print(f"Оба алгоритма нашли пути с одинаковой стоимостью: {bfs_cost}")

def demo_error_reporting():
    """
    @brief Демонстрирует работу системы отчетов об ошибках.
    """
    print("\nДемонстрация системы отчетов об ошибках")
    print("=" * 50)
    
    # Создаем объект для отправки отчетов об ошибках
    error_api = ErrorAPI()
    
    # Демонстрируем отправку отчета об ошибке с контекстом
    try:
        # Генерируем исключение для демонстрации
        print("Генерируем исключение для демонстрации...")
        result = 1 / 0
    except Exception as e:
        # Создаем контекст ошибки из исключения
        error_context = ErrorContext.from_exception(e)
        
        # Выводим информацию о контексте ошибки
        print(f"Контекст ошибки: {error_context}")
        print(f"Модуль: {error_context.module}")
        print(f"Функция: {error_context.function}")
        print(f"Строка: {error_context.line}")
        print(f"Исключение: {type(e).__name__}: {e}")
        
        # Отправляем отчет об ошибке
        bug_id = error_api.report_error(
            "Демонстрация отчета об ошибке",
            f"Произошло исключение: {type(e).__name__}: {e}",
            error_context
        )
        
        if bug_id:
            print(f"Отчет об ошибке успешно отправлен. ID: {bug_id}")
            
            # Демонстрируем добавление комментария к отчету
            error_api.add_comment(
                bug_id,
                f"Дополнительная информация: ошибка произошла в {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            # Демонстрируем обновление статуса отчета
            error_api.update_bug_status(bug_id, "RESOLVED")
        else:
            print("Не удалось отправить отчет об ошибке.")

def demo_notification():
    """
    @brief Демонстрирует работу системы уведомлений.
    """
    print("\nДемонстрация системы уведомлений")
    print("=" * 50)
    
    # Создаем объект для отправки уведомлений
    notifier = TelegramNotifier()
    
    # Демонстрируем отправку различных типов уведомлений
    print("Отправляем информационное уведомление...")
    notifier.send_info_notification(
        "Демонстрация информационного уведомления",
        "Это демонстрационное информационное уведомление."
    )
    
    print("Отправляем уведомление о предупреждении...")
    notifier.send_warning_notification(
        "Демонстрация уведомления о предупреждении",
        "Это демонстрационное уведомление о предупреждении."
    )
    
    print("Отправляем уведомление об ошибке...")
    error_context = ErrorContext.current()
    notifier.send_error_notification(
        "Демонстрация уведомления об ошибке",
        "Это демонстрационное уведомление об ошибке.",
        error_context
    )
    
    print("Отправляем уведомление о деплое...")
    notifier.send_deployment_notification(
        "development",
        "success",
        "1.0.0"
    )

def main():
    """
    @brief Основная функция скрипта.
    """
    # Настраиваем парсер аргументов командной строки
    parser = setup_parser()
    args = parser.parse_args()
    
    # Устанавливаем окружение
    os.environ["PATHFINDER_ENV"] = args.env
    
    # Загружаем конфигурацию
    config = Config()
    
    # Настраиваем логирование
    logging.basicConfig(
        level=getattr(logging, config.get("log_level", "INFO")),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Выводим информацию о текущей конфигурации
    print(f"Текущее окружение: {config.get_environment().value}")
    print(f"Уровень логирования: {config.get('log_level')}")
    print(f"Визуализация: {'включена' if config.get('visualization_enabled') else 'отключена'}")
    print(f"Отчеты об ошибках: {'включены' if config.get('error_reporting.enabled') else 'отключены'}")
    print(f"Отправка отчетов в Bugzilla: {'включена' if config.get('error_reporting.report_to_bugzilla') else 'отключена'}")
    print(f"Отправка уведомлений: {'включена' if config.get('error_reporting.send_notifications') else 'отключена'}")
    print(f"Оптимизированные алгоритмы: {'включены' if config.get('performance.use_optimized_algorithms') else 'отключены'}")
    print(f"Кэширование результатов: {'включено' if config.get('performance.cache_results') else 'отключено'}")
    
    # Запускаем выбранную демонстрацию
    try:
        if args.demo == "path" or args.demo == "all":
            demo_path_finding(args.map)
            
        if args.demo == "gathering" or args.demo == "all":
            demo_gathering_point(args.map)
            
        if args.demo == "comparison" or args.demo == "all":
            demo_comparison(args.map)
            
        if args.demo == "error" or args.demo == "all":
            demo_error_reporting()
            
        if args.demo == "notification" or args.demo == "all":
            demo_notification()
    except Exception as e:
        # В случае ошибки выводим информацию и отправляем отчет
        print(f"Произошла ошибка: {type(e).__name__}: {e}")
        traceback.print_exc()
        
        # Создаем контекст ошибки из исключения
        error_context = ErrorContext.from_exception(e)
        
        # Отправляем отчет об ошибке
        error_api = ErrorAPI()
        error_api.report_error(
            f"Ошибка в демонстрационном скрипте: {type(e).__name__}",
            str(e),
            error_context
        )

if __name__ == "__main__":
    main() 