"""
@file error_reporter.py
@brief Модуль для отслеживания ошибок и отправки отчетов в Bugzilla.

@details
Этот модуль предоставляет функционал для перехвата исключений и
автоматической отправки отчетов об ошибках в систему Bugzilla.

Модуль обеспечивает три основных способа отправки отчетов об ошибках:
1. Использование декоратора @catch_and_report для функций
2. Использование контекстного менеджера ErrorContext для блоков кода
3. Прямой вызов функции report_error для отправки отчета вручную

@author Разработчики проекта PathFinder
@date 2025-03-10
@version 1.0
"""

import sys
import traceback
import logging
import functools
import inspect
import os
import time
import threading
from typing import Optional, Callable, Any, Dict, List, Tuple, Union

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

## @var _BUGZILLA_ENABLED
## @brief Флаг, указывающий, включена ли система отчетов об ошибках.
_BUGZILLA_ENABLED = False

## @var _BUGZILLA_CLIENT
## @brief Глобальный экземпляр клиента Bugzilla.
_BUGZILLA_CLIENT = None

## @var _DEFAULT_CREDENTIALS
## @brief Учетные данные по умолчанию для Bugzilla.
_DEFAULT_CREDENTIALS = {
    "username": "developer@example.com",
    "password": "developer123"
}

def _lazy_import_bugzilla_client():
    """
    @brief Ленивый импорт BugzillaRestClient для избежания циклических зависимостей.
    
    @details
    Эта функция пытается импортировать BugzillaRestClient сначала как 
    относительный импорт, затем как абсолютный. Ленивый импорт помогает
    избежать циклических зависимостей между модулями.
    
    @return Класс BugzillaRestClient или None, если не удалось импортировать.
    """
    try:
        # Сначала пробуем относительный импорт (в рамках пакета)
        try:
            from . import bugzilla_rest_client
            return bugzilla_rest_client.BugzillaRestClient
        except (ImportError, ValueError):
            # Затем абсолютный импорт для использования вне пакета
            from bugzilla_rest_client import BugzillaRestClient
            return BugzillaRestClient
    except ImportError as e:
        logger.warning(f"Не удалось импортировать BugzillaRestClient: {str(e)}")
        return None

def initialize(enabled: bool = True, 
               credentials: Optional[Dict[str, str]] = None, 
               headless: bool = True) -> bool:
    """
    @brief Инициализация системы отчетов об ошибках.
    
    @details
    Эта функция инициализирует систему отчетов об ошибках, создавая
    и настраивая клиент для взаимодействия с Bugzilla. Если enabled=False,
    система отчетов отключается. Если credentials=None, используются
    учетные данные по умолчанию из _DEFAULT_CREDENTIALS.
    
    @param enabled Включить отправку отчетов в Bugzilla (по умолчанию True).
    @param credentials Словарь с учетными данными для Bugzilla. 
                      Должен содержать "username" и "password".
    @param headless Запускать браузер в фоновом режиме без GUI (по умолчанию True).
        
    @return True, если инициализация прошла успешно, иначе False.
    
    @code
    # Пример использования:
    from error_reporter import initialize, report_error
    
    # Инициализация с учетными данными по умолчанию
    if initialize():
        print("Система отчетов об ошибках успешно инициализирована")
    
    # Инициализация с пользовательскими учетными данными
    custom_credentials = {
        "username": "user@example.com",
        "password": "password123"
    }
    initialize(enabled=True, credentials=custom_credentials, headless=False)
    @endcode
    """
    global _BUGZILLA_ENABLED, _BUGZILLA_CLIENT
    
    if not enabled:
        _BUGZILLA_ENABLED = False
        return True
    
    creds = credentials or _DEFAULT_CREDENTIALS
    
    try:
        # Ленивый импорт для избежания циклических зависимостей
        BugzillaRestClient = _lazy_import_bugzilla_client()
        
        if BugzillaRestClient:
            # Создаем клиент и пробуем авторизоваться
            client = BugzillaRestClient(headless=headless)
            
            if client.login(creds["username"], creds["password"]):
                _BUGZILLA_CLIENT = client
                _BUGZILLA_ENABLED = True
                logger.info("Система отчетов об ошибках Bugzilla успешно инициализирована")
                return True
            else:
                logger.warning("Не удалось авторизоваться в Bugzilla")
                client.logout()  # Закрываем браузер, чтобы не оставлять его открытым
        else:
            logger.warning("Не удалось загрузить модуль Bugzilla")
        
        _BUGZILLA_ENABLED = False
        return False
    except Exception as e:
        logger.error(f"Ошибка при инициализации системы отчетов: {str(e)}")
        _BUGZILLA_ENABLED = False
        return False

