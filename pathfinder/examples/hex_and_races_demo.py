#!/usr/bin/env python
"""
@file hex_and_races_demo.py
@brief Демонстрационный скрипт для гексагональной карты и расовых модификаторов.

@details
Этот скрипт демонстрирует возможности работы с гексагональной картой, разными
типами местности и расовыми модификаторами для передвижения. Включает примеры
создания карты, поиска пути для разных рас и визуализации результатов.
"""

import sys
import os
import logging
import argparse
from enum import Enum

# Добавляем путь к пакету pathfinder в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.hex import HexMap, HexCell, HexTerrainType
from src.races import Human, Elf, Dwarf, Orc
from src.pathfinding import find_path


class DemoMode(Enum):
    """
    Режимы демонстрации.
    """
    SIMPLE = "simple"           # Простая демонстрация одной расы на карте
    COMPARISON = "comparison"   # Сравнение пути для разных рас
    CUSTOM_MAP = "custom_map"   # Использование пользовательской карты
    ALL = "all"                 # Все демонстрации


def create_sample_map():
    """
    Создает образец гексагональной карты для демонстрации.
    
    @return: объект HexMap с разными типами местности
    """
    hex_map = HexMap()
    
    # Добавляем различные типы местности
    # Создаем правильную сетку 10x10
    for q in range(10):
        for r in range(10):
            # Выбираем тип местности в зависимости от координат
            if q == 0 and r == 0:
                terrain_type = HexTerrainType.START
            elif q == 9 and r == 9:
                terrain_type = HexTerrainType.END
            elif 3 <= q <= 6 and 2 <= r <= 5:
                terrain_type = HexTerrainType.FOREST
            elif 7 <= q <= 8 and 1 <= r <= 3:
                terrain_type = HexTerrainType.MOUNTAIN
            elif 1 <= q <= 2 and 7 <= r <= 8:
                terrain_type = HexTerrainType.WATER
            elif q == 5 and r == 7:
                terrain_type = HexTerrainType.VILLAGE
            elif 4 <= q <= 6 and r == 1:
                terrain_type = HexTerrainType.ROAD
            elif q == 4 and 1 <= r <= 7:
                terrain_type = HexTerrainType.ROAD
            elif 2 <= q <= 3 and 4 <= r <= 5:
                terrain_type = HexTerrainType.SWAMP
            elif 8 <= q <= 9 and 7 <= r <= 8:
                terrain_type = HexTerrainType.DESERT
            elif 1 <= q <= 2 and 1 <= r <= 2:
                terrain_type = HexTerrainType.SNOW
            elif q == 7 and r == 6:
                terrain_type = HexTerrainType.CASTLE
            elif q == 2 and r == 6:
                terrain_type = HexTerrainType.LAVA
            else:
                terrain_type = HexTerrainType.GRASS
                
            # Добавляем ячейку на карту
            hex_map.add_cell(q, r, terrain_type)
    
    return hex_map


def simple_demo():
    """
    Демонстрирует поиск пути для одной расы на гексагональной карте.
    """
    print("\n=== ПРОСТАЯ ДЕМОНСТРАЦИЯ ===")
    print("Поиск пути для человека на гексагональной карте")
    
    # Создаем карту
    hex_map = create_sample_map()
    
    # Создаем расу
    human = Human()
    
    # Находим путь от начала до конца
    path, cost = hex_map.find_path(hex_map.start, hex_map.end, human)
    
    if path:
        print(f"Путь найден! Стоимость: {cost:.2f}")
        print(f"Количество шагов: {len(path) - 1}")
        
        # Визуализируем карту и путь
        hex_map.visualize(path)
    else:
        print("Путь не найден!")
        # Визуализируем только карту
        hex_map.visualize()


