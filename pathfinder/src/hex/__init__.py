"""
@package hex
@brief Пакет для работы с гексагональной картой.

@details
Содержит классы и функции для представления гексагональной карты, ячеек и 
типов местности. Включает логику работы с гексагональными координатами,
вычисление расстояний и определение соседних ячеек.

Основные компоненты:
- HexCell: Класс для представления одной гексагональной ячейки
- HexTerrainType: Перечисление типов местности для гексагональной карты
- HexMap: Класс для представления гексагональной карты
"""

from .hex_coordinate import HexCoordinate
from .hex_cell import HexCell
from .hex_terrain_type import HexTerrainType
from .hex_map import HexMap 