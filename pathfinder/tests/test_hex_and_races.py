#!/usr/bin/env python
"""
@file test_hex_and_races.py
@brief Модульные тесты для гексагональной карты и расовых модификаторов.

@details
Тесты для проверки функциональности гексагональной карты, ячеек, рас
и алгоритма поиска пути с учетом расовых модификаторов.
"""

import sys
import os
import unittest

# Добавляем путь к пакету pathfinder в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.hex import HexMap, HexCell, HexTerrainType
from src.races import Human, Elf, Dwarf, Orc, Race
from src.pathfinding import find_path


class TestHexCell(unittest.TestCase):
    """
    Тесты для класса HexCell.
    """
    
    def test_initialization(self):
        """
        Проверяет инициализацию ячейки с заданными координатами и типом местности.
        """
        cell = HexCell(1, 2, HexTerrainType.GRASS)
        self.assertEqual(cell.q, 1)
        self.assertEqual(cell.r, 2)
        self.assertEqual(cell.s, -3)  # q + r + s = 0
        self.assertEqual(cell.terrain_type, HexTerrainType.GRASS)
    
    def test_equality(self):
        """
        Проверяет сравнение ячеек на равенство.
        """
        cell1 = HexCell(1, 2, HexTerrainType.GRASS)
        cell2 = HexCell(1, 2, HexTerrainType.FOREST)
        cell3 = HexCell(2, 1, HexTerrainType.GRASS)
        
        self.assertEqual(cell1, cell2)  # Равны, так как у них одинаковые координаты
        self.assertNotEqual(cell1, cell3)  # Не равны, так как у них разные координаты
    
    def test_hashing(self):
        """
        Проверяет хеширование ячеек.
        """
        cell1 = HexCell(1, 2, HexTerrainType.GRASS)
        cell2 = HexCell(1, 2, HexTerrainType.FOREST)
        cell3 = HexCell(2, 1, HexTerrainType.GRASS)
        
        # Ячейки с одинаковыми координатами имеют одинаковый хеш
        self.assertEqual(hash(cell1), hash(cell2))
        # Ячейки с разными координатами имеют разный хеш
        self.assertNotEqual(hash(cell1), hash(cell3))
    
    def test_distance(self):
        """
        Проверяет вычисление расстояния между ячейками.
        """
        cell1 = HexCell(0, 0, HexTerrainType.GRASS)
        cell2 = HexCell(1, 2, HexTerrainType.FOREST)
        cell3 = HexCell(3, 0, HexTerrainType.MOUNTAIN)
        
        self.assertEqual(cell1.distance(cell2), 3)  # max(|0-1|, |0-2|, |0-(-3)|) = 3
        self.assertEqual(cell2.distance(cell3), 2)  # max(|1-3|, |2-0|, |-3-(-3)|) = 2
        self.assertEqual(cell1.distance(cell3), 3)  # max(|0-3|, |0-0|, |0-(-3)|) = 3
    
    def test_get_neighbors(self):
        """
        Проверяет получение координат соседних ячеек.
        """
        cell = HexCell(1, 1, HexTerrainType.GRASS)
        neighbors = cell.get_neighbors()
        
        # Должно быть 6 соседей
        self.assertEqual(len(neighbors), 6)
        
        # Проверяем, что все 6 соседей имеют правильные координаты
        expected_neighbors = [(2, 1), (2, 0), (1, 0), (0, 1), (0, 2), (1, 2)]
        self.assertSetEqual(set(neighbors), set(expected_neighbors))


