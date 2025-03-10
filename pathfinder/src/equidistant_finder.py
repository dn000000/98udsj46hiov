"""
Модуль для поиска равноудаленной точки.

Этот модуль содержит алгоритмы для поиска точки, 
равноудаленной от всех героев в лабиринте.
"""

from collections import deque
import numpy as np


class EquidistantFinder:
    """
    Класс для поиска точки, равноудаленной от всех героев.
    """
    
    def __init__(self, maze):
        """
        Инициализация объекта EquidistantFinder.
        
        Args:
            maze: Объект Maze, представляющий лабиринт.
        """
        self.maze = maze
    
    def calculate_distances(self, start_pos):
        """
        Вычисляет расстояния от начальной позиции до всех доступных точек.
        
        Использует алгоритм BFS для нахождения кратчайших путей.
        
        Args:
            start_pos (tuple): Начальная позиция (row, col).
            
        Returns:
            dict: Словарь расстояний {position: distance}.
        """
        if start_pos is None:
            return {}
        
        # Инициализация очереди и посещенных вершин
        queue = deque([(start_pos, 0)])  # (позиция, расстояние)
        distances = {start_pos: 0}
        
        while queue:
            pos, dist = queue.popleft()
            
            # Для каждого соседа
            for neighbor in self.maze.get_neighbors(pos):
                if neighbor not in distances:
                    distances[neighbor] = dist + 1
                    queue.append((neighbor, dist + 1))
        
        return distances
    
    def find_equidistant_point(self):
        """
        Находит точку, равноудаленную от всех героев.
        
        Returns:
            tuple or None: Кортеж (position, distance) или None, если точка не найдена.
                position - это кортеж (row, col), представляющий равноудаленную точку.
                distance - это расстояние от этой точки до каждого героя.
        """
        # Получаем позиции всех героев
        heroes = self.maze.get_hero_positions()
        
        if len(heroes) < 2:
            return None  # Нужно как минимум два героя
        
        # Вычисляем расстояния от каждого героя до всех точек
        hero_distances = {}
        for hero_id, pos in heroes.items():
            hero_distances[hero_id] = self.calculate_distances(pos)
        
        # Получаем все допустимые позиции
        valid_positions = self.maze.get_all_valid_positions()
        
        # Для каждой позиции проверяем, равноудалена ли она от всех героев
        best_point = None
        min_max_distance = float('inf')
        
        for pos in valid_positions:
            # Исключаем позиции героев
            if pos in heroes.values():
                continue
            
            # Проверяем, достижима ли эта позиция от всех героев
            distances = []
            reachable_from_all = True
            
            for hero_id in heroes:
                if pos not in hero_distances[hero_id]:
                    reachable_from_all = False
                    break
                distances.append(hero_distances[hero_id][pos])
            
            if not reachable_from_all:
                continue
            
            # Проверяем равноудаленность
            min_dist = min(distances)
            max_dist = max(distances)
            
            # Если точка абсолютно равноудалена
            if min_dist == max_dist and max_dist < min_max_distance:
                min_max_distance = max_dist
                best_point = pos
            # Если точка не абсолютно равноудалена, но лучше текущей
            elif max_dist < min_max_distance:
                min_max_distance = max_dist
                best_point = pos
        
        if best_point is not None:
            return (best_point, min_max_distance)
        
        return None
    
    def get_paths_to_equidistant_point(self, equidistant_point):
        """
        Получает пути от всех героев до равноудаленной точки.
        
        Args:
            equidistant_point (tuple): Равноудаленная точка (row, col).
            
        Returns:
            dict: Словарь путей {hero_id: path}.
        """
        heroes = self.maze.get_hero_positions()
        paths = {}
        
        for hero_id, pos in heroes.items():
            path = self._find_path(pos, equidistant_point)
            paths[hero_id] = path
        
        return paths
    
    def _find_path(self, start, end):
        """
        Находит путь от start до end с помощью BFS.
        
        Args:
            start (tuple): Начальная позиция (row, col).
            end (tuple): Конечная позиция (row, col).
            
        Returns:
            list or None: Список позиций, представляющий путь, или None, если путь не найден.
        """
        queue = deque([start])
        visited = {start: None}
        
        while queue:
            current = queue.popleft()
            
            if current == end:
                # Восстанавливаем путь
                path = []
                while current is not None:
                    path.append(current)
                    current = visited[current]
                return path[::-1]
            
            for neighbor in self.maze.get_neighbors(current):
                if neighbor not in visited:
                    queue.append(neighbor)
                    visited[neighbor] = current
        
        return None
    
    def get_variance_of_distances(self, point):
        """
        Вычисляет дисперсию расстояний от точки до всех героев.
        
        Args:
            point (tuple): Точка (row, col).
            
        Returns:
            float: Дисперсия расстояний.
        """
        heroes = self.maze.get_hero_positions()
        distances = []
        
        for hero_id, pos in heroes.items():
            path = self._find_path(pos, point)
            if path:
                distances.append(len(path) - 1)  # Вычитаем 1, так как путь включает начальную точку
        
        if not distances:
            return float('inf')
        
        return np.var(distances) 