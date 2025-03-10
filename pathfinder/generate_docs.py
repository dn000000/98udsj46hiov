#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для генерации документации с помощью Doxygen.

Этот скрипт проверяет наличие установленного Doxygen, запускает
генерацию документации и открывает сгенерированную документацию
в браузере.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_doxygen_installed():
    """
    Проверяет, установлен ли Doxygen в системе.
    
    Returns:
        bool: True, если Doxygen установлен, иначе False.
    """
    try:
        result = subprocess.run(
            ["doxygen", "--version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def generate_documentation():
    """
    Генерирует документацию с помощью Doxygen.
    
    Returns:
        bool: True, если документация успешно сгенерирована, иначе False.
    """
    # Получаем текущую директорию проекта
    project_dir = Path(__file__).parent
    
    # Проверяем наличие файла конфигурации
    doxyfile_path = project_dir / "doxyfile"
    if not doxyfile_path.exists():
        print(f"Ошибка: Файл конфигурации {doxyfile_path} не найден.")
        return False
    
    # Создаем директорию для документации, если она не существует
    output_dir = project_dir / "docs" / "doxygen"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Запускаем Doxygen
    print(f"Запуск Doxygen для генерации документации...")
    try:
        result = subprocess.run(
            ["doxygen", str(doxyfile_path)], 
            cwd=str(project_dir),
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            print(f"Ошибка при генерации документации:")
            print(result.stderr)
            return False
        
        print("Документация успешно сгенерирована!")
        return True
    except Exception as e:
        print(f"Ошибка при запуске Doxygen: {str(e)}")
        return False

def open_documentation():
    """
    Открывает сгенерированную документацию в браузере.
    
    Returns:
        bool: True, если документация успешно открыта, иначе False.
    """
    # Получаем путь к сгенерированной документации
    project_dir = Path(__file__).parent
    index_path = project_dir / "docs" / "doxygen" / "html" / "index.html"
    
    if not index_path.exists():
        print(f"Ошибка: Файл документации {index_path} не найден.")
        return False
    
    # Открываем документацию в браузере
    print(f"Открытие документации в браузере...")
    try:
        # Преобразуем путь в URL-формат для корректной работы в разных ОС
        file_url = "file://" + str(index_path.absolute()).replace("\\", "/")
        webbrowser.open(file_url)
        return True
    except Exception as e:
        print(f"Ошибка при открытии документации: {str(e)}")
        return False

def main():
    """
    Основная функция скрипта.
    """
    print("=== Генерация документации Doxygen ===")
    
    # Проверяем наличие Doxygen
    if not check_doxygen_installed():
        print("Ошибка: Doxygen не установлен в системе.")
        print("Установите Doxygen с помощью Chocolatey (Windows) или apt/brew (Linux/macOS):")
        print("  - Windows: choco install doxygen.install")
        print("  - Linux: sudo apt-get install doxygen")
        print("  - macOS: brew install doxygen")
        sys.exit(1)
    
    # Генерируем документацию
    if not generate_documentation():
        print("Генерация документации завершилась с ошибками.")
        sys.exit(1)
    
    # Открываем документацию в браузере
    if "--no-open" not in sys.argv:
        if not open_documentation():
            print("Не удалось открыть документацию в браузере.")
    
    print("=== Генерация документации завершена ===")

if __name__ == "__main__":
    main() 