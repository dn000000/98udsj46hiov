"""
@file race.py
@brief Базовый класс для представления расовых особенностей.

@details
Определяет интерфейс и базовую функциональность для всех рас, включая
методы для получения стоимости передвижения с учетом расовых модификаторов.
"""

from abc import ABC
from typing import Dict, Any
import sys
import os

# Добавляем корневой каталог проекта в путь поиска модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.hex.hex_terrain_type import HexTerrainType


class Race(ABC):
    """
    @brief Абстрактный базовый класс для представления расы.
    
    @details
    Определяет общие свойства и методы для всех рас. Каждая конкретная раса должна
    наследоваться от этого класса и определять свои модификаторы для разных
    типов местности, которые влияют на стоимость передвижения.
    """
    
    # Имя расы (должно быть переопределено в наследниках)
    name = "Базовая раса"
    
    # Описание расовых особенностей (должно быть переопределено в наследниках)
    description = "Базовое описание расы"
    
    # Модификаторы стоимости прохода для разных типов местности
    # Значение 1.0 означает нормальную скорость передвижения
    # Значение < 1.0 означает ускорение (бонус)
    # Значение > 1.0 означает замедление (штраф)
    # Значение float('inf') означает непроходимую местность
    # Должно быть переопределено в наследниках
    terrain_modifiers = {t: 1.0 for t in HexTerrainType}
    
    def get_movement_cost(self, terrain_type):
        """
        Возвращает стоимость передвижения по указанному типу местности с учетом
        расовых модификаторов.
        
        @param terrain_type: тип местности из HexTerrainType
        @return: модифицированная стоимость передвижения для данной расы
        """
        # Получаем базовый модификатор для этого типа местности
        modifier = self.terrain_modifiers.get(terrain_type, 1.0)
        
        # Если модификатор бесконечный, это означает непроходимую территорию
        if modifier == float('inf'):
            return float('inf')
        
        # Возвращаем модифицированную стоимость
        return modifier
    
    def __str__(self):
        """
        Возвращает строковое представление расы.
        
        @return: название расы
        """
        return self.name
    
    def get_details(self):
        """
        Возвращает детальное описание расы и ее модификаторов.
        
        @return: строка с описанием расы и ее особенностей
        """
        details = f"Раса: {self.name}\n"
        details += f"Описание: {self.description}\n"
        details += "Модификаторы передвижения по типам местности:\n"
        
        # Сортировка типов местности по значению для удобного вывода
        sorted_terrains = sorted(self.terrain_modifiers.items(), key=lambda x: x[0].value)
        
        for terrain, modifier in sorted_terrains:
            terrain_name = HexTerrainType.get_description(terrain)
            if modifier == float('inf'):
                details += f"  {terrain_name}: Непроходимо\n"
            else:
                # Форматируем модификатор как процент для удобства чтения
                percent = (1.0 - modifier) * 100
                if percent > 0:
                    details += f"  {terrain_name}: Бонус +{percent:.0f}%\n"
                elif percent < 0:
                    details += f"  {terrain_name}: Штраф {percent:.0f}%\n"
                else:
                    details += f"  {terrain_name}: Обычная скорость\n"
                    
        return details

    @classmethod
    def get_terrain_modifier(cls, terrain_type: HexTerrainType) -> float:
        """
        @brief Возвращает модификатор стоимости прохода для указанного типа местности.
        
        @param terrain_type: Тип местности
        @return Модификатор стоимости прохода (float)
        """
        return cls.terrain_modifiers.get(terrain_type, 1.0)
    
    @classmethod
    def get_modified_cost(cls, terrain_type: HexTerrainType) -> float:
        """
        @brief Вычисляет модифицированную стоимость прохода через указанный тип местности.
        
        @param terrain_type: Тип местности
        @return Модифицированная стоимость прохода (float)
        """
        base_cost = HexTerrainType.get_cost(terrain_type)
        modifier = cls.get_terrain_modifier(terrain_type)
        return base_cost * modifier
    
    @classmethod
    def is_passable(cls, terrain_type: HexTerrainType) -> bool:
        """
        @brief Проверяет, проходим ли указанный тип местности для данной расы.
        
        @details
        Некоторые расы могут проходить через типы местности, непроходимые для других
        (например, эльфы могут проходить через густой лес). Но есть и абсолютно
        непроходимые типы местности, такие как стены.
        
        @param terrain_type: Тип местности
        @return True, если тип местности проходим для данной расы
        """
        # Проверяем, проходим ли тип местности в принципе
        if not HexTerrainType.is_passable(terrain_type):
            # Непроходимые типы местности (например, стены) непроходимы для всех рас
            # Если это "абсолютно непроходимый" тип местности, возвращаем False
            if terrain_type in [HexTerrainType.WALL, HexTerrainType.LAVA, HexTerrainType.MOUNTAIN]:
                return False
            # Для других "условно непроходимых" типов проверяем модификатор
            else:
                # Если модификатор меньше бесконечности, то раса может проходить этот тип местности
                return cls.get_terrain_modifier(terrain_type) < float('inf')
        
        # Для обычно проходимых типов местности возвращаем True
        return True 