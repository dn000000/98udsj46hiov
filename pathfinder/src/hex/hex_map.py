"""
@file hex_map.py
@brief Класс для представления гексагональной карты.

@details
Этот класс реализует гексагональную карту, содержащую ячейки с различными типами местности.
Карта предоставляет методы для добавления ячеек, получения информации о ячейках, 
определения соседей и визуализации.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import RegularPolygon

from .hex_cell import HexCell
from .hex_terrain_type import HexTerrainType


class HexMap:
    """
    @brief Класс, представляющий гексагональную карту.
    
    @details
    Карта состоит из гексагональных ячеек, каждая из которых имеет тип местности.
    Используется кубическая система координат (q, r, s) для представления гексов.
    """
    
    def __init__(self):
        """
        Инициализирует пустую гексагональную карту.
        """
        # Словарь ячеек, где ключ - кортеж (q, r), значение - объект HexCell
        self.cells = {}
        # Точки старта и финиша (если определены)
        self.start = None
        self.end = None
    
    def add_cell(self, q, r, terrain_type):
        """
        Добавляет новую ячейку на карту.
        
        @param q: q-координата в кубической системе
        @param r: r-координата в кубической системе
        @param terrain_type: тип местности (из HexTerrainType)
        @return: созданная ячейка HexCell
        """
        # Создаем новую ячейку
        cell = HexCell(q, r, terrain_type)
        # Добавляем в словарь
        self.cells[(q, r)] = cell
        
        # Если это стартовая или конечная точка, сохраняем ее
        if terrain_type == HexTerrainType.START:
            self.start = cell
        elif terrain_type == HexTerrainType.END:
            self.end = cell
            
        return cell
    
    def get_cell(self, q, r):
        """
        Возвращает ячейку по ее координатам.
        
        @param q: q-координата в кубической системе
        @param r: r-координата в кубической системе
        @return: объект HexCell или None, если ячейки с такими координатами нет
        """
        return self.cells.get((q, r))
    
    def get_neighbors(self, cell):
        """
        Возвращает всех соседей для заданной ячейки, которые существуют на карте.
        
        @param cell: ячейка, для которой ищем соседей
        @return: список соседних ячеек HexCell
        """
        neighbor_coords = cell.get_neighbors()
        neighbors = []
        
        for q, r in neighbor_coords:
            neighbor = self.get_cell(q, r)
            if neighbor:
                neighbors.append(neighbor)
                
        return neighbors
    
    def find_path(self, start, end, race):
        """
        Находит путь от начальной до конечной точки с учетом расовых модификаторов.
        
        @param start: начальная ячейка
        @param end: конечная ячейка
        @param race: объект Race, представляющий расу с модификаторами передвижения
        @return: (путь, общая стоимость) или (None, float('inf')), если путь не найден
        """
        from src.pathfinding.hex_a_star import find_path
        return find_path(self, start, end, race)
    
    def visualize(self, path=None, figsize=(10, 8)):
        """
        Визуализирует гексагональную карту и опционально путь.
        
        @param path: список ячеек HexCell, представляющих путь (опционально)
        @param figsize: размер рисунка (ширина, высота) в дюймах
        """
        # Создаем фигуру и оси
        fig, ax = plt.subplots(figsize=figsize)
        
        # Константы для отрисовки
        hex_size = 1.0
        # Смещения для координат (для преобразования кубических в декартовы)
        sqrt3 = np.sqrt(3)
        
        # Отрисовываем каждую ячейку
        for coords, cell in self.cells.items():
            q, r = coords
            # Вычисляем позицию центра гекса в декартовых координатах
            x = hex_size * (sqrt3 * q + sqrt3/2 * r)
            y = hex_size * (3/2 * r)
            
            # Определяем цвет гекса на основе terrain_type
            terrain_type = cell.terrain_type
            
            # Карта цветов для различных типов местности
            color_map = {
                HexTerrainType.GRASS: '#7CFC00',    # LawnGreen
                HexTerrainType.FOREST: '#228B22',   # ForestGreen
                HexTerrainType.HILLS: '#CD853F',    # Peru (коричневый)
                HexTerrainType.MOUNTAIN: '#A0522D', # Sienna (темно-коричневый)
                HexTerrainType.WATER: '#1E90FF',    # DodgerBlue
                HexTerrainType.SWAMP: '#2F4F4F',    # DarkSlateGray
                HexTerrainType.DESERT: '#F4A460',   # SandyBrown
                HexTerrainType.SNOW: '#FFFAFA',     # Snow
                HexTerrainType.LAVA: '#FF4500',     # OrangeRed
                HexTerrainType.ROAD: '#808080',     # Gray
                HexTerrainType.CASTLE: '#708090',   # SlateGray
                HexTerrainType.VILLAGE: '#8B4513',  # SaddleBrown
                HexTerrainType.CAVE: '#4B0082',     # Indigo
                HexTerrainType.WALL: '#696969',     # DimGray
                HexTerrainType.START: '#32CD32',    # LimeGreen
                HexTerrainType.END: '#DC143C'       # Crimson
            }
            
            color = color_map.get(terrain_type, '#000000')  # Черный по умолчанию
            
            # Создаем гексагон
            hex_patch = RegularPolygon(
                (x, y),
                numVertices=6,
                radius=hex_size,
                orientation=0,  # плоской стороной вверх
                facecolor=color,
                edgecolor='black',
                alpha=0.7
            )
            ax.add_patch(hex_patch)
            
            # Добавляем координаты
            ax.text(x, y, f"({q},{r})", ha='center', va='center', fontsize=8)
        
        # Если есть путь, отрисовываем его
        if path:
            path_x = []
            path_y = []
            for cell in path:
                q, r = cell.q, cell.r
                x = hex_size * (sqrt3 * q + sqrt3/2 * r)
                y = hex_size * (3/2 * r)
                path_x.append(x)
                path_y.append(y)
            ax.plot(path_x, path_y, 'r-', linewidth=2, alpha=0.7)
        
        # Настраиваем оси и отображаем
        ax.set_aspect('equal')
        ax.autoscale_view()
        ax.set_title("Гексагональная карта")
        plt.tight_layout()
        plt.show()
    
    @classmethod
    def load_from_text(cls, map_text):
        """
        Создает карту из текстового представления.
        
        @param map_text: текстовое представление карты
        @return: объект HexMap
        
        Формат текста:
        - Нечетные строки начинаются с пробела
        - Каждый символ представляет определенный тип местности
        - Символы должны соответствовать типам из HexTerrainType
        
        Пример:
         G F M  (строка 0, r=0)
        G G F M  (строка 1, r=1)
         W G F   (строка 2, r=2)
        """
        hex_map = cls()
        
        # Разбиваем текст на строки
        lines = [line.strip() for line in map_text.strip().split('\n')]
        
        # Считываем карту
        for r, line in enumerate(lines):
            row_offset = r // 2  # Смещение для четных/нечетных строк
            
            for col, char in enumerate(line):
                if char == ' ':
                    continue
                
                # Вычисляем кубические координаты
                q = col - row_offset
                
                # Определяем тип местности по символу
                try:
                    terrain_type = None
                    for tt in HexTerrainType:
                        if tt.value == int(char):
                            terrain_type = tt
                            break
                    if terrain_type is None:
                        terrain_type = HexTerrainType.GRASS  # По умолчанию
                except ValueError:
                    terrain_type = HexTerrainType.GRASS  # По умолчанию
                
                # Добавляем ячейку
                hex_map.add_cell(q, r, terrain_type)
        
        return hex_map 