"""
@file simple_terrain_demo.py
@brief Упрощенная демонстрация поиска пути с учетом типов местности.

@details
Этот скрипт демонстрирует простую работу алгоритмов поиска пути через
различные типы местности.
"""

import sys
import os

# Добавляем путь к исходному коду
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from terrain_maze import TerrainMaze
from terrain_pathfinder import TerrainPathFinder

def create_simple_terrain_map():
    """
    Создает простую карту с разными типами местности
    """
    # Создаем простую карту для демонстрации
    # 'R' - дорога (стоимость: 0.5)
    # 'G' - трава (стоимость: 1.0)
    # 'F' - лес (стоимость: 3.0)
    # 'H' - холмы (стоимость: 4.0)
    # 'S' - болото (стоимость: 5.0)
    # 'W' - вода (непроходимо)
    # 'M' - горы (непроходимо)
    # '#' - стена (непроходимо)
    # '1' - начальная точка (герой 1)
    # 'E' - конечная точка (финиш)
    # Примечание: 'F' используется как для леса, так и для финиша,
    # поэтому используем 'E' для финиша в этой демонстрации
    
    simple_map = [
        ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
        ['#', '1', 'R', 'R', 'R', 'R', 'G', 'G', 'G', 'R', 'R', 'R', '#'],
        ['#', 'R', '#', '#', '#', '#', '#', 'R', '#', '#', '#', '#', '#'],
        ['#', 'R', 'F', 'G', 'G', 'R', 'W', 'R', 'R', 'R', 'F', 'F', '#'],
        ['#', 'R', '#', '#', '#', '#', 'R', '#', '#', '#', '#', '#', '#'],
        ['#', 'R', 'F', 'G', 'G', 'G', 'G', 'G', 'R', 'H', 'R', 'E', '#'],
        ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#']
    ]
    
    return simple_map

def main():
    """
    Основная функция демонстрации
    """
    # Создаем простую карту местности
    terrain_map = create_simple_terrain_map()
    
    # Создаем лабиринт на основе карты
    maze = TerrainMaze(grid=terrain_map)
    
    # Выводим лабиринт
    print("\nИсходный лабиринт с различными типами местности:")
    print(maze)
    
    # Создаем объект поиска пути
    pathfinder = TerrainPathFinder(maze)
    
    # Ищем путь с помощью алгоритма Дейкстры
    path = pathfinder.dijkstra()
    
    # Выводим результаты
    if path:
        print("\nНайден оптимальный путь:")
        path_with_costs = pathfinder.get_path_directions_with_costs(path)
        
        total_cost = 0
        step_number = 1
        for direction, cost in path_with_costs:
            total_cost += cost
            print(f"Шаг {step_number}: {direction}, стоимость: {cost}")
            step_number += 1
        
        print(f"\nОбщая стоимость пути: {total_cost}")
        print(f"Количество шагов: {len(path) - 1}")
    else:
        print("\nПуть не найден!")

if __name__ == "__main__":
    main() 