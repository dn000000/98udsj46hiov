"""
PathFinder - пакет для поиска оптимального пути в лабиринте.

Этот пакет содержит модули для:
- Представления лабиринта и его элементов
- Алгоритма поиска пути
- Визуализации результатов
- Поиска равноудаленной точки от всех героев
- Интеграции с системой управления ошибками
"""

# Экспортируем основные классы и функции для удобства импорта
from .maze import Maze
from .pathfinder import PathFinder
from .visualizer import MazeVisualizer
from .equidistant_finder import EquidistantFinder

# Версия пакета
__version__ = '1.0.0' 