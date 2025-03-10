"""
Тесты для класса Maze.
"""

import sys
import os
import unittest

# Добавляем путь к исходному коду
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from maze import Maze


class TestMaze(unittest.TestCase):
    """Тесты для класса Maze."""
    
    def test_default_maze(self):
        """Тест лабиринта по умолчанию."""
        maze = Maze()
        self.assertEqual(maze.height, 6)
        self.assertEqual(maze.width, 6)
        self.assertEqual(maze.get_start_position(), (0, 0))
        self.assertEqual(maze.get_end_position(), (4, 5))
    
    def test_custom_maze(self):
        """Тест пользовательского лабиринта."""
        grid = [
            ['1', 0, 1],
            [0, 0, 'F'],
            [1, 1, 1]
        ]
        maze = Maze(grid)
        self.assertEqual(maze.height, 3)
        self.assertEqual(maze.width, 3)
        self.assertEqual(maze.get_start_position(), (0, 0))
        self.assertEqual(maze.get_end_position(), (1, 2))
    
    def test_is_valid_position(self):
        """Тест проверки допустимой позиции."""
        maze = Maze()
        # Свободная клетка
        self.assertTrue(maze.is_valid_position((1, 1)))
        # Стена
        self.assertFalse(maze.is_valid_position((0, 2)))
        # За пределами лабиринта
        self.assertFalse(maze.is_valid_position((-1, 0)))
        self.assertFalse(maze.is_valid_position((6, 0)))
    
    def test_get_neighbors(self):
        """Тест получения соседних позиций."""
        maze = Maze()
        # Для точки (1, 1)
        neighbors = maze.get_neighbors((1, 1))
        self.assertIn((0, 1), neighbors)  # Верх
        # позиция (2, 1) - это стена, поэтому она не должна быть в списке соседей
        self.assertIn((1, 0), neighbors)  # Влево
        self.assertIn((1, 2), neighbors)  # Вправо
        self.assertEqual(len(neighbors), 3)  # Только три соседа, так как (2, 1) - стена
        
        # Для точки (0, 0) - старт
        neighbors = maze.get_neighbors((0, 0))
        self.assertIn((1, 0), neighbors)  # Низ
        self.assertIn((0, 1), neighbors)  # Вправо
        self.assertEqual(len(neighbors), 2)  # Два соседа: вниз и вправо
    
    def test_get_hero_positions(self):
        """Тест получения позиций героев."""
        # Создаем лабиринт с несколькими героями
        grid = [
            ['1', 0, 0],
            [0, '2', 0],
            [0, 0, '3']
        ]
        maze = Maze(grid)
        
        # Получаем позиции героев
        heroes = maze.get_hero_positions()
        
        # Проверяем, что все герои найдены
        self.assertEqual(len(heroes), 3)
        self.assertEqual(heroes['1'], (0, 0))
        self.assertEqual(heroes['2'], (1, 1))
        self.assertEqual(heroes['3'], (2, 2))
    
    def test_get_all_valid_positions(self):
        """Тест получения всех допустимых позиций."""
        # Создаем простой лабиринт
        grid = [
            [0, 1],
            [0, 0]
        ]
        maze = Maze(grid)
        
        # Получаем все допустимые позиции
        valid_positions = maze.get_all_valid_positions()
        
        # Проверяем, что все допустимые позиции найдены
        self.assertEqual(len(valid_positions), 3)
        self.assertIn((0, 0), valid_positions)
        self.assertIn((1, 0), valid_positions)
        self.assertIn((1, 1), valid_positions)
        self.assertNotIn((0, 1), valid_positions)  # Стена
    
    def test_str_representation(self):
        """Тест строкового представления лабиринта."""
        maze = Maze()
        string_repr = str(maze)
        self.assertIsInstance(string_repr, str)
        self.assertTrue(len(string_repr) > 0)


if __name__ == '__main__':
    unittest.main() 