def shutdown() -> None:
    """
    @brief Завершение работы системы отчетов об ошибках.
    
    @details
    Закрывает соединение с Bugzilla и освобождает ресурсы.
    Эту функцию следует вызывать при завершении работы приложения.
    
    @code
    # Пример использования:
    import atexit
    from error_reporter import initialize, shutdown
    
    # Инициализация системы отчетов
    initialize()
    
    # Регистрация функции завершения
    atexit.register(shutdown)
    @endcode
    """
    global _BUGZILLA_ENABLED, _BUGZILLA_CLIENT
    
    if _BUGZILLA_CLIENT:
        try:
            _BUGZILLA_CLIENT.logout()
        except Exception as e:
            logger.error(f"Ошибка при закрытии соединения с Bugzilla: {str(e)}")
        finally:
            _BUGZILLA_CLIENT = None
            _BUGZILLA_ENABLED = False

def report_error(error: Exception, 
                 component: str = "Core", 
                 additional_info: str = "") -> Optional[str]:
    """
    @brief Отправляет отчет об ошибке в Bugzilla.
    
    @details
    Эта функция создает отчет об ошибке в Bugzilla на основе переданного исключения.
    Отчет включает информацию о типе исключения, сообщение об ошибке, стек вызовов
    и дополнительную информацию, если она предоставлена.
    
    @param error Объект исключения.
    @param component Компонент, в котором произошла ошибка.
    @param additional_info Дополнительная информация об ошибке.
    
    @return ID созданной ошибки или None, если отчет не был отправлен.
    
    @code
    # Пример использования:
    from error_reporter import initialize, report_error
    
    # Инициализация системы отчетов
    initialize()
    
    # Отправка отчета об ошибке
    try:
        # Код, который может вызвать исключение
        result = 1 / 0
    except Exception as e:
        bug_id = report_error(e, component="Math", additional_info="Ошибка при вычислении")
        if bug_id:
            print(f"Отчет об ошибке отправлен, ID: {bug_id}")
    @endcode
    
    @warning Функция вернет None, если система отчетов не инициализирована или отключена.
    Для инициализации системы используйте функцию initialize().
    """
    if not _BUGZILLA_ENABLED or not _BUGZILLA_CLIENT:
        logger.warning("Система отчетов Bugzilla не инициализирована или отключена")
        return None
    
    try:
        # Получаем информацию о стеке вызовов
        exc_type, exc_value, exc_traceback = sys.exc_info()
        stack_trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # Формируем заголовок ошибки
        error_type = type(error).__name__
        error_message = str(error)
        summary = f"{error_type}: {error_message[:100]}"
        
        # Формируем описание ошибки
        description = f"""
### Описание ошибки
**Тип**: {error_type}
**Сообщение**: {error_message}

### Стек вызовов
```
{stack_trace}
```

### Дополнительная информация
{additional_info}

### Системная информация
- Дата и время: {time.strftime('%Y-%m-%d %H:%M:%S')}
- Python: {sys.version}
- Платформа: {sys.platform}
"""
        
        # Отправляем отчет в Bugzilla
        result = _BUGZILLA_CLIENT.create_bug(
            summary=summary,
            description=description,
            component=component
        )
        
        if result and result.get('status') == 'success':
            bug_id = result.get('bug', {}).get('id', 'unknown')
            logger.info(f"Отчет об ошибке успешно отправлен в Bugzilla, ID: {bug_id}")
            return bug_id
        else:
            logger.warning("Не удалось отправить отчет об ошибке в Bugzilla")
            return None
    except Exception as e:
        logger.error(f"Ошибка при отправке отчета об ошибке: {str(e)}")
        return None

