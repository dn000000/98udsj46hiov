"""
Тесты для класса PathFinder.
"""

import sys
import os
import unittest

# Добавляем путь к исходному коду
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from maze import Maze
from pathfinder import PathFinder


class TestPathFinder(unittest.TestCase):
    """Тесты для класса PathFinder."""
    
    def test_bfs_default_maze(self):
        """Тест BFS на лабиринте по умолчанию."""
        maze = Maze()
        finder = PathFinder(maze)
        path = finder.bfs()
        
        # Проверяем, что путь найден
        self.assertIsNotNone(path)
        self.assertGreater(len(path), 1)
        
        # Проверяем, что первая точка - стартовая, а последняя - конечная
        self.assertEqual(path[0], maze.get_start_position())
        self.assertEqual(path[-1], maze.get_end_position())
    
    def test_bfs_no_path(self):
        """Тест BFS на лабиринте без пути."""
        # Создаем лабиринт без пути
        grid = [
            ['1', 1, 1],
            [1, 'F', 1],
            [1, 1, 1]
        ]
        maze = Maze(grid)
        finder = PathFinder(maze)
        path = finder.bfs()
        
        # Проверяем, что путь не найден
        self.assertIsNone(path)
    
    def test_bfs_simple_path(self):
        """Тест BFS на простом лабиринте с прямым путем."""
        # Создаем простой лабиринт с прямым путем
        grid = [
            ['1', 0, 'F'],
            [1, 1, 1],
            [1, 1, 1]
        ]
        maze = Maze(grid)
        finder = PathFinder(maze)
        path = finder.bfs()
        
        # Проверяем путь
        self.assertIsNotNone(path)
        self.assertEqual(len(path), 3)  # Старт -> промежуточная -> финиш
        self.assertEqual(path, [(0, 0), (0, 1), (0, 2)])
    
    def test_get_path_directions(self):
        """Тест получения направлений для пути."""
        # Создаем простой путь
        path = [(0, 0), (0, 1), (1, 1), (1, 2)]
        
        maze = Maze()
        finder = PathFinder(maze)
        directions = finder.get_path_directions(path)
        
        # Проверяем направления
        self.assertEqual(directions, ['вправо', 'вниз', 'вправо'])
    
    def test_get_path_directions_empty(self):
        """Тест получения направлений для пустого пути."""
        maze = Maze()
        finder = PathFinder(maze)
        
        # Пустой путь
        directions = finder.get_path_directions([])
        self.assertEqual(directions, [])
        
        # Путь из одной точки
        directions = finder.get_path_directions([(0, 0)])
        self.assertEqual(directions, [])


if __name__ == '__main__':
    unittest.main() 