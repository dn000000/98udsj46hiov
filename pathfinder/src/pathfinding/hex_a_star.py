"""
@file hex_a_star.py
@brief Реализация алгоритма A* для поиска пути на гексагональной карте.

@details
Этот модуль содержит реализацию алгоритма A* для поиска оптимального
пути на гексагональной карте с учетом расовых модификаторов стоимости
передвижения по разным типам местности.
"""

import heapq


def find_path(hex_map, start, end, race):
    """
    Находит оптимальный путь от начальной до конечной точки на гексагональной карте
    с учетом расовых модификаторов.
    
    @param hex_map: гексагональная карта (объект HexMap)
    @param start: начальная ячейка (объект HexCell)
    @param end: конечная ячейка (объект HexCell)
    @param race: раса, определяющая модификаторы движения (объект Race)
    @return: кортеж (путь, стоимость), где путь - список объектов HexCell от start до end,
             стоимость - общая стоимость пути. Если путь не найден, возвращает (None, float('inf'))
    """
    # Приоритетная очередь для открытых узлов (f_score, node)
    open_set = []
    # Словарь для хранения g_score для каждого узла
    g_score = {start: 0}
    # Словарь для хранения f_score для каждого узла
    f_score = {start: start.distance(end)}
    # Словарь для обратного пути
    came_from = {}
    # Множество закрытых узлов
    closed_set = set()
    
    # Добавляем начальную точку в открытый список
    heapq.heappush(open_set, (f_score[start], id(start), start))
    
    while open_set:
        # Получаем узел с наименьшей f-оценкой
        _, _, current = heapq.heappop(open_set)
        
        # Если достигли конечной точки
        if current == end:
            # Восстанавливаем путь
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path, g_score[end]
        
        # Добавляем текущий узел в закрытый список
        closed_set.add(current)
        
        # Обрабатываем всех соседей
        for neighbor in hex_map.get_neighbors(current):
            # Если сосед уже обработан
            if neighbor in closed_set:
                continue
            
            # Получаем стоимость перехода к этому соседу с учетом расы
            movement_cost = race.get_movement_cost(neighbor.terrain_type)
            
            # Если местность непроходима для этой расы
            if movement_cost == float('inf'):
                continue
            
            # Вычисляем новую g-оценку
            tentative_g_score = g_score[current] + movement_cost
            
            # Если сосед уже есть в открытом списке и новый путь не лучше
            if neighbor in g_score and tentative_g_score >= g_score[neighbor]:
                continue
            
            # Найден лучший путь к соседу
            came_from[neighbor] = current
            g_score[neighbor] = tentative_g_score
            f_score[neighbor] = tentative_g_score + neighbor.distance(end)
            
            # Добавляем соседа в открытый список
            heapq.heappush(open_set, (f_score[neighbor], id(neighbor), neighbor))
    
    # Путь не найден
    return None, float('inf') 