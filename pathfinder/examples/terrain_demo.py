"""
@file terrain_demo.py
@brief Демонстрационный скрипт для алгоритмов поиска пути с учетом типов местности.

@details
Этот скрипт демонстрирует работу алгоритмов поиска пути с учетом
различных типов местности и скоростей перемещения героев.
"""

import sys
import os

# Добавляем путь к исходному коду
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from terrain_maze import TerrainMaze
from terrain_pathfinder import TerrainPathFinder
from terrain_equidistant_finder import TerrainEquidistantFinder
from terrain_visualizer import TerrainVisualizer
from terrain_maps import (
    SMALL_TERRAIN_MAP, MEDIUM_TERRAIN_MAP, LARGE_TERRAIN_MAP, 
    CITY_TERRAIN_MAP, HEROES_MAP, HERO_POSITIONS, HERO_SPEEDS,
    map_with_heroes
)

def demo_path_finding():
    """
    @brief Демонстрирует поиск пути с учетом типов местности.
    """
    print("Демонстрация поиска пути с учетом типов местности")
    print("=" * 50)
    
    # Используем карту среднего размера для демонстрации
    maze = TerrainMaze(grid=MEDIUM_TERRAIN_MAP)
    
    # Создаем объекты для поиска пути и визуализации
    pathfinder = TerrainPathFinder(maze)
    visualizer = TerrainVisualizer(maze)
    
    # Отображаем карту
    print("Исходная карта с различными типами местности:")
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

def demo_gathering_point():
    """
    @brief Демонстрирует поиск оптимальной точки сбора для команды героев.
    """
    print("\nДемонстрация поиска оптимальной точки сбора")
    print("=" * 50)
    
    # Используем карту с героями
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

def demo_comparison():
    """
    @brief Демонстрирует сравнение обычного BFS и алгоритма Дейкстры с учетом стоимости.
    """
    print("\nСравнение алгоритмов BFS и Дейкстры")
    print("=" * 50)
    
    # Используем небольшую карту для наглядности
    maze = TerrainMaze(grid=SMALL_TERRAIN_MAP)
    
    # Создаем объект для поиска пути
    pathfinder = TerrainPathFinder(maze)
    visualizer = TerrainVisualizer(maze)
    
    # Отображаем карту
    print("Исходная карта:")
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

if __name__ == "__main__":
    # Запускаем все демонстрации
    demo_path_finding()
    demo_gathering_point()
    demo_comparison() 