"""
Тесты для класса EquidistantFinder.
"""

import sys
import os
import unittest

# Добавляем путь к исходному коду
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from maze import Maze
from equidistant_finder import EquidistantFinder


class TestEquidistantFinder(unittest.TestCase):
    """Тесты для класса EquidistantFinder."""
    
    def test_calculate_distances(self):
        """Тест расчета расстояний."""
        # Создаем простой лабиринт
        grid = [
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 0]
        ]
        maze = Maze(grid)
        finder = EquidistantFinder(maze)
        
        # Проверяем расстояния от верхнего левого угла
        distances = finder.calculate_distances((0, 0))
        
        # Проверяем, что все доступные клетки имеют расстояния
        self.assertEqual(distances[(0, 0)], 0)  # Начальная точка
        self.assertEqual(distances[(0, 1)], 1)  # Вправо от начала
        self.assertEqual(distances[(0, 2)], 2)  # Два шага вправо
        self.assertEqual(distances[(1, 0)], 1)  # Вниз от начала
        self.assertEqual(distances[(2, 0)], 2)  # Два шага вниз
        self.assertEqual(distances[(2, 1)], 3)  # Вниз и вправо
        self.assertEqual(distances[(2, 2)], 4)  # Вниз и вправо и вправо
        
        # Проверяем, что стена не доступна
        self.assertNotIn((1, 1), distances)
        
        # Проверяем с None
        self.assertEqual(finder.calculate_distances(None), {})
    
    def test_find_equidistant_point_simple(self):
        """Тест поиска равноудаленной точки в простом случае."""
        # Создаем лабиринт с двумя героями на противоположных концах
        grid = [
            ['1', 0, 0, 0, '2'],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]
        maze = Maze(grid)
        finder = EquidistantFinder(maze)
        
        # Находим равноудаленную точку
        result = finder.find_equidistant_point()
        
        # Проверяем результат
        self.assertIsNotNone(result)
        point, distance = result
        
        # Ожидаемая равноудаленная точка - середина между героями
        self.assertEqual(point, (0, 2))
        self.assertEqual(distance, 2)
    
    def test_find_equidistant_point_with_wall(self):
        """Тест поиска равноудаленной точки с препятствием."""
        # Создаем лабиринт с двумя героями и стеной между ними
        grid = [
            ['1', 0, 1, 0, '2'],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0]
        ]
        maze = Maze(grid)
        finder = EquidistantFinder(maze)
        
        # Находим равноудаленную точку
        result = finder.find_equidistant_point()
        
        # Проверяем результат
        self.assertIsNotNone(result)
        point, distance = result
        
        # Равноудаленная точка должна быть ниже стены
        self.assertEqual(point[0], 2)  # В третьей строке
    
    def test_find_equidistant_point_three_heroes(self):
        """Тест поиска равноудаленной точки для трех героев."""
        # Создаем лабиринт с тремя героями
        grid = [
            ['1', 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, '2'],
            [0, 0, 0, 0, 0],
            ['3', 0, 0, 0, 0]
        ]
        maze = Maze(grid)
        finder = EquidistantFinder(maze)
        
        # Находим равноудаленную точку
        result = finder.find_equidistant_point()
        
        # Проверяем результат
        self.assertIsNotNone(result)
    
    def test_find_equidistant_point_no_heroes(self):
        """Тест поиска равноудаленной точки без героев."""
        # Создаем лабиринт без героев
        grid = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        maze = Maze(grid)
        finder = EquidistantFinder(maze)
        
        # Находим равноудаленную точку
        result = finder.find_equidistant_point()
        
        # Проверяем результат
        self.assertIsNone(result)
    
    def test_find_equidistant_point_one_hero(self):
        """Тест поиска равноудаленной точки с одним героем."""
        # Создаем лабиринт с одним героем
        grid = [
            ['1', 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        maze = Maze(grid)
        finder = EquidistantFinder(maze)
        
        # Находим равноудаленную точку
        result = finder.find_equidistant_point()
        
        # Проверяем результат
        self.assertIsNone(result)
    
    def test_get_paths_to_equidistant_point(self):
        """Тест получения путей до равноудаленной точки."""
        # Создаем лабиринт с двумя героями
        grid = [
            ['1', 0, 0, 0, '2'],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]
        maze = Maze(grid)
        finder = EquidistantFinder(maze)
        
        # Находим равноудаленную точку
        result = finder.find_equidistant_point()
        self.assertIsNotNone(result)
        point, _ = result
        
        # Получаем пути
        paths = finder.get_paths_to_equidistant_point(point)
        
        # Проверяем, что есть пути для обоих героев
        self.assertIn('1', paths)
        self.assertIn('2', paths)
        
        # Проверяем длины путей
        self.assertEqual(len(paths['1']), 3)  # Начало + 2 шага
        self.assertEqual(len(paths['2']), 3)  # Начало + 2 шага
    
    def test_get_variance_of_distances(self):
        """Тест расчета дисперсии расстояний."""
        # Создаем лабиринт с двумя героями
        grid = [
            ['1', 0, 0, 0, '2'],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]
        maze = Maze(grid)
        finder = EquidistantFinder(maze)
        
        # Равноудаленная точка
        equidistant_point = (0, 2)
        
        # Вычисляем дисперсию
        variance = finder.get_variance_of_distances(equidistant_point)
        
        # Проверяем, что дисперсия близка к нулю (точка равноудалена)
        self.assertAlmostEqual(variance, 0.0)
        
        # Не равноудаленная точка
        non_equidistant_point = (0, 1)
        
        # Вычисляем дисперсию
        variance = finder.get_variance_of_distances(non_equidistant_point)
        
        # Проверяем, что дисперсия больше нуля
        self.assertGreater(variance, 0.0)


if __name__ == '__main__':
    unittest.main() 