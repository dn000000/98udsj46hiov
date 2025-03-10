"""
@file hex_terrain_type.py
@brief Перечисление типов местности для гексагональной карты.

@details
Определяет различные типы местности, которые могут быть представлены
на гексагональной карте. Каждый тип имеет свой уникальный идентификатор
и характеристики для алгоритмов поиска пути.
"""

from enum import Enum


class HexTerrainType(Enum):
    """
    @brief Перечисление типов местности для гексагональной карты.
    
    @details
    Каждый тип местности имеет уникальный целочисленный идентификатор и представляет
    определенный тип территории на гексагональной карте. Эти типы влияют на стоимость
    передвижения через соответствующий гекс для разных рас.
    """
    
    # Базовые типы местности
    GRASS = 0       # Трава, равнина
    FOREST = 1      # Лес
    HILLS = 2       # Холмы
    MOUNTAIN = 3    # Горы
    WATER = 4       # Вода, озеро
    SWAMP = 5       # Болото
    DESERT = 6      # Пустыня
    SNOW = 7        # Снег
    LAVA = 8        # Лава
    
    # Искусственные сооружения
    ROAD = 9        # Дорога
    CASTLE = 10     # Замок
    VILLAGE = 11    # Деревня
    CAVE = 12       # Пещера
    WALL = 13       # Стена, непреодолимое препятствие
    
    # Специальные типы для поиска пути
    START = 14      # Начальная точка
    END = 15        # Конечная точка
    
    # Словарь с описанием каждого типа местности для вывода
    DESCRIPTIONS = {
        GRASS: "Равнина",
        FOREST: "Лес",
        HILLS: "Холмы",
        MOUNTAIN: "Горы",
        WATER: "Вода",
        SWAMP: "Болото",
        DESERT: "Пустыня",
        SNOW: "Снег",
        LAVA: "Лава",
        ROAD: "Дорога",
        CASTLE: "Замок",
        VILLAGE: "Деревня",
        CAVE: "Пещера",
        WALL: "Стена",
        START: "Старт",
        END: "Финиш"
    }
    
    # Цвета для визуализации разных типов местности
    COLORS = {
        GRASS: '#7CFC00',    # LawnGreen
        FOREST: '#228B22',   # ForestGreen
        HILLS: '#CD853F',    # Peru (коричневый)
        MOUNTAIN: '#A0522D', # Sienna (темно-коричневый)
        WATER: '#1E90FF',    # DodgerBlue
        SWAMP: '#2F4F4F',    # DarkSlateGray
        DESERT: '#F4A460',   # SandyBrown
        SNOW: '#FFFAFA',     # Snow
        LAVA: '#FF4500',     # OrangeRed
        ROAD: '#808080',     # Gray
        CASTLE: '#708090',   # SlateGray
        VILLAGE: '#8B4513',  # SaddleBrown
        CAVE: '#4B0082',     # Indigo
        WALL: '#696969',     # DimGray
        START: '#32CD32',    # LimeGreen
        END: '#DC143C'       # Crimson
    }
    
    @classmethod
    def get_description(cls, terrain_type):
        """
        Возвращает текстовое описание типа местности.
        
        @param terrain_type: Тип местности из перечисления HexTerrainType
        @return: Строка с описанием типа местности
        """
        # Преобразуем описания в обычный словарь
        descriptions_dict = {k: v for k, v in cls.DESCRIPTIONS.items()}
        
        # Если terrain_type - это экземпляр элемента перечисления HexTerrainType
        if isinstance(terrain_type, HexTerrainType):
            # Используем прямой доступ с проверкой наличия ключа
            if terrain_type in descriptions_dict:
                return descriptions_dict[terrain_type]
            return "Неизвестный тип"
        else:
            # Возможно это значение из перечисления, а не сам элемент
            if terrain_type in descriptions_dict:
                return descriptions_dict[terrain_type]
            return "Неизвестный тип"
    
    @classmethod
    def get_color(cls, terrain_type):
        """
        Возвращает цвет для визуализации типа местности.
        
        @param terrain_type: Тип местности из перечисления HexTerrainType
        @return: Строка с шестнадцатеричным кодом цвета
        """
        # Преобразуем цвета в обычный словарь
        colors_dict = {k: v for k, v in cls.COLORS.items()}
        
        # Если terrain_type - это экземпляр элемента перечисления HexTerrainType
        if isinstance(terrain_type, HexTerrainType):
            # Используем прямой доступ с проверкой наличия ключа
            if terrain_type in colors_dict:
                return colors_dict[terrain_type]
            return "#000000"  # Черный по умолчанию
        else:
            # Возможно это значение из перечисления, а не сам элемент
            if terrain_type in colors_dict:
                return colors_dict[terrain_type]
            return "#000000"  # Черный по умолчанию 