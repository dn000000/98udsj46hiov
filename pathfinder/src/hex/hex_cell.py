"""
@file hex_cell.py
@brief Класс для представления гексагональной ячейки на карте.

@details
Этот класс реализует гексагональную ячейку карты, хранящую координаты, тип местности и
предоставляющую методы для работы с гексагональными координатами, включая вычисление
расстояний и соседних ячеек.
"""


class HexCell:
    """
    @brief Класс, представляющий гексагональную ячейку на карте.
    
    @details
    Используется кубическая система координат (q, r, s) для представления гексагональной ячейки,
    где q + r + s = 0. Каждая ячейка имеет тип местности, который влияет на стоимость
    передвижения через нее.
    """
    
    def __init__(self, q, r, terrain_type):
        """
        Инициализирует гексагональную ячейку с заданными координатами и типом местности.
        
        @param q: q-координата в кубической системе
        @param r: r-координата в кубической системе
        @param terrain_type: тип местности (из HexTerrainType)
        """
        self.q = q
        self.r = r
        # s-координата вычисляется из q и r (т.к. q + r + s = 0)
        self.s = -q - r
        self.terrain_type = terrain_type
        
    def __eq__(self, other):
        """
        Проверяет равенство двух гексагональных ячеек.
        
        @param other: другая гексагональная ячейка
        @return: True, если ячейки имеют одинаковые координаты
        """
        if not isinstance(other, HexCell):
            return False
        return self.q == other.q and self.r == other.r
    
    def __hash__(self):
        """
        Вычисляет хеш гексагональной ячейки на основе ее координат.
        
        @return: хеш ячейки
        """
        return hash((self.q, self.r))
    
    def __str__(self):
        """
        Возвращает строковое представление гексагональной ячейки.
        
        @return: строка с координатами и типом местности
        """
        from src.hex.hex_terrain_type import HexTerrainType
        terrain_desc = HexTerrainType.get_description(self.terrain_type)
        return f"HexCell(q={self.q}, r={self.r}, s={self.s}, terrain={terrain_desc})"
    
    def distance(self, other):
        """
        Вычисляет расстояние между двумя гексагональными ячейками.
        
        @param other: другая гексагональная ячейка
        @return: расстояние между ячейками в гексах
        """
        return max(
            abs(self.q - other.q),
            abs(self.r - other.r),
            abs(self.s - other.s)
        )
    
    def get_neighbors(self):
        """
        Возвращает координаты всех соседних гексов.
        
        @return: список кортежей (q, r) для всех соседних гексов
        """
        # Смещения для соседних гексов в кубических координатах
        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        
        neighbors = []
        for dir_q, dir_r in directions:
            neighbors.append((self.q + dir_q, self.r + dir_r))
        
        return neighbors 