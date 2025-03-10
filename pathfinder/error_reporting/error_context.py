"""
@file error_context.py
@brief Модуль для хранения контекста ошибки.

@details
Этот модуль содержит класс ErrorContext, который используется для
хранения контекстной информации об ошибке (модуль, функция, строка,
переменные и т.д.).
"""

import inspect
import os
import sys
import traceback

class ErrorContext:
    """
    @brief Класс для хранения контекста ошибки.
    
    @details
    Класс ErrorContext используется для хранения контекстной информации
    об ошибке, такой как модуль, функция, строка, переменные и т.д.
    Эта информация может быть использована для отладки и отправки
    отчетов об ошибках.
    """
    
    def __init__(self, module=None, function=None, line=None, variables=None, exception=None):
        """
        @brief Инициализация объекта ErrorContext.
        
        @param module Имя модуля, в котором произошла ошибка.
        @param function Имя функции, в которой произошла ошибка.
        @param line Номер строки, на которой произошла ошибка.
        @param variables Словарь переменных, актуальных на момент ошибки.
        @param exception Объект исключения, если ошибка связана с исключением.
        
        @code
        # Пример использования:
        from pathfinder.error_reporting.error_context import ErrorContext
        
        # Создаем контекст ошибки вручную
        error_context = ErrorContext(
            module="pathfinder.maze",
            function="get_path",
            line=42,
            variables={"start": (0, 0), "end": (10, 10)}
        )
        
        # Или автоматически из исключения
        try:
            # Какой-то код, который может вызвать исключение
            result = 1 / 0
        except Exception as e:
            error_context = ErrorContext.from_exception(e)
            # Используем контекст для отчета об ошибке
        @endcode
        """
        self.module = module
        self.function = function
        self.line = line
        self.variables = variables or {}
        self.exception = exception
        self.traceback = None
        
        if exception:
            self.traceback = traceback.format_exception(
                type(exception), exception, exception.__traceback__
            )
    
    @classmethod
    def from_exception(cls, exception, include_locals=True):
        """
        @brief Создает объект ErrorContext из исключения.
        
        @param exception Объект исключения.
        @param include_locals Включать ли локальные переменные в контекст.
        
        @return Объект ErrorContext, содержащий информацию об исключении.
        """
        if not exception:
            return cls()
            
        # Получаем информацию о стеке вызовов
        tb = exception.__traceback__
        frame = None
        
        while tb:
            frame = tb.tb_frame
            tb = tb.tb_next
            
        if not frame:
            return cls(exception=exception)
            
        # Извлекаем информацию из фрейма
        module = frame.f_globals.get('__name__', 'unknown')
        function = frame.f_code.co_name
        line = frame.f_lineno
        
        # Извлекаем локальные переменные, если это требуется
        variables = {}
        if include_locals:
            for key, value in frame.f_locals.items():
                # Пропускаем приватные переменные и объекты, которые нельзя сериализовать
                if not key.startswith('_') and not inspect.ismodule(value) and not inspect.isclass(value) and not inspect.isfunction(value) and not inspect.ismethod(value):
                    try:
                        # Пытаемся преобразовать значение в строку
                        str_value = str(value)
                        # Ограничиваем длину строки
                        if len(str_value) > 1000:
                            str_value = str_value[:1000] + "..."
                        variables[key] = str_value
                    except:
                        # Если не удалось преобразовать значение, пропускаем его
                        pass
        
        return cls(module=module, function=function, line=line, variables=variables, exception=exception)
    
    @classmethod
    def current(cls, include_locals=True):
        """
        @brief Создает объект ErrorContext для текущего контекста выполнения.
        
        @param include_locals Включать ли локальные переменные в контекст.
        
        @return Объект ErrorContext, содержащий информацию о текущем контексте.
        """
        # Получаем информацию о текущем фрейме
        frame = inspect.currentframe().f_back
        
        if not frame:
            return cls()
            
        # Извлекаем информацию из фрейма
        module = frame.f_globals.get('__name__', 'unknown')
        function = frame.f_code.co_name
        line = frame.f_lineno
        
        # Извлекаем локальные переменные, если это требуется
        variables = {}
        if include_locals:
            for key, value in frame.f_locals.items():
                # Пропускаем приватные переменные и объекты, которые нельзя сериализовать
                if not key.startswith('_') and not inspect.ismodule(value) and not inspect.isclass(value) and not inspect.isfunction(value) and not inspect.ismethod(value):
                    try:
                        # Пытаемся преобразовать значение в строку
                        str_value = str(value)
                        # Ограничиваем длину строки
                        if len(str_value) > 1000:
                            str_value = str_value[:1000] + "..."
                        variables[key] = str_value
                    except:
                        # Если не удалось преобразовать значение, пропускаем его
                        pass
        
        return cls(module=module, function=function, line=line, variables=variables)
    
    def to_dict(self):
        """
        @brief Преобразует контекст ошибки в словарь.
        
        @return Словарь, содержащий информацию о контексте ошибки.
        """
        result = {
            "module": self.module,
            "function": self.function,
            "line": self.line,
            "variables": self.variables
        }
        
        if self.exception:
            result["exception"] = {
                "type": type(self.exception).__name__,
                "message": str(self.exception)
            }
            
        if self.traceback:
            result["traceback"] = self.traceback
            
        return result
    
    def __str__(self):
        """
        @brief Возвращает строковое представление контекста ошибки.
        
        @return Строка, содержащая информацию о контексте ошибки.
        """
        result = f"ErrorContext(module={self.module}, function={self.function}, line={self.line})"
        
        if self.exception:
            result += f", exception={type(self.exception).__name__}: {self.exception}"
            
        return result 