"""
Модуль для работы с лабиринтом.

Этот модуль предоставляет классы и функции для представления лабиринта
и выполнения операций над ним.
"""

class Maze:
    """
    Класс для представления лабиринта.
    
    Лабиринт представлен в виде двумерной сетки, где:
    - 0: свободная клетка
    - 1: стена
    - '1', '2', '3', ...: герои (начальные точки)
    - 'F': конечная точка
    """
    
    def __init__(self, grid=None):
        """
        Инициализация лабиринта.
        
        Args:
            grid (list): Двумерный список, представляющий лабиринт.
                         Если None, создается простой лабиринт по умолчанию.
        """
        if grid is None:
            self.grid = [
                ['1', 0, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 1],
                [1, 1, 1, 0, 0, 1],
                [1, 0, 0, 0, 1, 1],
                [1, 0, 1, 0, 0, 'F'],
                [1, 1, 1, 1, 1, 1]
            ]
        else:
            self.grid = grid
        
        self.height = len(self.grid)
        self.width = len(self.grid[0]) if self.height > 0 else 0
        
        # Находим героев и конечную точку
        self.heroes = {}  # словарь {идентификатор: позиция}
        self.end = None
        
        for i in range(self.height):
            for j in range(self.width):
                cell = self.grid[i][j]
                if isinstance(cell, str) and cell.isdigit():
                    self.heroes[cell] = (i, j)
                elif cell == 'F':
                    self.end = (i, j)
    
    def is_valid_position(self, position):
        """
        Проверяет, является ли позиция допустимой (внутри лабиринта и не стена).
        
        Args:
            position (tuple): Кортеж (row, col), представляющий позицию.
            
        Returns:
            bool: True, если позиция допустима, иначе False.
        """
        row, col = position
        if 0 <= row < self.height and 0 <= col < self.width:
            cell = self.grid[row][col]
            return cell != 1  # Не стена
        return False
    
    def get_neighbors(self, position):
        """
        Получает соседние позиции для данной позиции.
        
        Args:
            position (tuple): Кортеж (row, col), представляющий текущую позицию.
            
        Returns:
            list: Список кортежей (row, col), представляющих соседние позиции.
        """
        row, col = position
        neighbors = [
            (row-1, col),  # Верх
            (row+1, col),  # Низ
            (row, col-1),  # Влево
            (row, col+1)   # Вправо
        ]
        
        # Фильтруем невалидные позиции
        return [pos for pos in neighbors if self.is_valid_position(pos)]
    
    def get_start_position(self):
        """
        Возвращает начальную позицию (для совместимости).
        
        Returns:
            tuple: Кортеж (row, col), представляющий начальную позицию.
        """
        return self.heroes.get('1')
    
    def get_end_position(self):
        """
        Возвращает конечную позицию.
        
        Returns:
            tuple: Кортеж (row, col), представляющий конечную позицию.
        """
        return self.end
    
    def get_hero_positions(self):
        """
        Возвращает словарь позиций всех героев.
        
        Returns:
            dict: Словарь {идентификатор: позиция} для всех героев.
        """
        return self.heroes
    
    def get_all_valid_positions(self):
        """
        Возвращает список всех допустимых позиций в лабиринте.
        
        Returns:
            list: Список кортежей (row, col), представляющих все допустимые позиции.
        """
        valid_positions = []
        for i in range(self.height):
            for j in range(self.width):
                if self.is_valid_position((i, j)):
                    valid_positions.append((i, j))
        return valid_positions
    
    def __str__(self):
        """
        Возвращает строковое представление лабиринта.
        
        Returns:
            str: Строковое представление лабиринта.
        """
        result = ""
        for row in self.grid:
            result += " ".join(str(cell) for cell in row) + "\n"
        return result 