class TestHexMap(unittest.TestCase):
    """
    Тесты для класса HexMap.
    """
    
    def setUp(self):
        """
        Создает карту для тестирования.
        """
        self.map = HexMap()
        
        # Добавляем несколько ячеек с разными типами местности
        self.map.add_cell(0, 0, HexTerrainType.START)
        self.map.add_cell(0, 1, HexTerrainType.GRASS)
        self.map.add_cell(1, 0, HexTerrainType.FOREST)
        self.map.add_cell(1, 1, HexTerrainType.MOUNTAIN)
        self.map.add_cell(2, 0, HexTerrainType.END)
    
    def test_add_cell(self):
        """
        Проверяет добавление ячейки на карту.
        """
        # Добавляем новую ячейку
        cell = self.map.add_cell(2, 1, HexTerrainType.WATER)
        
        # Проверяем, что ячейка добавлена правильно
        self.assertEqual(cell.q, 2)
        self.assertEqual(cell.r, 1)
        self.assertEqual(cell.terrain_type, HexTerrainType.WATER)
        
        # Проверяем, что ячейка есть на карте
        self.assertIn((2, 1), self.map.cells)
    
    def test_get_cell(self):
        """
        Проверяет получение ячейки по координатам.
        """
        # Получаем существующую ячейку
        cell = self.map.get_cell(1, 0)
        self.assertIsNotNone(cell)
        self.assertEqual(cell.terrain_type, HexTerrainType.FOREST)
        
        # Пытаемся получить несуществующую ячейку
        cell = self.map.get_cell(10, 10)
        self.assertIsNone(cell)
    
    def test_get_neighbors(self):
        """
        Проверяет получение соседних ячеек.
        """
        # Получаем центральную ячейку
        cell = self.map.get_cell(0, 0)
        
        # Получаем соседей
        neighbors = self.map.get_neighbors(cell)
        
        # Должно быть 2 соседа (те, которые существуют на карте)
        self.assertEqual(len(neighbors), 2)
        
        # Проверяем, что соседи имеют правильные координаты
        coords = [(neighbor.q, neighbor.r) for neighbor in neighbors]
        expected_coords = [(0, 1), (1, 0)]
        self.assertSetEqual(set(coords), set(expected_coords))
    
    def test_start_end_points(self):
        """
        Проверяет правильность установки начальной и конечной точек.
        """
        # Проверяем начальную точку
        self.assertIsNotNone(self.map.start)
        self.assertEqual(self.map.start.q, 0)
        self.assertEqual(self.map.start.r, 0)
        
        # Проверяем конечную точку
        self.assertIsNotNone(self.map.end)
        self.assertEqual(self.map.end.q, 2)
        self.assertEqual(self.map.end.r, 0)


class TestRace(unittest.TestCase):
    """
    Тесты для классов рас.
    """
    
    def test_human_modifiers(self):
        """
        Проверяет модификаторы для расы Человек.
        """
        human = Human()
        
        # Проверяем несколько модификаторов
        self.assertEqual(human.get_movement_cost(HexTerrainType.ROAD), 0.5)  # Бонус на дорогах
        self.assertEqual(human.get_movement_cost(HexTerrainType.FOREST), 1.5)  # Штраф в лесах
        self.assertEqual(human.get_movement_cost(HexTerrainType.GRASS), 1.0)  # Обычная скорость на равнинах
        self.assertEqual(human.get_movement_cost(HexTerrainType.MOUNTAIN), float('inf'))  # Горы непроходимы
    
    def test_elf_modifiers(self):
        """
        Проверяет модификаторы для расы Эльф.
        """
        elf = Elf()
        
        # Проверяем несколько модификаторов
        self.assertEqual(elf.get_movement_cost(HexTerrainType.FOREST), 0.5)  # Бонус в лесах
        self.assertEqual(elf.get_movement_cost(HexTerrainType.GRASS), 0.7)  # Бонус на равнинах
        self.assertEqual(elf.get_movement_cost(HexTerrainType.CAVE), 1.5)  # Штраф в пещерах
        self.assertEqual(elf.get_movement_cost(HexTerrainType.WATER), float('inf'))  # Вода непроходима
    
    def test_dwarf_modifiers(self):
        """
        Проверяет модификаторы для расы Гном.
        """
        dwarf = Dwarf()
        
        # Проверяем несколько модификаторов
        self.assertEqual(dwarf.get_movement_cost(HexTerrainType.MOUNTAIN), 0.5)  # Бонус в горах
        self.assertEqual(dwarf.get_movement_cost(HexTerrainType.CAVE), 0.5)  # Бонус в пещерах
        self.assertEqual(dwarf.get_movement_cost(HexTerrainType.SWAMP), 1.5)  # Штраф в болотах
        self.assertEqual(dwarf.get_movement_cost(HexTerrainType.WATER), float('inf'))  # Вода непроходима
    
    def test_orc_modifiers(self):
        """
        Проверяет модификаторы для расы Орк.
        """
        orc = Orc()
        
        # Проверяем несколько модификаторов
        self.assertEqual(orc.get_movement_cost(HexTerrainType.DESERT), 0.7)  # Бонус в пустыне
        self.assertEqual(orc.get_movement_cost(HexTerrainType.HILLS), 0.7)  # Бонус на холмах
        self.assertEqual(orc.get_movement_cost(HexTerrainType.SNOW), 1.4)  # Штраф в снегу
        self.assertEqual(orc.get_movement_cost(HexTerrainType.LAVA), 2.0)  # Могут проходить через лаву с большим штрафом


