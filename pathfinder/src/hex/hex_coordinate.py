"""
@file hex_coordinate.py
@brief Модуль для работы с гексагональными координатами.

@details
Этот модуль предоставляет класс HexCoordinate для работы с кубическими 
координатами гексагональной сетки (q, r, s), где q + r + s = 0.
"""

import math
from typing import Tuple, List, Dict, Set


class HexCoordinate:
    """
    @brief Класс для работы с координатами на гексагональной сетке.
    
    @details
    Использует кубические координаты (q, r, s), где q + r + s = 0.
    Это дает удобное представление для расчетов на гексагональной сетке.
    
    Координаты:
    q: ось, идущая с северо-запада на юго-восток
    r: ось, идущая с севера на юг
    s: ось, идущая с северо-востока на юго-запад
    
    Соседи в гексагональной сетке располагаются по 6 направлениям.
    """
    
    # Константы для направлений (в кубических координатах)
    # Порядок: восток, северо-восток, северо-запад, запад, юго-запад, юго-восток
    DIRECTIONS = [
        (1, -1, 0), (0, -1, 1), (-1, 0, 1),
        (-1, 1, 0), (0, 1, -1), (1, 0, -1)
    ]
    
    # Названия направлений для удобства
    DIRECTION_NAMES = [
        "восток", "северо-восток", "северо-запад", 
        "запад", "юго-запад", "юго-восток"
    ]
    
    def __init__(self, q: int, r: int, s: int = None):
        """
        @brief Создает новую гексагональную координату.
        
        @param q: координата q (с северо-запада на юго-восток)
        @param r: координата r (с севера на юг)
        @param s: координата s (с северо-востока на юго-запад), 
                  может быть вычислена как s = -q-r
        """
        if s is None:
            s = -q - r
        
        # Проверка, что координаты удовлетворяют правилу q + r + s = 0
        if q + r + s != 0:
            raise ValueError(f"Координаты не удовлетворяют правилу q + r + s = 0: {q} + {r} + {s} = {q + r + s}")
        
        self.q = q
        self.r = r
        self.s = s
    
    def __eq__(self, other):
        """Сравнение двух координат."""
        if not isinstance(other, HexCoordinate):
            return False
        return self.q == other.q and self.r == other.r and self.s == other.s
    
    def __hash__(self):
        """Хеш-функция для использования в качестве ключа словаря."""
        return hash((self.q, self.r, self.s))
    
    def __str__(self):
        """Строковое представление координаты."""
        return f"({self.q}, {self.r}, {self.s})"
    
    def __repr__(self):
        """Представление для отладки."""
        return f"HexCoordinate(q={self.q}, r={self.r}, s={self.s})"
    
    def to_tuple(self) -> Tuple[int, int, int]:
        """
        @brief Возвращает координаты в виде кортежа (q, r, s).
        
        @return Кортеж (q, r, s)
        """
        return (self.q, self.r, self.s)
    
    def to_axial(self) -> Tuple[int, int]:
        """
        @brief Преобразует кубические координаты в аксиальные (q, r).
        
        @details
        Аксиальные координаты используют только две оси (q, r),
        так как третья (s) может быть вычислена из них.
        
        @return Кортеж (q, r) - аксиальные координаты
        """
        return (self.q, self.r)
    
    def to_offset(self) -> Tuple[int, int]:
        """
        @brief Преобразует кубические координаты в смещенные (col, row).
        
        @details
        Смещенные координаты удобны для хранения гексов в двумерном массиве.
        Здесь используется "odd-r" смещение, где нечетные строки смещены вправо.
        
        @return Кортеж (col, row) - смещенные координаты
        """
        col = self.q + (self.r - (self.r & 1)) // 2
        row = self.r
        return (col, row)
    
    @classmethod
    def from_offset(cls, col: int, row: int) -> 'HexCoordinate':
        """
        @brief Создает гексагональную координату из смещенных координат.
        
        @param col: столбец в смещенной системе
        @param row: строка в смещенной системе
        @return Новый объект HexCoordinate
        """
        q = col - (row - (row & 1)) // 2
        r = row
        s = -q - r
        return cls(q, r, s)
    
    def distance(self, other: 'HexCoordinate') -> int:
        """
        @brief Расстояние между двумя гексами.
        
        @details
        Расстояние в гексагональной сетке - это максимум из абсолютных 
        разностей по трем осям.
        
        @param other: координата, до которой измеряется расстояние
        @return Расстояние в гексах
        """
        return max(
            abs(self.q - other.q),
            abs(self.r - other.r),
            abs(self.s - other.s)
        )
    
    def neighbor(self, direction: int) -> 'HexCoordinate':
        """
        @brief Возвращает координаты соседнего гекса в указанном направлении.
        
        @param direction: направление (0-5), где:
                         0 - восток
                         1 - северо-восток
                         2 - северо-запад
                         3 - запад
                         4 - юго-запад
                         5 - юго-восток
        @return Координаты соседнего гекса
        """
        dir_q, dir_r, dir_s = self.DIRECTIONS[direction]
        return HexCoordinate(self.q + dir_q, self.r + dir_r, self.s + dir_s)
    
    def neighbors(self) -> List['HexCoordinate']:
        """
        @brief Возвращает список всех соседних гексов.
        
        @return Список из 6 координат соседних гексов
        """
        return [self.neighbor(i) for i in range(6)]
    
    @classmethod
    def range(cls, center: 'HexCoordinate', radius: int) -> List['HexCoordinate']:
        """
        @brief Возвращает все гексы в пределах указанного радиуса от центра.
        
        @param center: центральный гекс
        @param radius: радиус в гексах
        @return Список координат всех гексов в пределах радиуса
        """
        results = []
        
        # Перебираем все возможные комбинации q, r, s в пределах радиуса
        for q in range(-radius, radius + 1):
            r_min = max(-radius, -q - radius)
            r_max = min(radius, -q + radius)
            
            for r in range(r_min, r_max + 1):
                s = -q - r
                results.append(HexCoordinate(center.q + q, center.r + r, center.s + s))
        
        return results
    
    @classmethod
    def line(cls, start: 'HexCoordinate', end: 'HexCoordinate') -> List['HexCoordinate']:
        """
        @brief Возвращает все гексы на линии от start до end.
        
        @details
        Использует алгоритм Брезенхема для гексагональной сетки.
        
        @param start: начальная координата
        @param end: конечная координата
        @return Список координат всех гексов на линии
        """
        distance = start.distance(end)
        if distance == 0:
            return [start]
        
        results = []
        for i in range(distance + 1):
            t = 1.0 * i / distance
            q = round(start.q * (1-t) + end.q * t)
            r = round(start.r * (1-t) + end.r * t)
            s = round(start.s * (1-t) + end.s * t)
            results.append(HexCoordinate(q, r, s))
        
        return results 