def comparison_demo():
    """
    Демонстрирует сравнение путей для разных рас на одной карте.
    """
    print("\n=== СРАВНИТЕЛЬНАЯ ДЕМОНСТРАЦИЯ ===")
    print("Сравнение путей для разных рас на одной карте")
    
    # Создаем карту
    hex_map = create_sample_map()
    
    # Создаем разные расы
    races = [Human(), Elf(), Dwarf(), Orc()]
    
    # Находим путь для каждой расы и отображаем результаты
    for race in races:
        print(f"\nПоиск пути для расы: {race.name}")
        path, cost = hex_map.find_path(hex_map.start, hex_map.end, race)
        
        if path:
            print(f"Путь найден! Стоимость: {cost:.2f}")
            print(f"Количество шагов: {len(path) - 1}")
            
            # Выводим некоторые детали о пути
            terrain_counts = {}
            for cell in path:
                terrain = cell.terrain_type
                # Отладочный вывод
                if len(terrain_counts) == 0:
                    print(f"Тип terrain: {type(terrain)}, значение: {terrain}")
                
                # Получаем имя типа местности напрямую из значения enum
                if hasattr(terrain, "name"):
                    terrain_name = terrain.name
                else:
                    terrain_name = str(terrain)
                
                terrain_counts[terrain_name] = terrain_counts.get(terrain_name, 0) + 1
            
            print("Пройденные типы местности:")
            for terrain_name, count in terrain_counts.items():
                print(f"  {terrain_name}: {count} гексов")
            
            # Визуализируем карту и путь
            hex_map.visualize(path)
        else:
            print("Путь не найден!")
            # Визуализируем только карту
            hex_map.visualize()


def custom_map_demo():
    """
    Демонстрирует создание собственной карты и поиск пути на ней.
    """
    print("\n=== ДЕМОНСТРАЦИЯ ПОЛЬЗОВАТЕЛЬСКОЙ КАРТЫ ===")
    print("Создание карты и поиск пути для всех рас")
    
    # Текстовое представление карты
    # 0 - равнина, 1 - лес, 3 - горы, 4 - вода, 9 - дорога, 14 - старт, 15 - финиш
    map_text = """
     0 0 0 0 0 0 0
    0 14 0 1 0 3 0 0
     0 0 1 1 3 3 0
    0 9 9 1 0 3 0 0
     9 1 0 0 0 0 0
    0 9 0 0 4 4 0 0
     9 0 0 4 4 15 0
    """
    
    # Создаем карту из текста
    hex_map = HexMap.load_from_text(map_text)
    
    # Создаем разные расы
    races = [Human(), Elf(), Dwarf(), Orc()]
    
    # Находим путь для каждой расы и отображаем результаты
    for race in races:
        print(f"\nПоиск пути для расы: {race.name}")
        
        # Если старт или финиш не определены, пропускаем
        if not hex_map.start or not hex_map.end:
            print("Ошибка: не определены точки старта и/или финиша на карте")
            continue
        
        path, cost = hex_map.find_path(hex_map.start, hex_map.end, race)
        
        if path:
            print(f"Путь найден! Стоимость: {cost:.2f}")
            print(f"Количество шагов: {len(path) - 1}")
            
            # Визуализируем карту и путь
            hex_map.visualize(path)
        else:
            print("Путь не найден!")
            # Визуализируем только карту
            hex_map.visualize()


def main():
    """
    Главная функция для запуска демонстрации.
    """
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Разбор аргументов командной строки
    parser = argparse.ArgumentParser(description='Демонстрация гексагональной карты и рас')
    parser.add_argument('--demo', choices=[mode.value for mode in DemoMode], 
                       default=DemoMode.SIMPLE.value, help='Режим демонстрации')
    args = parser.parse_args()
    
    # Выбор режима демонстрации
    demo_mode = args.demo
    
    # Запуск выбранного режима демонстрации
    if demo_mode == DemoMode.SIMPLE.value or demo_mode == DemoMode.ALL.value:
        simple_demo()
        
    if demo_mode == DemoMode.COMPARISON.value or demo_mode == DemoMode.ALL.value:
        comparison_demo()
        
    if demo_mode == DemoMode.CUSTOM_MAP.value or demo_mode == DemoMode.ALL.value:
        custom_map_demo()
    
    print("\nДемонстрация завершена!")


if __name__ == "__main__":
    main() 