class TestPathfinding(unittest.TestCase):
    """
    Тесты для алгоритма поиска пути.
    """
    
    def setUp(self):
        """
        Создает карту для тестирования поиска пути.
        """
        self.map = HexMap()
        
        # Создаем простую карту 3x3
        # S G F
        # G G M
        # F G E
        self.map.add_cell(0, 0, HexTerrainType.START)
        self.map.add_cell(0, 1, HexTerrainType.GRASS)
        self.map.add_cell(0, 2, HexTerrainType.FOREST)
        self.map.add_cell(1, 0, HexTerrainType.GRASS)
        self.map.add_cell(1, 1, HexTerrainType.GRASS)
        self.map.add_cell(1, 2, HexTerrainType.GRASS)
        self.map.add_cell(2, 0, HexTerrainType.FOREST)
        self.map.add_cell(2, 1, HexTerrainType.MOUNTAIN)
        self.map.add_cell(2, 2, HexTerrainType.END)
    
    def test_find_path(self):
        """
        Проверяет поиск пути для разных рас.
        """
        # Создаем разные расы
        human = Human()
        elf = Elf()
        
        # Находим путь для человека
        human_path, human_cost = self.map.find_path(self.map.start, self.map.end, human)
        
        # Проверяем, что путь найден
        self.assertIsNotNone(human_path)
        self.assertLess(human_cost, float('inf'))
        
        # Находим путь для эльфа
        elf_path, elf_cost = self.map.find_path(self.map.start, self.map.end, elf)
        
        # Проверяем, что путь найден
        self.assertIsNotNone(elf_path)
        self.assertLess(elf_cost, float('inf'))
        
        # Для эльфа стоимость должна быть меньше из-за бонуса в лесу и на равнинах
        self.assertLess(elf_cost, human_cost)
    
    def test_unreachable_path(self):
        """
        Проверяет, что путь через непроходимую местность не найден.
        """
        # Создаем карту с непроходимым препятствием
        map_with_obstacle = HexMap()
        map_with_obstacle.add_cell(0, 0, HexTerrainType.START)
        map_with_obstacle.add_cell(0, 1, HexTerrainType.WATER)
        map_with_obstacle.add_cell(0, 2, HexTerrainType.END)
        
        # Создаем расу
        human = Human()
        
        # Пытаемся найти путь
        path, cost = map_with_obstacle.find_path(map_with_obstacle.start, map_with_obstacle.end, human)
        
        # Путь не должен быть найден
        self.assertIsNone(path)
        self.assertEqual(cost, float('inf'))


if __name__ == "__main__":
    unittest.main() 