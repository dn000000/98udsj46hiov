"""
@file terrain_visualizer.py
@brief Модуль для визуализации лабиринта с различными типами местности.

@details
Этот модуль содержит класс TerrainVisualizer, который расширяет
базовый класс MazeVisualizer и добавляет возможность визуализации
различных типов местности с использованием цветовой кодировки.
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from matplotlib.cm import get_cmap

class TerrainVisualizer:
    """
    @brief Класс для визуализации лабиринта с различными типами местности.
    
    @details
    Класс TerrainVisualizer предоставляет методы для визуализации лабиринта
    с различными типами местности, отображения путей и точек сбора.
    """
    
    # Цветовая карта для разных типов местности
    TERRAIN_COLORS = {
        '.': '#FFFFFF',  # Дорога - белый
        ',': '#90EE90',  # Трава - светло-зеленый
        '#': '#000000',  # Стена - черный
        '~': '#00BFFF',  # Вода - голубой
        '*': '#8B4513',  # Грязь - коричневый
        '=': '#A9A9A9',  # Камни - серый
        '^': '#808000',  # Болото - темно-оливковый
        'S': '#FF0000',  # Начальная точка - красный
        'E': '#00FF00',  # Конечная точка - зеленый
    }
    
    # Соответствие типов местности их названиям для легенды
    TERRAIN_NAMES = {
        '.': 'Дорога (1)',
        ',': 'Трава (2)',
        '#': 'Стена (∞)',
        '~': 'Вода (5)',
        '*': 'Грязь (3)',
        '=': 'Камни (4)',
        '^': 'Болото (7)',
        'S': 'Старт',
        'E': 'Финиш',
    }
    
    def __init__(self, maze, figsize=(10, 10)):
        """
        @brief Инициализация объекта TerrainVisualizer.
        
        @param maze Объект TerrainMaze, представляющий лабиринт с типами местности.
        @param figsize Размер фигуры matplotlib для отображения лабиринта.
        
        @code
        # Пример использования:
        from terrain_maze import TerrainMaze
        from terrain_visualizer import TerrainVisualizer
        
        # Создаем лабиринт с разными типами местности
        maze = TerrainMaze()
        
        # Создаем объект для визуализации
        visualizer = TerrainVisualizer(maze)
        
        # Отображаем лабиринт
        visualizer.display_maze()
        @endcode
        """
        self.maze = maze
        self.figsize = figsize
        
    def get_colored_maze(self):
        """
        @brief Создает цветовую карту лабиринта.
        
        @return Двумерный массив numpy с цветами для каждой ячейки лабиринта.
        """
        grid = self.maze.get_grid()
        height, width = len(grid), len(grid[0])
        
        # Создаем массив для цветов
        colored_maze = np.zeros((height, width, 3))
        
        # Заполняем массив цветами в зависимости от типа местности
        for i in range(height):
            for j in range(width):
                cell_type = grid[i][j]
                if cell_type in self.TERRAIN_COLORS:
                    color = mcolors.to_rgb(self.TERRAIN_COLORS[cell_type])
                else:
                    # Если тип местности не определен, используем серый цвет
                    color = mcolors.to_rgb('#CCCCCC')
                    
                colored_maze[i, j] = color
        
        return colored_maze
        
    def display_maze(self, title="Лабиринт с различными типами местности"):
        """
        @brief Отображает лабиринт с различными типами местности.
        
        @param title Заголовок для графического изображения.
        """
        colored_maze = self.get_colored_maze()
        
        fig, ax = plt.subplots(figsize=self.figsize)
        ax.imshow(colored_maze, interpolation='nearest')
        
        # Добавляем сетку для более четкого отображения ячеек
        ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=0.5)
        ax.set_xticks(np.arange(-0.5, len(self.maze.get_grid()[0]), 1), minor=True)
        ax.set_yticks(np.arange(-0.5, len(self.maze.get_grid()), 1), minor=True)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.tick_params(axis='both', which='both', length=0)
        
        # Добавляем заголовок
        plt.title(title)
        
        # Добавляем легенду
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=self.TERRAIN_COLORS[key], 
                                edgecolor='black',
                                label=self.TERRAIN_NAMES[key]) 
                          for key in self.TERRAIN_NAMES]
        
        ax.legend(handles=legend_elements, loc='upper center', 
                 bbox_to_anchor=(0.5, -0.05), ncol=3, fontsize=8)
        
        plt.tight_layout()
        plt.show()
        
    def display_path(self, path, title="Оптимальный путь с учетом типов местности"):
        """
        @brief Отображает лабиринт с выделенным путем.
        
        @param path Список точек, представляющих путь.
        @param title Заголовок для графического изображения.
        """
        if not path:
            print("Путь не найден!")
            return
            
        colored_maze = self.get_colored_maze()
        
        # Отмечаем путь красным цветом
        for row, col in path:
            # Делаем путь более заметным, смешивая его с красным цветом
            colored_maze[row, col] = np.array([1.0, 0.0, 0.0])  # Красный
            
        fig, ax = plt.subplots(figsize=self.figsize)
        ax.imshow(colored_maze, interpolation='nearest')
        
        # Добавляем сетку
        ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=0.5)
        ax.set_xticks(np.arange(-0.5, len(self.maze.get_grid()[0]), 1), minor=True)
        ax.set_yticks(np.arange(-0.5, len(self.maze.get_grid()), 1), minor=True)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.tick_params(axis='both', which='both', length=0)
        
        # Добавляем заголовок
        plt.title(title)
        
        # Добавляем легенду
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=self.TERRAIN_COLORS[key], 
                                edgecolor='black',
                                label=self.TERRAIN_NAMES[key]) 
                          for key in self.TERRAIN_NAMES]
        
        legend_elements.append(Patch(facecolor='red', 
                                    edgecolor='black',
                                    label='Путь'))
        
        ax.legend(handles=legend_elements, loc='upper center', 
                 bbox_to_anchor=(0.5, -0.05), ncol=3, fontsize=8)
        
        plt.tight_layout()
        plt.show()
        
    def display_gathering_point(self, hero_positions, gathering_point, hero_speeds=None, 
                               title="Оптимальная точка сбора"):
        """
        @brief Отображает лабиринт с позициями героев и точкой сбора.
        
        @param hero_positions Список позиций героев.
        @param gathering_point Точка сбора.
        @param hero_speeds Список скоростей передвижения героев.
        @param title Заголовок для графического изображения.
        """
        if not gathering_point:
            print("Точка сбора не найдена!")
            return
            
        colored_maze = self.get_colored_maze()
        
        fig, ax = plt.subplots(figsize=self.figsize)
        ax.imshow(colored_maze, interpolation='nearest')
        
        # Отмечаем позиции героев
        for i, (row, col) in enumerate(hero_positions):
            speed_text = f" (v={hero_speeds[i]})" if hero_speeds else ""
            plt.scatter(col, row, c='blue', s=100, marker='o', edgecolors='black')
            plt.text(col, row, f"H{i+1}{speed_text}", fontsize=8, ha='center', va='center', color='white')
            
        # Отмечаем точку сбора
        row, col = gathering_point
        plt.scatter(col, row, c='yellow', s=200, marker='*', edgecolors='black')
        plt.text(col, row, "Сбор", fontsize=10, ha='center', va='center', color='black')
        
        # Добавляем сетку
        ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=0.5)
        ax.set_xticks(np.arange(-0.5, len(self.maze.get_grid()[0]), 1), minor=True)
        ax.set_yticks(np.arange(-0.5, len(self.maze.get_grid()), 1), minor=True)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.tick_params(axis='both', which='both', length=0)
        
        # Добавляем заголовок
        plt.title(title)
        
        # Добавляем легенду
        from matplotlib.patches import Patch
        from matplotlib.lines import Line2D
        
        legend_elements = [Patch(facecolor=self.TERRAIN_COLORS[key], 
                                edgecolor='black',
                                label=self.TERRAIN_NAMES[key]) 
                          for key in self.TERRAIN_NAMES]
        
        legend_elements.extend([
            Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', 
                  markersize=10, label='Герой'),
            Line2D([0], [0], marker='*', color='w', markerfacecolor='yellow', 
                  markersize=15, label='Точка сбора')
        ])
        
        ax.legend(handles=legend_elements, loc='upper center', 
                 bbox_to_anchor=(0.5, -0.05), ncol=3, fontsize=8)
        
        plt.tight_layout()
        plt.show()
        
    def display_paths_to_gathering_point(self, hero_positions, gathering_point, 
                                        paths=None, hero_speeds=None,
                                        title="Пути героев к точке сбора"):
        """
        @brief Отображает лабиринт с путями героев к точке сбора.
        
        @param hero_positions Список позиций героев.
        @param gathering_point Точка сбора.
        @param paths Список путей для каждого героя. Если None, пути не отображаются.
        @param hero_speeds Список скоростей передвижения героев.
        @param title Заголовок для графического изображения.
        """
        if not gathering_point:
            print("Точка сбора не найдена!")
            return
            
        colored_maze = self.get_colored_maze()
        
        fig, ax = plt.subplots(figsize=self.figsize)
        ax.imshow(colored_maze, interpolation='nearest')
        
        # Определяем цвета для путей героев
        hero_colors = ['red', 'green', 'blue', 'orange', 'purple', 'cyan', 'magenta', 'yellow']
        
        # Отмечаем пути героев, если они предоставлены
        if paths:
            for i, path in enumerate(paths):
                if path:
                    color = hero_colors[i % len(hero_colors)]
                    for row, col in path:
                        plt.scatter(col, row, c=color, s=50, alpha=0.5)
        
        # Отмечаем позиции героев
        for i, (row, col) in enumerate(hero_positions):
            speed_text = f" (v={hero_speeds[i]})" if hero_speeds else ""
            plt.scatter(col, row, c=hero_colors[i % len(hero_colors)], s=100, marker='o', edgecolors='black')
            plt.text(col, row, f"H{i+1}{speed_text}", fontsize=8, ha='center', va='center', color='white')
            
        # Отмечаем точку сбора
        row, col = gathering_point
        plt.scatter(col, row, c='yellow', s=200, marker='*', edgecolors='black')
        plt.text(col, row, "Сбор", fontsize=10, ha='center', va='center', color='black')
        
        # Добавляем сетку
        ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=0.5)
        ax.set_xticks(np.arange(-0.5, len(self.maze.get_grid()[0]), 1), minor=True)
        ax.set_yticks(np.arange(-0.5, len(self.maze.get_grid()), 1), minor=True)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.tick_params(axis='both', which='both', length=0)
        
        # Добавляем заголовок
        plt.title(title)
        
        # Добавляем легенду для типов местности и героев
        from matplotlib.patches import Patch
        from matplotlib.lines import Line2D
        
        legend_elements = [Patch(facecolor=self.TERRAIN_COLORS[key], 
                                edgecolor='black',
                                label=self.TERRAIN_NAMES[key]) 
                          for key in self.TERRAIN_NAMES]
        
        # Добавляем героев в легенду
        for i in range(len(hero_positions)):
            speed_text = f" (v={hero_speeds[i]})" if hero_speeds else ""
            legend_elements.append(
                Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor=hero_colors[i % len(hero_colors)], 
                      markersize=10, label=f'Герой {i+1}{speed_text}')
            )
            
        legend_elements.append(
            Line2D([0], [0], marker='*', color='w', markerfacecolor='yellow', 
                  markersize=15, label='Точка сбора')
        )
        
        ax.legend(handles=legend_elements, loc='upper center', 
                 bbox_to_anchor=(0.5, -0.05), ncol=3, fontsize=8)
        
        plt.tight_layout()
        plt.show() 