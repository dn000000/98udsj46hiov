"""
@file pathfinder.py
@brief Модуль для поиска пути в лабиринте.

@details
Этот модуль содержит алгоритмы для поиска пути в лабиринте,
включая поиск в ширину (BFS) и другие алгоритмы.

Основной класс PathFinder предоставляет функционал для:
- Поиска кратчайшего пути между двумя точками в лабиринте
- Получения последовательности шагов для прохождения пути
- Работы с различными типами лабиринтов

@author Разработчики проекта PathFinder
@version 1.0
@date 2025-03-10
"""

from collections import deque


class PathFinder:
    """
    @brief Класс для поиска пути в лабиринте.
    
    @details
    Класс реализует различные алгоритмы поиска пути в лабиринте,
    включая поиск в ширину (BFS) и вспомогательные функции для
    обработки найденного пути. Основной метод - bfs(), который
    находит кратчайший путь от стартовой до целевой точки.
    
    @see maze.Maze
    """
    
    def __init__(self, maze):
        """
        @brief Инициализация объекта PathFinder.
        
        @param maze Объект Maze, представляющий лабиринт.
        
        @code
        # Пример использования:
        from maze import Maze
        from pathfinder import PathFinder
        
        # Создаем лабиринт
        maze = Maze()
        
        # Создаем объект для поиска пути
        finder = PathFinder(maze)
        
        # Ищем путь
        path = finder.bfs()
        @endcode
        """
        self.maze = maze
    
    def bfs(self):
        """
        @brief Алгоритм поиска в ширину (Breadth-First Search).
        
        @details
        Реализует поиск кратчайшего пути от начальной точки до конечной точки
        в лабиринте с использованием алгоритма поиска в ширину (BFS).
        
        Пошаговый алгоритм:
        1. Начинаем с начальной точки s.
        2. Добавляем s в очередь и отмечаем её как посещенную.
        3. Пока очередь не пуста:
           a. Извлекаем первый элемент из очереди (текущая позиция).
           b. Если это конечная точка, восстанавливаем путь и возвращаем его.
           c. Для каждого соседа текущей позиции:
              i. Если сосед не посещён, добавляем его в очередь и отмечаем.
        4. Если очередь опустела и конечная точка не найдена, возвращаем None.
        
        @return Список точек, представляющих найденный путь, или None, если путь не найден.
        
        @throws Этот метод не вызывает исключений, но может вернуть None, если путь не найден.
        
        @warning Сложность алгоритма O(V+E), где V - количество вершин, E - количество рёбер.
        Для больших лабиринтов может потребоваться значительное время выполнения.
        """
        start = self.maze.get_start_position()
        end = self.maze.get_end_position()
        
        if start is None or end is None:
            return None
        
        # Очередь для BFS
        queue = deque([start])
        # Словарь для отслеживания предыдущего шага
        visited = {start: None}
        
        while queue:
            current = queue.popleft()
            
            # Если достигли конечной точки
            if current == end:
                # Восстанавливаем путь
                path = []
                while current:
                    path.append(current)
                    current = visited[current]
                return path[::-1]  # Переворачиваем путь
            
            # Обрабатываем соседей
            for neighbor in self.maze.get_neighbors(current):
                if neighbor not in visited:
                    queue.append(neighbor)
                    visited[neighbor] = current
        
        # Если путь не найден
        return None
    
    def get_path_directions(self, path):
        """
        Преобразует путь в последовательность направлений.
        
        Args:
            path (list): Список кортежей (row, col), представляющих путь.
            
        Returns:
            list: Список строк направлений ('вверх', 'вниз', 'влево', 'вправо').
        """
        if not path or len(path) < 2:
            return []
        
        directions = []
        for i in range(1, len(path)):
            prev_row, prev_col = path[i-1]
            curr_row, curr_col = path[i]
            
            if curr_row < prev_row:
                directions.append('вверх')
            elif curr_row > prev_row:
                directions.append('вниз')
            elif curr_col < prev_col:
                directions.append('влево')
            elif curr_col > prev_col:
                directions.append('вправо')
        
        return directions 