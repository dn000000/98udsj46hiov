"""
@file terrain_maze.py
@brief Модуль для представления лабиринта с различными типами местности.

@details
Этот модуль содержит класс TerrainMaze, который расширяет базовый класс Maze
и добавляет поддержку различных типов местности с разной стоимостью прохода.
"""

from maze import Maze

class TerrainMaze(Maze):
    """
    @brief Класс для представления лабиринта с различными типами местности.
    
    @details
    Класс TerrainMaze расширяет базовый класс Maze и добавляет поддержку
    различных типов местности с разной стоимостью прохода. Каждая клетка на
    карте имеет определенный тип и соответствующую стоимость прохода.
    """
    
    # Типы местности и их стоимость прохода
    TERRAIN_TYPES = {
        'R': {'name': 'Road', 'cost': 0.5, 'passable': True, 'color': 'gray'},
        'G': {'name': 'Grass', 'cost': 1.0, 'passable': True, 'color': 'lightgreen'},
        'F': {'name': 'Forest', 'cost': 3.0, 'passable': True, 'color': 'darkgreen'},
        'H': {'name': 'Hill', 'cost': 4.0, 'passable': True, 'color': 'brown'},
        'S': {'name': 'Swamp', 'cost': 5.0, 'passable': True, 'color': 'olive'},
        'W': {'name': 'Water', 'cost': float('inf'), 'passable': False, 'color': 'blue'},
        'M': {'name': 'Mountain', 'cost': float('inf'), 'passable': False, 'color': 'black'},
        ' ': {'name': 'Empty', 'cost': float('inf'), 'passable': False, 'color': 'white'},
        '#': {'name': 'Wall', 'cost': float('inf'), 'passable': False, 'color': 'black'},
        '1': {'name': 'Start', 'cost': 1.0, 'passable': True, 'color': 'lightgreen'},
        'F': {'name': 'Finish', 'cost': 1.0, 'passable': True, 'color': 'lightgreen'},
        # Добавляем информацию о героях (2-9)
        '2': {'name': 'Hero2', 'cost': 1.0, 'passable': True, 'color': 'lightgreen'},
        '3': {'name': 'Hero3', 'cost': 1.0, 'passable': True, 'color': 'lightgreen'},
        '4': {'name': 'Hero4', 'cost': 1.0, 'passable': True, 'color': 'lightgreen'},
        '5': {'name': 'Hero5', 'cost': 1.0, 'passable': True, 'color': 'lightgreen'},
        '6': {'name': 'Hero6', 'cost': 1.0, 'passable': True, 'color': 'lightgreen'},
        '7': {'name': 'Hero7', 'cost': 1.0, 'passable': True, 'color': 'lightgreen'},
        '8': {'name': 'Hero8', 'cost': 1.0, 'passable': True, 'color': 'lightgreen'},
        '9': {'name': 'Hero9', 'cost': 1.0, 'passable': True, 'color': 'lightgreen'},
    }
    
    def __init__(self, grid=None):
        """
        @brief Инициализация объекта TerrainMaze.
        
        @param grid Двумерный список, представляющий лабиринт с типами местности.
                  Если None, создается лабиринт по умолчанию.
        
        @code
        # Пример создания лабиринта с разными типами местности:
        terrain_grid = [
            ['#', '#', '#', '#', '#', '#', '#'],
            ['#', '1', 'G', 'G', 'F', 'F', '#'],
            ['#', 'G', 'G', 'R', 'R', 'G', '#'],
            ['#', 'F', 'H', 'W', 'R', 'G', '#'],
            ['#', 'F', 'H', 'R', 'G', 'G', '#'],
            ['#', 'S', 'S', 'R', 'G', 'F', '#'],
            ['#', '#', '#', '#', '#', '#', '#']
        ]
        maze = TerrainMaze(terrain_grid)
        @endcode
        """
        # Если сетка не указана, создаем типовой пример с разными типами местности
        if grid is None:
            grid = [
                ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
                ['#', '1', 'G', 'G', 'F', 'F', 'H', 'H', 'G', 'G', 'F', '#'],
                ['#', 'G', 'G', 'R', 'R', 'G', 'G', 'G', 'G', 'G', 'G', '#'],
                ['#', 'F', 'H', 'W', 'R', 'G', 'G', 'W', 'W', 'G', 'G', '#'],
                ['#', 'F', 'H', 'R', 'G', 'G', 'G', 'W', 'R', 'R', 'R', '#'],
                ['#', 'S', 'S', 'R', 'G', 'G', 'G', 'G', 'R', 'G', '2', '#'],
                ['#', 'S', 'M', 'M', 'G', 'G', 'G', 'G', 'R', 'G', 'G', '#'],
                ['#', 'S', 'S', 'G', 'G', 'G', 'F', 'F', 'R', 'G', 'G', '#'],
                ['#', 'G', 'G', 'G', 'G', 'G', 'F', 'G', 'R', 'G', 'G', '#'],
                ['#', 'G', 'G', 'W', 'W', 'G', 'G', 'G', 'R', 'G', 'G', '#'],
                ['#', '3', 'G', 'W', 'G', 'G', 'G', 'G', 'R', 'R', 'R', '#'],
                ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#']
            ]
        
        # Вызываем инициализатор родительского класса
        super().__init__(grid)
    
    def get_terrain_type(self, position):
        """
        @brief Возвращает тип местности для указанной позиции.
        
        @param position Кортеж (row, col) с координатами клетки.
        @return Строка, обозначающая тип местности ('R', 'G', 'F' и т.д.).
        """
        if not self.is_valid_position(position):
            return ' '
        
        row, col = position
        return self.grid[row][col]
    
    def get_terrain_info(self, position):
        """
        @brief Возвращает информацию о типе местности для указанной позиции.
        
        @param position Кортеж (row, col) с координатами клетки.
        @return Словарь с информацией о типе местности или None, если позиция недопустима.
        """
        terrain_type = self.get_terrain_type(position)
        return self.TERRAIN_TYPES.get(terrain_type, {'name': 'Unknown', 'cost': float('inf'), 'passable': False, 'color': 'white'})
    
    def get_terrain_cost(self, position):
        """
        @brief Возвращает стоимость прохода через указанную клетку.
        
        @param position Кортеж (row, col) с координатами клетки.
        @return Число, обозначающее стоимость прохода через клетку.
        """
        info = self.get_terrain_info(position)
        return info['cost']
    
    def is_passable(self, position):
        """
        @brief Проверяет, проходима ли указанная клетка.
        
        @param position Кортеж (row, col) с координатами клетки.
        @return True, если клетка проходима, иначе False.
        """
        if not self.is_valid_position(position):
            return False
        
        info = self.get_terrain_info(position)
        return info['passable']
    
    def get_neighbors(self, position):
        """
        @brief Возвращает список соседних клеток, которые проходимы.
        
        @details
        Этот метод переопределяет метод из базового класса, чтобы учитывать
        проходимость клеток в зависимости от типа местности.
        
        @param position Кортеж (row, col) с координатами клетки.
        @return Список кортежей с координатами проходимых соседних клеток.
        """
        neighbors = []
        row, col = position
        
        # Проверяем все 4 соседние клетки
        potential_neighbors = [
            (row-1, col),  # Вверх
            (row+1, col),  # Вниз
            (row, col-1),  # Влево
            (row, col+1)   # Вправо
        ]
        
        for neighbor in potential_neighbors:
            if self.is_passable(neighbor):
                neighbors.append(neighbor)
        
        return neighbors
    
    def __str__(self):
        """
        @brief Возвращает строковое представление лабиринта.
        
        @return Строка, представляющая лабиринт с типами местности.
        """
        result = "Лабиринт с разными типами местности:\n"
        for row in self.grid:
            result += ' '.join(cell for cell in row) + '\n'
        
        # Добавляем легенду
        result += "\nЛегенда:\n"
        result += "R - Дорога (стоимость: 0.5)\n"
        result += "G - Трава (стоимость: 1.0)\n"
        result += "F - Лес (стоимость: 3.0)\n"
        result += "H - Холмы (стоимость: 4.0)\n"
        result += "S - Болото (стоимость: 5.0)\n"
        result += "W - Вода (непроходимо)\n"
        result += "M - Горы (непроходимо)\n"
        result += "# - Стена (непроходимо)\n"
        result += "1 - Начальная точка\n"
        result += "F - Конечная точка\n"
        result += "2-9 - Герои\n"
        
        return result
    
    def get_grid(self):
        """
        @brief Возвращает сетку лабиринта.
        
        @return Двумерный список, представляющий лабиринт.
        """
        return self.grid 