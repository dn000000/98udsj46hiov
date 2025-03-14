"""
@package pathfinding
@brief Пакет для алгоритмов поиска пути.

@details
Содержит реализации различных алгоритмов поиска пути на гексагональной карте,
включая A*, Dijkstra и BFS. Алгоритмы учитывают расовые модификаторы
стоимости передвижения по разным типам местности.

Ключевые модули:
- hex_a_star: Реализация алгоритма A* для гексагональной карты
"""

from .hex_a_star import find_path 