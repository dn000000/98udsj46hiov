"""
Модуль для визуализации лабиринта и пути.

Этот модуль предоставляет функциональность для визуализации
лабиринта и найденного пути с использованием библиотеки matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np


class MazeVisualizer:
    """
    Класс для визуализации лабиринта и пути.
    """
    
    def __init__(self, maze):
        """
        Инициализация визуализатора.
        
        Args:
            maze: Объект Maze, представляющий лабиринт.
        """
        self.maze = maze
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
    
    def draw_maze(self):
        """
        Отрисовывает лабиринт.
        """
        # Создаем матрицу цветов
        grid = np.zeros((self.maze.height, self.maze.width))
        
        # Заполняем матрицу
        for i in range(self.maze.height):
            for j in range(self.maze.width):
                cell = self.maze.grid[i][j]
                if cell == 1:
                    grid[i][j] = 1  # Стена
                elif isinstance(cell, str) and cell.isdigit():
                    grid[i][j] = 2  # Герой
                elif cell == 'F':
                    grid[i][j] = 3  # Конец
                else:
                    grid[i][j] = 0  # Проход
        
        # Создаем colormap
        colors = ['white', 'black', 'green', 'red']
        cmap = mcolors.ListedColormap(colors)
        
        # Отрисовываем лабиринт
        self.ax.imshow(grid, cmap=cmap)
        
        # Добавляем сетку
        self.ax.grid(color='gray', linestyle='-', linewidth=0.5)
        self.ax.set_xticks(np.arange(-0.5, self.maze.width, 1), minor=True)
        self.ax.set_yticks(np.arange(-0.5, self.maze.height, 1), minor=True)
        
        # Настраиваем оси
        self.ax.set_xticks(np.arange(0, self.maze.width, 1))
        self.ax.set_yticks(np.arange(0, self.maze.height, 1))
        self.ax.tick_params(axis='both', which='both', length=0)
        
        # Подписи для героев
        for i in range(self.maze.height):
            for j in range(self.maze.width):
                cell = self.maze.grid[i][j]
                if isinstance(cell, str) and cell.isdigit():
                    self.ax.text(j, i, cell, ha='center', va='center', color='white', fontsize=12, fontweight='bold')
                elif cell == 'F':
                    self.ax.text(j, i, 'F', ha='center', va='center', color='white', fontsize=12, fontweight='bold')
    
    def draw_path(self, path, color='blue', linewidth=2, markersize=8):
        """
        Отрисовывает путь на лабиринте.
        
        Args:
            path (list): Список кортежей (row, col), представляющих путь.
            color (str): Цвет пути.
            linewidth (int): Ширина линии.
            markersize (int): Размер маркера.
        """
        if not path:
            return
        
        # Извлекаем координаты
        rows, cols = zip(*path)
        
        # Отрисовываем путь
        self.ax.plot(cols, rows, 'o-', color=color, linewidth=linewidth, markersize=markersize)
    
    def draw_equidistant_point(self, point, paths=None):
        """
        Отрисовывает равноудаленную точку и пути к ней от всех героев.
        
        Args:
            point (tuple): Кортеж (row, col), представляющий равноудаленную точку.
            paths (dict): Словарь {hero_id: path} с путями от героев к точке.
        """
        if not point:
            return
        
        row, col = point
        
        # Отрисовываем точку
        self.ax.plot(col, row, 'o', color='purple', markersize=12)
        self.ax.text(col, row, 'E', ha='center', va='center', color='white', fontsize=12, fontweight='bold')
        
        # Отрисовываем пути от героев к точке, если предоставлены
        if paths:
            colors = ['blue', 'red', 'green', 'orange', 'cyan', 'magenta', 'yellow', 'brown', 'pink']
            for i, (hero_id, path) in enumerate(paths.items()):
                if path:
                    color = colors[i % len(colors)]
                    self.draw_path(path, color=color)
    
    def draw_distance_map(self, point, distances):
        """
        Отрисовывает тепловую карту расстояний от точки.
        
        Args:
            point (tuple): Кортеж (row, col), представляющий точку.
            distances (dict): Словарь {position: distance} с расстояниями.
        """
        if not point or not distances:
            return
        
        # Создаем матрицу расстояний
        distance_grid = np.full((self.maze.height, self.maze.width), np.nan)
        
        for (i, j), dist in distances.items():
            distance_grid[i, j] = dist
        
        # Создаем отдельную фигуру для тепловой карты
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Отрисовываем тепловую карту
        heatmap = ax.imshow(distance_grid, cmap='hot_r')
        
        # Добавляем цветовую шкалу
        plt.colorbar(heatmap, ax=ax, label='Расстояние')
        
        # Настраиваем оси
        ax.set_xticks(np.arange(0, self.maze.width, 1))
        ax.set_yticks(np.arange(0, self.maze.height, 1))
        
        # Добавляем сетку
        ax.grid(color='white', linestyle='-', linewidth=0.5)
        ax.set_title(f'Тепловая карта расстояний от точки {point}')
        
        return fig
    
    def save(self, filename='maze_solution.png'):
        """
        Сохраняет визуализацию в файл.
        
        Args:
            filename (str): Имя файла для сохранения.
        """
        self.fig.savefig(filename)
    
    def show(self):
        """
        Отображает визуализацию.
        """
        plt.show() 