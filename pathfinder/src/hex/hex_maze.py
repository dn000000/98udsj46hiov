"""
@file hex_maze.py
@brief Модуль для работы с гексагональным лабиринтом.

@details
Этот модуль содержит класс HexMaze, представляющий лабиринт на гексагональной
сетке с различными типами местности.
"""

from typing import List, Dict, Tuple, Set, Optional, Any
import random
import os
import numpy as np

from .hex_coordinate import HexCoordinate
from .hex_terrain_type import HexTerrainType


class HexMaze:
    """
    @brief Класс для представления гексагонального лабиринта.
    
    @details
    Лабиринт представлен словарем, где ключами являются объекты HexCoordinate,
    а значениями - типы местности (HexTerrainType).
    """
    
    def __init__(self, grid=None, width=20, height=20):
        """
        @brief Инициализирует гексагональный лабиринт.
        
        @param grid: Список строк, представляющих лабиринт (если None, создается случайный)
        @param width: Ширина лабиринта (используется только если grid=None)
        @param height: Высота лабиринта (используется только если grid=None)
        """
        self.terrain = {}  # Словарь координат и типов местности
        self.width = width
        self.height = height
        self.start_position = None
        self.end_position = None
        self.hero_positions = []
        
        if grid is not None:
            self._parse_grid(grid)
        else:
            self._generate_random_maze(width, height)
    
    def _parse_grid(self, grid: List[str]):
        """
        @brief Разбирает представление лабиринта в виде списка строк.
        
        @details
        Каждая строка представляет ряд гексов. Четные строки смещены вправо.
        
        @param grid: Список строк, представляющих лабиринт
        """
        self.height = len(grid)
        self.width = max(len(row) for row in grid)
        
        for row in range(self.height):
            for col in range(len(grid[row])):
                # Преобразуем смещенные координаты в гексагональные
                hex_coord = HexCoordinate.from_offset(col, row)
                symbol = grid[row][col]
                
                # Определяем тип местности по символу
                terrain_type = HexTerrainType.from_symbol(symbol)
                self.terrain[hex_coord] = terrain_type
                
                # Запоминаем особые точки
                if terrain_type == HexTerrainType.START:
                    self.start_position = hex_coord
                    self.hero_positions.append(hex_coord)
                elif terrain_type == HexTerrainType.END:
                    self.end_position = hex_coord
                # Здесь можно добавить обработку других героев (2-9)
                elif symbol in "23456789":
                    # Считаем остальные цифры героями
                    self.hero_positions.append(hex_coord)
                    # Сохраняем как проходимую местность (равнина)
                    self.terrain[hex_coord] = HexTerrainType.GRASS
    
    def _generate_random_maze(self, width: int, height: int):
        """
        @brief Генерирует случайный гексагональный лабиринт.
        
        @param width: Ширина лабиринта в гексах
        @param height: Высота лабиринта в гексах
        """
        # Возможные типы местности для случайной генерации
        terrain_types = [
            HexTerrainType.ROAD, 
            HexTerrainType.GRASS, 
            HexTerrainType.FOREST,
            HexTerrainType.HILLS, 
            HexTerrainType.WATER, 
            HexTerrainType.SWAMP,
            HexTerrainType.DESERT
        ]
        
        # Вероятности для разных типов местности
        terrain_probs = {
            HexTerrainType.ROAD: 0.08,    # Дороги редки
            HexTerrainType.GRASS: 0.45,   # Основной тип местности
            HexTerrainType.FOREST: 0.15,  # Довольно много леса
            HexTerrainType.HILLS: 0.10,   # Холмы не так часто
            HexTerrainType.WATER: 0.10,   # Вода не так часто
            HexTerrainType.SWAMP: 0.07,   # Болота редки
            HexTerrainType.DESERT: 0.05   # Пустыни очень редки
        }
        
        # Создаем карту с указанными размерами
        for row in range(height):
            for col in range(width):
                # Преобразуем смещенные координаты в гексагональные
                hex_coord = HexCoordinate.from_offset(col, row)
                
                # Граница всегда стена
                if row == 0 or row == height - 1 or col == 0 or col == width - 1:
                    self.terrain[hex_coord] = HexTerrainType.WALL
                else:
                    # Выбираем случайный тип местности с учетом вероятностей
                    r = random.random()
                    cumulative_prob = 0
                    selected_terrain = HexTerrainType.GRASS  # По умолчанию
                    
                    for terrain, prob in terrain_probs.items():
                        cumulative_prob += prob
                        if r <= cumulative_prob:
                            selected_terrain = terrain
                            break
                    
                    self.terrain[hex_coord] = selected_terrain
        
        # Создаем проход в лабиринте, чтобы было гарантированно проходимо
        self._ensure_path()
        
        # Устанавливаем стартовую и конечную позиции
        valid_positions = [pos for pos, terrain in self.terrain.items() 
                         if HexTerrainType.is_passable(terrain)]
        
        if valid_positions:
            # Стартовая позиция в верхнем левом углу (ближе к началу)
            start_candidates = sorted(valid_positions, 
                                     key=lambda pos: pos.to_offset()[0] + pos.to_offset()[1])
            self.start_position = start_candidates[0]
            self.terrain[self.start_position] = HexTerrainType.START
            
            # Конечная позиция в нижнем правом углу (ближе к концу)
            end_candidates = sorted(valid_positions, 
                                   key=lambda pos: -(pos.to_offset()[0] + pos.to_offset()[1]))
            self.end_position = end_candidates[0]
            self.terrain[self.end_position] = HexTerrainType.END
            
            # Добавляем стартовую позицию в список героев
            self.hero_positions = [self.start_position]
    
    def _ensure_path(self):
        """
        @brief Гарантирует наличие проходимого пути в лабиринте.
        
        @details
        Создает случайный путь через лабиринт, делая клетки на пути проходимыми.
        """
        # Выбираем случайные начальную и конечную позиции
        start_row, start_col = 1, 1
        end_row, end_col = self.height - 2, self.width - 2
        
        start_hex = HexCoordinate.from_offset(start_col, start_row)
        end_hex = HexCoordinate.from_offset(end_col, end_row)
        
        # Создаем путь от начала до конца
        path = HexCoordinate.line(start_hex, end_hex)
        
        # Делаем все клетки на пути проходимыми (трава)
        for hex_coord in path:
            self.terrain[hex_coord] = HexTerrainType.GRASS
        
        # Добавляем немного случайности в путь
        for i in range(min(10, self.width // 2)):
            # Выбираем случайную точку на пути
            hex_coord = random.choice(path)
            
            # Создаем случайный отрезок пути от этой точки
            random_direction = random.randint(0, 5)
            random_length = random.randint(3, 5)
            
            current = hex_coord
            for _ in range(random_length):
                current = current.neighbor(random_direction)
                if 0 < current.to_offset()[0] < self.width - 1 and 0 < current.to_offset()[1] < self.height - 1:
                    self.terrain[current] = HexTerrainType.GRASS
    
    def is_valid_position(self, position: HexCoordinate) -> bool:
        """
        @brief Проверяет, является ли позиция допустимой.
        
        @param position: Проверяемая позиция
        @return True, если позиция находится в пределах лабиринта
        """
        return position in self.terrain
    
    def is_passable(self, position: HexCoordinate) -> bool:
        """
        @brief Проверяет, является ли позиция проходимой.
        
        @param position: Проверяемая позиция
        @return True, если позиция проходима
        """
        if not self.is_valid_position(position):
            return False
        
        terrain = self.terrain.get(position)
        return HexTerrainType.is_passable(terrain)
    
    def get_terrain_type(self, position: HexCoordinate) -> HexTerrainType:
        """
        @brief Возвращает тип местности в указанной позиции.
        
        @param position: Позиция в лабиринте
        @return Тип местности в указанной позиции
        """
        return self.terrain.get(position)
    
    def get_terrain_cost(self, position: HexCoordinate) -> float:
        """
        @brief Возвращает стоимость прохода через указанную позицию.
        
        @param position: Позиция в лабиринте
        @return Стоимость прохода
        """
        terrain = self.get_terrain_type(position)
        return HexTerrainType.get_cost(terrain)
    
    def get_terrain_info(self, position: HexCoordinate) -> Tuple[HexTerrainType, str, float]:
        """
        @brief Возвращает информацию о местности в указанной позиции.
        
        @param position: Позиция в лабиринте
        @return Кортеж (тип местности, название, стоимость)
        """
        terrain = self.get_terrain_type(position)
        name = HexTerrainType.get_name(terrain)
        cost = HexTerrainType.get_cost(terrain)
        return terrain, name, cost
    
    def get_neighbors(self, position: HexCoordinate) -> List[HexCoordinate]:
        """
        @brief Возвращает список соседних проходимых позиций.
        
        @param position: Позиция в лабиринте
        @return Список соседних проходимых позиций
        """
        neighbors = []
        
        for i in range(6):  # 6 направлений в гексагональной сетке
            neighbor = position.neighbor(i)
            if self.is_valid_position(neighbor) and self.is_passable(neighbor):
                neighbors.append(neighbor)
        
        return neighbors
    
    def get_start_position(self) -> HexCoordinate:
        """
        @brief Возвращает начальную позицию.
        
        @return Координата начальной позиции
        """
        return self.start_position
    
    def get_end_position(self) -> HexCoordinate:
        """
        @brief Возвращает конечную позицию.
        
        @return Координата конечной позиции
        """
        return self.end_position
    
    def get_hero_positions(self) -> List[HexCoordinate]:
        """
        @brief Возвращает список позиций героев.
        
        @return Список координат героев
        """
        return self.hero_positions
    
    def get_all_valid_positions(self) -> List[HexCoordinate]:
        """
        @brief Возвращает список всех допустимых позиций в лабиринте.
        
        @return Список всех допустимых позиций
        """
        return list(self.terrain.keys())
    
    def get_all_passable_positions(self) -> List[HexCoordinate]:
        """
        @brief Возвращает список всех проходимых позиций в лабиринте.
        
        @return Список всех проходимых позиций
        """
        return [pos for pos in self.terrain.keys() if self.is_passable(pos)]
    
    def __str__(self) -> str:
        """
        @brief Возвращает строковое представление лабиринта.
        
        @return Строковое представление лабиринта
        """
        if not self.terrain:
            return "Пустой лабиринт"
        
        min_col = min(pos.to_offset()[0] for pos in self.terrain.keys())
        max_col = max(pos.to_offset()[0] for pos in self.terrain.keys())
        min_row = min(pos.to_offset()[1] for pos in self.terrain.keys())
        max_row = max(pos.to_offset()[1] for pos in self.terrain.keys())
        
        result = []
        for row in range(min_row, max_row + 1):
            # Добавляем отступ для нечетных строк (odd-r смещение)
            if row % 2 == 1:
                line = " "
            else:
                line = ""
            
            for col in range(min_col, max_col + 1):
                hex_coord = HexCoordinate.from_offset(col, row)
                terrain = self.terrain.get(hex_coord)
                
                if terrain is None:
                    line += " "
                else:
                    line += terrain.value
            
            result.append(line)
        
        return "\n".join(result)
    
    def to_grid(self) -> List[str]:
        """
        @brief Возвращает представление лабиринта в виде списка строк.
        
        @return Список строк, представляющих лабиринт
        """
        if not self.terrain:
            return []
        
        min_col = min(pos.to_offset()[0] for pos in self.terrain.keys())
        max_col = max(pos.to_offset()[0] for pos in self.terrain.keys())
        min_row = min(pos.to_offset()[1] for pos in self.terrain.keys())
        max_row = max(pos.to_offset()[1] for pos in self.terrain.keys())
        
        result = []
        for row in range(min_row, max_row + 1):
            line = ""
            for col in range(min_col, max_col + 1):
                hex_coord = HexCoordinate.from_offset(col, row)
                terrain = self.terrain.get(hex_coord)
                
                if terrain is None:
                    line += " "
                else:
                    line += terrain.value
            
            result.append(line)
        
        return result 