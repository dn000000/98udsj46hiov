"""
@file terrain_equidistant_finder.py
@brief Модуль для поиска оптимальной точки сбора команды с учетом различных типов местности.

@details
Этот модуль содержит класс TerrainEquidistantFinder, который находит
оптимальную точку сбора для команды героев с учетом различных типов
местности и скоростей передвижения героев.
"""

import heapq
from collections import defaultdict
from equidistant_finder import EquidistantFinder

class TerrainEquidistantFinder(EquidistantFinder):
    """
    @brief Класс для поиска оптимальной точки сбора с учетом различных типов местности.
    
    @details
    Этот класс расширяет базовый класс EquidistantFinder и добавляет
    функциональность для учета различных типов местности и скоростей
    передвижения героев при поиске оптимальной точки сбора.
    """
    
    def __init__(self, maze):
        """
        @brief Инициализация объекта TerrainEquidistantFinder.
        
        @param maze Объект TerrainMaze, представляющий лабиринт с типами местности.
        
        @code
        # Пример использования:
        from terrain_maze import TerrainMaze
        from terrain_equidistant_finder import TerrainEquidistantFinder
        
        # Создаем лабиринт с разными типами местности
        maze = TerrainMaze()
        
        # Создаем объект для поиска оптимальной точки сбора
        finder = TerrainEquidistantFinder(maze)
        
        # Задаем стартовые позиции героев и их скорости
        hero_positions = [(0, 0), (5, 5), (10, 10)]
        hero_speeds = [1.0, 0.8, 1.2]
        
        # Ищем оптимальную точку сбора
        gathering_point = finder.find_optimal_gathering_point(hero_positions, hero_speeds)
        @endcode
        """
        # Проверяем, что переданный лабиринт поддерживает методы для работы со стоимостью перемещения
        if not hasattr(maze, 'get_terrain_cost') or not hasattr(maze, 'is_passable'):
            raise ValueError("Переданный лабиринт должен поддерживать методы для работы со стоимостью перемещения")
        
        super().__init__(maze)
    
    def compute_distances_with_costs(self, sources, speeds=None):
        """
        @brief Вычисляет минимальные расстояния от источников до всех точек лабиринта с учетом стоимости перемещения.
        
        @param sources Список стартовых позиций героев.
        @param speeds Список скоростей передвижения героев. Если не указан, то используется одинаковая скорость для всех.
        
        @return Словарь, где ключи - позиции в лабиринте, а значения - словари, содержащие время пути от каждого источника.
        
        @details
        Этот метод использует модифицированный алгоритм Дейкстры для вычисления минимального
        времени пути от каждого источника до всех доступных точек в лабиринте.
        """
        if not sources:
            return {}
        
        # Если скорости не указаны, используем одинаковую скорость для всех
        if speeds is None:
            speeds = [1.0] * len(sources)
            
        # Проверяем, что количество источников и скоростей совпадает
        if len(sources) != len(speeds):
            raise ValueError("Количество источников и скоростей должно совпадать")
        
        # Инициализируем словарь для хранения минимального времени от каждого источника
        # до каждой позиции в лабиринте
        distances = defaultdict(dict)
        
        # Для каждого источника проводим расчет минимального времени пути
        for idx, (source, speed) in enumerate(zip(sources, speeds)):
            # Проверяем, что источник находится внутри лабиринта
            if not self.maze.is_valid_position(source):
                continue
            
            # Приоритетная очередь для Дейкстры
            # Формат элемента: (время, позиция)
            priority_queue = [(0, source)]
            
            # Словарь, содержащий текущее минимальное время пути до каждой позиции
            time_so_far = {source: 0}
            
            while priority_queue:
                # Извлекаем позицию с минимальным временем
                current_time, current_pos = heapq.heappop(priority_queue)
                
                # Если текущее время больше, чем известное минимальное, пропускаем
                if current_time > time_so_far[current_pos]:
                    continue
                
                # Сохраняем минимальное время пути для текущей позиции
                distances[current_pos][idx] = current_time
                
                # Проверяем все соседние позиции
                for next_pos in self.maze.get_neighbors(current_pos):
                    # Вычисляем новое время пути с учетом стоимости перемещения и скорости героя
                    terrain_cost = self.maze.get_terrain_cost(next_pos)
                    time_to_move = terrain_cost / speed
                    new_time = current_time + time_to_move
                    
                    # Если мы нашли новый лучший путь до next_pos или это первый найденный путь
                    if next_pos not in time_so_far or new_time < time_so_far[next_pos]:
                        time_so_far[next_pos] = new_time
                        heapq.heappush(priority_queue, (new_time, next_pos))
        
        return distances
    
    def find_optimal_gathering_point(self, hero_positions, hero_speeds=None):
        """
        @brief Находит оптимальную точку сбора для команды героев с учетом скоростей передвижения.
        
        @param hero_positions Список стартовых позиций героев.
        @param hero_speeds Список скоростей передвижения героев. Если не указан, то используется одинаковая скорость для всех.
        
        @return Кортеж (row, col), представляющий оптимальную точку сбора.
        
        @details
        Этот метод находит точку сбора, при которой максимальное время прибытия
        всех героев минимально. Учитывается скорость передвижения каждого героя
        и стоимость прохождения через различные типы местности.
        """
        if not hero_positions:
            return None
        
        # Вычисляем расстояния с учетом стоимости перемещения и скоростей
        distances = self.compute_distances_with_costs(hero_positions, hero_speeds)
        
        # Если расстояния не вычислены, возвращаем None
        if not distances:
            return None
        
        # Находим точку с минимальным максимальным временем
        min_max_time = float('inf')
        optimal_point = None
        
        for pos, times in distances.items():
            # Если не все герои могут достичь этой точки, пропускаем её
            if len(times) != len(hero_positions):
                continue
            
            # Находим максимальное время прибытия для этой точки
            max_time = max(times.values())
            
            # Если найдена точка с меньшим максимальным временем, обновляем результат
            if max_time < min_max_time:
                min_max_time = max_time
                optimal_point = pos
        
        return optimal_point
    
    def get_arrival_times(self, gathering_point, hero_positions, hero_speeds=None):
        """
        @brief Возвращает время прибытия каждого героя в точку сбора.
        
        @param gathering_point Кортеж (row, col), представляющий точку сбора.
        @param hero_positions Список стартовых позиций героев.
        @param hero_speeds Список скоростей передвижения героев. Если не указан, то используется одинаковая скорость для всех.
        
        @return Список времен прибытия для каждого героя.
        """
        if not gathering_point or not hero_positions:
            return []
        
        # Вычисляем расстояния с учетом стоимости перемещения и скоростей
        distances = self.compute_distances_with_costs(hero_positions, hero_speeds)
        
        # Если точка сбора не достижима для всех героев, возвращаем пустой список
        if gathering_point not in distances or len(distances[gathering_point]) != len(hero_positions):
            return []
        
        # Извлекаем времена прибытия для каждого героя
        arrival_times = [distances[gathering_point][idx] for idx in range(len(hero_positions))]
        
        return arrival_times
    
    def get_max_arrival_time(self, gathering_point, hero_positions, hero_speeds=None):
        """
        @brief Возвращает максимальное время прибытия в точку сбора.
        
        @param gathering_point Кортеж (row, col), представляющий точку сбора.
        @param hero_positions Список стартовых позиций героев.
        @param hero_speeds Список скоростей передвижения героев. Если не указан, то используется одинаковая скорость для всех.
        
        @return Максимальное время прибытия.
        """
        arrival_times = self.get_arrival_times(gathering_point, hero_positions, hero_speeds)
        
        if not arrival_times:
            return float('inf')
        
        return max(arrival_times) 