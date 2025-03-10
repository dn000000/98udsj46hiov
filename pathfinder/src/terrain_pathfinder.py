"""
@file terrain_pathfinder.py
@brief Модуль для поиска пути в лабиринте с учетом стоимости перемещения.

@details
Этот модуль содержит класс TerrainPathFinder, который расширяет
функциональность базового класса PathFinder и добавляет
алгоритм Дейкстры для поиска оптимального пути с учетом
разных типов местности и стоимости перемещения.
"""

import heapq
from pathfinder import PathFinder
from terrain_maze import TerrainMaze

class TerrainPathFinder(PathFinder):
    """
    @brief Класс для поиска пути в лабиринте с учетом стоимости перемещения.
    
    @details
    Класс TerrainPathFinder расширяет базовый класс PathFinder и добавляет
    алгоритм Дейкстры для поиска оптимального пути с учетом разных типов
    местности и стоимости перемещения.
    """
    
    def __init__(self, maze):
        """
        @brief Инициализация объекта TerrainPathFinder.
        
        @param maze Объект TerrainMaze, представляющий лабиринт с типами местности.
        
        @code
        # Пример использования:
        from terrain_maze import TerrainMaze
        from terrain_pathfinder import TerrainPathFinder
        
        # Создаем лабиринт с разными типами местности
        maze = TerrainMaze()
        
        # Создаем объект для поиска пути
        finder = TerrainPathFinder(maze)
        
        # Ищем путь с учетом стоимости перемещения
        path = finder.dijkstra()
        @endcode
        """
        # Проверяем, что переданный лабиринт поддерживает методы для работы со стоимостью перемещения
        if not hasattr(maze, 'get_terrain_cost') or not hasattr(maze, 'is_passable'):
            raise ValueError("Переданный лабиринт должен поддерживать методы для работы со стоимостью перемещения")
        
        super().__init__(maze)
    
    def dijkstra(self):
        """
        @brief Алгоритм Дейкстры для поиска кратчайшего пути с учетом стоимости перемещения.
        
        @details
        Алгоритм Дейкстры находит путь минимальной стоимости от начальной точки до конечной,
        учитывая разные стоимости прохода через различные типы местности.
        
        Пошаговый алгоритм:
        1. Начинаем с начальной точки и устанавливаем её стоимость в 0.
        2. Помещаем начальную точку в приоритетную очередь.
        3. Пока очередь не пуста:
           a. Извлекаем вершину с минимальной стоимостью.
           b. Если это конечная точка, восстанавливаем путь и возвращаем его.
           c. Для каждого проходимого соседа:
              i. Вычисляем новую стоимость пути как сумму текущей стоимости и стоимости прохода через соседа.
              ii. Если найден путь с меньшей стоимостью, обновляем информацию о соседе.
        4. Если очередь опустела и конечная точка не найдена, возвращаем None.
        
        @return Список точек, представляющих найденный путь, или None, если путь не найден.
        
        @throws Этот метод не вызывает исключений, но может вернуть None, если путь не найден.
        
        @see https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
        """
        start = self.maze.get_start_position()
        end = self.maze.get_end_position()
        
        if not start or not end:
            return None
            
        # Приоритетная очередь для Дейкстры
        # Формат элемента: (стоимость, позиция)
        priority_queue = [(0, start)]
        
        # Словарь, содержащий текущую минимальную стоимость пути до каждой позиции
        cost_so_far = {start: 0}
        
        # Словарь для восстановления пути
        came_from = {start: None}
        
        while priority_queue:
            # Извлекаем позицию с минимальной стоимостью
            current_cost, current_pos = heapq.heappop(priority_queue)
            
            # Если мы достигли конечной точки, то путь найден
            if current_pos == end:
                break
                
            # Если текущая стоимость больше, чем известная минимальная, пропускаем
            if current_cost > cost_so_far[current_pos]:
                continue
                
            # Проверяем все соседние позиции
            for next_pos in self.maze.get_neighbors(current_pos):
                # Вычисляем новую стоимость пути
                new_cost = current_cost + self.maze.get_terrain_cost(next_pos)
                
                # Если мы нашли новый лучший путь до next_pos или это первый найденный путь
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    heapq.heappush(priority_queue, (new_cost, next_pos))
                    came_from[next_pos] = current_pos
        
        # Если мы не достигли конечной точки, то путь не найден
        if end not in came_from:
            return None
            
        # Восстанавливаем путь
        path = []
        current = end
        
        while current:
            path.append(current)
            current = came_from[current]
            
        # Переворачиваем путь, чтобы он шел от начала к концу
        path.reverse()
        
        return path
    
    def get_path_cost(self, path):
        """
        @brief Вычисляет общую стоимость пути.
        
        @param path Список точек, представляющих путь.
        @return Число, представляющее общую стоимость пути.
        """
        if not path or len(path) < 2:
            return 0
            
        total_cost = 0
        
        # Суммируем стоимость прохождения через каждую точку пути, кроме начальной
        for i in range(1, len(path)):
            total_cost += self.maze.get_terrain_cost(path[i])
            
        return total_cost
    
    def get_path_directions_with_costs(self, path):
        """
        @brief Возвращает последовательность направлений и стоимостей шагов для найденного пути.
        
        @param path Список точек, представляющих путь.
        @return Список кортежей (направление, стоимость).
        """
        if not path or len(path) < 2:
            return []
            
        directions = []
        
        # Определяем направление для каждого шага
        for i in range(len(path) - 1):
            current_row, current_col = path[i]
            next_row, next_col = path[i+1]
            
            # Определяем направление
            if next_row < current_row:
                direction = "↑"  # Вверх
            elif next_row > current_row:
                direction = "↓"  # Вниз
            elif next_col < current_col:
                direction = "←"  # Влево
            else:
                direction = "→"  # Вправо
                
            # Получаем стоимость шага
            cost = self.maze.get_terrain_cost(path[i+1])
            
            directions.append((direction, cost))
            
        return directions 