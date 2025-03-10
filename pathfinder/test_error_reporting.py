#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тестовый скрипт для демонстрации работы системы отчетов об ошибках.

Этот скрипт показывает различные способы использования системы
отчетов об ошибках Bugzilla в проекте PathFinder.
"""

import sys
import os
import time
import traceback
from pathlib import Path

# Добавляем директорию src в путь для импорта
sys.path.append(str(Path(__file__).parent / "src"))

# Импортируем модуль для отчетов об ошибках
import error_reporter


# Функция с декоратором для перехвата исключений
@error_reporter.catch_and_report(component="Testing", additional_info="Тестовая функция с декоратором")
def test_with_decorator():
    """
    Тестовая функция с декоратором для перехвата исключений.
    """
    print("Вызов функции с декоратором для перехвата исключений")
    print("Генерация исключения для проверки...")
    raise ValueError("Тестовое исключение из функции с декоратором")


# Функция для тестирования контекстного менеджера
def test_with_context_manager():
    """
    Тестовая функция с использованием контекстного менеджера для перехвата исключений.
    """
    print("Использование контекстного менеджера для перехвата исключений")
    print("Генерация исключения для проверки...")
    
    with error_reporter.ErrorContext("Testing", "Тестовая ошибка в контекстном менеджере"):
        # Этот код вызовет исключение, которое будет перехвачено и отправлено в Bugzilla
        result = 1 / 0  # ZeroDivisionError


# Функция для тестирования прямого вызова report_error
def test_direct_reporting():
    """
    Тестовая функция с прямым вызовом report_error.
    """
    print("Тестирование прямого вызова report_error()")
    
    try:
        # Генерируем ошибку
        print("Генерация исключения для проверки...")
        some_value = None
        result = len(some_value)  # TypeError
    except Exception as e:
        # Перехватываем ошибку и отправляем отчет
        print(f"Перехвачено исключение: {type(e).__name__}: {str(e)}")
        bug_id = error_reporter.report_error(
            e,
            component="Testing",
            additional_info="Тестовая ошибка с прямым вызовом report_error"
        )
        
        if bug_id:
            print(f"Отчет об ошибке успешно отправлен, ID: {bug_id}")
        else:
            print("Не удалось отправить отчет об ошибке")


def main():
    """
    Основная функция для запуска тестов.
    """
    print("=== Тестирование системы отчетов об ошибках ===")
    
    # Инициализируем систему отчетов
    print("\n1. Инициализация системы отчетов об ошибках")
    headless = "--visible" not in sys.argv
    success = error_reporter.initialize(enabled=True, headless=headless)
    
    if success:
        print("✅ Система отчетов об ошибках успешно инициализирована")
        
        # Проводим различные тесты с перехватом исключений
        tests = [
            ("Тест с декоратором", test_with_decorator),
            ("Тест с контекстным менеджером", test_with_context_manager),
            ("Тест с прямым вызовом report_error", test_direct_reporting)
        ]
        
        for i, (name, test_func) in enumerate(tests, start=2):
            print(f"\n{i}. {name}")
            try:
                test_func()
            except Exception as e:
                print(f"❌ Тест завершился с ошибкой: {type(e).__name__}: {str(e)}")
                traceback.print_exc()
            
            # Пауза между тестами
            if i < len(tests) + 1:
                print("\nПауза 3 секунды перед следующим тестом...")
                time.sleep(3)
    else:
        print("❌ Не удалось инициализировать систему отчетов об ошибках")
    
    # Завершаем работу с системой отчетов
    print("\nЗавершение работы системы отчетов об ошибках")
    error_reporter.shutdown()
    
    print("\n=== Тестирование завершено ===")


if __name__ == "__main__":
    main() 