def catch_and_report(component: str = "Core", 
                     additional_info: str = "") -> Callable:
    """
    @brief Декоратор для перехвата исключений и отправки отчетов в Bugzilla.
    
    @details
    Этот декоратор оборачивает функцию, перехватывает любые возникающие исключения,
    отправляет отчет об ошибке в Bugzilla и затем пробрасывает исключение дальше.
    Он не изменяет поведение функции, но добавляет отправку отчетов об ошибках.
    
    @param component Компонент, в котором произошла ошибка.
    @param additional_info Дополнительная информация об ошибке.
    
    @return Декоратор функции.
    
    @code
    # Пример использования:
    from error_reporter import catch_and_report
    
    @catch_and_report(component="Algorithm", additional_info="Ошибка в алгоритме поиска пути")
    def find_path(graph, start, end):
        # Код алгоритма
        if start not in graph:
            raise ValueError(f"Начальная точка {start} не найдена в графе")
        # ...
    @endcode
    """
    def decorator(func):
        """
        @brief Внутренняя функция декоратора.
        
        @param func Декорируемая функция.
        @return Обертка функции.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """
            @brief Обертка функции, которая перехватывает исключения.
            
            @details
            Выполняет декорируемую функцию, перехватывает возникающие исключения,
            отправляет отчет об ошибке в Bugzilla и пробрасывает исключение дальше.
            
            @param args Позиционные аргументы для декорируемой функции.
            @param kwargs Именованные аргументы для декорируемой функции.
            @return Результат выполнения декорируемой функции.
            @throws Любое исключение, возникшее в декорируемой функции.
            """
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Получаем контекст вызова
                call_context = f"Функция: {func.__name__}, Модуль: {func.__module__}"
                info = f"{additional_info}\n\n### Контекст вызова\n{call_context}"
                
                # Отправляем отчет об ошибке
                bug_id = report_error(e, component, info)
                
                # Перебрасываем исключение дальше
                raise
        return wrapper
    return decorator

class ErrorContext:
    """
    @brief Контекстный менеджер для перехвата исключений и отправки отчетов в Bugzilla.
    
    @details
    Этот класс реализует контекстный менеджер (с использованием протокола with),
    который перехватывает исключения в блоке кода и автоматически отправляет
    отчеты об ошибках в Bugzilla, не подавляя само исключение.
    
    @code
    # Пример использования:
    from error_reporter import ErrorContext
    
    def process_data(data):
        with ErrorContext("UI", "Ошибка при обработке данных"):
            # Код, который может вызвать исключение
            result = data['key'] / 0  # Потенциальная ошибка
            return result
    @endcode
    """
    
    def __init__(self, component: str = "Core", additional_info: str = ""):
        """
        @brief Инициализация контекстного менеджера.
        
        @param component Компонент, в котором произошла ошибка.
        @param additional_info Дополнительная информация об ошибке.
        """
        self.component = component
        self.additional_info = additional_info
    
    def __enter__(self):
        """
        @brief Метод входа в контекстный блок.
        
        @return Экземпляр контекстного менеджера.
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        @brief Метод выхода из контекстного блока.
        
        @details
        Этот метод вызывается при выходе из блока with. Если произошло исключение,
        отправляет отчет об ошибке в Bugzilla и позволяет исключению распространяться дальше.
        
        @param exc_type Тип исключения или None, если исключение не возникло.
        @param exc_val Значение исключения или None.
        @param exc_tb Трассировка исключения или None.
        
        @return False, чтобы не подавлять исключение, или True, если исключение подавляется.
        """
        if exc_type is not None:
            # Отправляем отчет об ошибке
            caller_frame = inspect.currentframe().f_back
            call_context = f"Файл: {caller_frame.f_code.co_filename}, Строка: {caller_frame.f_lineno}"
            info = f"{self.additional_info}\n\n### Контекст вызова\n{call_context}"
            
            report_error(exc_val, self.component, info)
            
            # Исключение будет проброшено дальше
            return False  # Не подавляем исключение

# Инициализация автоматически при импорте модуля
def _auto_initialize():
    """
    Автоматическая инициализация системы отчетов при импорте модуля,
    если установлена переменная окружения BUGZILLA_ENABLED.
    """
    if os.environ.get('BUGZILLA_ENABLED', '').lower() in ('true', '1', 't', 'yes'):
        username = os.environ.get('BUGZILLA_USERNAME', _DEFAULT_CREDENTIALS['username'])
        password = os.environ.get('BUGZILLA_PASSWORD', _DEFAULT_CREDENTIALS['password'])
        headless = os.environ.get('BUGZILLA_HEADLESS', '').lower() not in ('false', '0', 'f', 'no')
        
        credentials = {
            "username": username,
            "password": password
        }
        
        # Запускаем инициализацию в отдельном потоке, чтобы не блокировать импорт
        def init_thread():
            initialize(True, credentials, headless)
        
        threading.Thread(target=init_thread).start()

# Автоинициализация при наличии переменных окружения
_auto_initialize() 