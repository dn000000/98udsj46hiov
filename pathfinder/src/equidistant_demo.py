"""
Демонстрационный скрипт для поиска равноудаленной точки.

Этот скрипт демонстрирует функциональность поиска точки,
равноудаленной от всех героев.
"""

import os
import matplotlib.pyplot as plt

from maze import Maze
from equidistant_finder import EquidistantFinder
from visualizer import MazeVisualizer


def main():
    """
    Основная функция демонстрации.
    """
    # Создаем лабиринт с несколькими героями
    grid = [
        ['1', 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 0, 1, 1, 1, 0],
        [0, 0, 1, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 1, 0, 1, 1, 1, 0, 1, 0],
        [0, 0, 1, 0, 1, '3', 1, 0, 1, 0],
        [0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 1, 1, 1, 0, 1, 0],
        [0, 1, 0, 0, 1, '2', 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]
    
    maze = Maze(grid)
    print("Лабиринт с несколькими героями:")
    print(maze)
    
    # Создаем объект EquidistantFinder
    finder = EquidistantFinder(maze)
    
    # Находим равноудаленную точку
    result = finder.find_equidistant_point()
    
    if result:
        equidistant_point, distance = result
        print(f"Найдена равноудаленная точка: {equidistant_point} с расстоянием {distance}")
        
        # Получаем пути от всех героев до равноудаленной точки
        paths = finder.get_paths_to_equidistant_point(equidistant_point)
        
        # Выводим информацию о путях
        heroes = maze.get_hero_positions()
        print("\nПути от героев до равноудаленной точки:")
        for hero_id, path in paths.items():
            print(f"Герой {hero_id} ({heroes[hero_id]}): Путь длиной {len(path) - 1} шагов")
        
        # Вычисляем дисперсию расстояний
        variance = finder.get_variance_of_distances(equidistant_point)
        print(f"\nДисперсия расстояний: {variance}")
        
        # Визуализируем
        visualizer = MazeVisualizer(maze)
        visualizer.draw_maze()
        visualizer.draw_equidistant_point(equidistant_point, paths)
        
        # Создаем папку visualization, если она не существует
        os.makedirs("../visualization", exist_ok=True)
        
        # Сохраняем изображение
        visualizer.save("../visualization/equidistant_point.png")
        print("\nВизуализация сохранена в файл visualization/equidistant_point.png")
        
        # Создаем тепловую карту расстояний для каждого героя
        print("\nСоздание тепловых карт расстояний...")
        
        for hero_id, pos in heroes.items():
            # Вычисляем расстояния от героя до всех точек
            distances = finder.calculate_distances(pos)
            
            # Создаем тепловую карту
            fig = visualizer.draw_distance_map(pos, distances)
            
            # Сохраняем тепловую карту
            filename = f"../visualization/distance_map_hero_{hero_id}.png"
            fig.savefig(filename)
            plt.close(fig)
            print(f"Тепловая карта для героя {hero_id} сохранена в файл {filename}")
        
        # Показываем изображение основного лабиринта
        visualizer.show()
    else:
        print("Равноудаленная точка не найдена!")


if __name__ == "__main__":
    main() 