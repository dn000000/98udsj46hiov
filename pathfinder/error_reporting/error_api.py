"""
@file error_api.py
@brief Модуль для интеграции с API для управления ошибками.

@details
Этот модуль предоставляет функциональность для отправки отчетов об ошибках
в систему управления ошибками (Bugzilla) и отправки уведомлений.
"""

import os
import sys
import logging
import json
import requests
from datetime import datetime

# Добавляем путь к корневому каталогу проекта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Пробуем импортировать модули через разные пути
try:
    from pathfinder.config.config import Config
    from pathfinder.notifications.telegram_notifier import TelegramNotifier
except ImportError:
    try:
        from config.config import Config
        from notifications.telegram_notifier import TelegramNotifier
    except ImportError:
        pass  # Будет обработано при конкретном использовании

class ErrorAPI:
    """
    @brief Класс для интеграции с API для управления ошибками.
    
    @details
    Класс ErrorAPI предоставляет методы для отправки отчетов об ошибках
    в систему управления ошибками (Bugzilla) и отправки уведомлений.
    """
    
    def __init__(self, bugzilla_url=None, api_key=None):
        """
        @brief Инициализация объекта ErrorAPI.
        
        @param bugzilla_url URL Bugzilla API. Если не указан, берется из переменной окружения BUGZILLA_URL.
        @param api_key API ключ для доступа к Bugzilla. Если не указан, берется из переменной окружения BUGZILLA_API_KEY.
        
        @code
        # Пример использования:
        from pathfinder.error_reporting.error_api import ErrorAPI
        from pathfinder.error_reporting.error_context import ErrorContext
        
        # Создаем объект для отправки отчетов об ошибках
        error_api = ErrorAPI()
        
        # Создаем контекст ошибки
        error_context = ErrorContext(
            module="pathfinder.maze",
            function="get_path",
            line=42,
            variables={"start": (0, 0), "end": (10, 10)}
        )
        
        # Отправляем отчет об ошибке
        error_api.report_error("Ошибка при поиске пути", "Не удалось найти путь между точками", error_context)
        @endcode
        """
        self.bugzilla_url = bugzilla_url or os.environ.get("BUGZILLA_URL")
        self.api_key = api_key or os.environ.get("BUGZILLA_API_KEY")
        
        if not self.bugzilla_url:
            logging.warning("Не указан URL Bugzilla API. Отчеты об ошибках не будут отправляться в Bugzilla.")
        
        if not self.api_key:
            logging.warning("Не указан API ключ для Bugzilla. Отчеты об ошибках не будут отправляться в Bugzilla.")
        
        # Загружаем конфигурацию
        self.config = Config()
        
        # Создаем объект для отправки уведомлений
        self.notifier = TelegramNotifier()
    
    def report_error(self, title, description, error_context=None):
        """
        @brief Отправляет отчет об ошибке.
        
        @param title Заголовок отчета.
        @param description Описание ошибки.
        @param error_context Контекст ошибки (объект ErrorContext).
        
        @return ID созданного отчета об ошибке или None, если отчет не был создан.
        """
        # Проверяем, включены ли отчеты об ошибках в конфигурации
        if not self.config.get("error_reporting.enabled", False):
            logging.info("Отправка отчетов об ошибках отключена в конфигурации.")
            return None
        
        # Отправляем отчет в Bugzilla, если это включено в конфигурации
        bug_id = None
        if self.config.get("error_reporting.report_to_bugzilla", False):
            bug_id = self._report_to_bugzilla(title, description, error_context)
        
        # Отправляем уведомление, если это включено в конфигурации
        if self.config.get("error_reporting.send_notifications", False):
            self.notifier.send_error_notification(title, description, error_context)
        
        return bug_id
    
    def _report_to_bugzilla(self, title, description, error_context=None):
        """
        @brief Отправляет отчет об ошибке в Bugzilla.
        
        @param title Заголовок отчета.
        @param description Описание ошибки.
        @param error_context Контекст ошибки (объект ErrorContext).
        
        @return ID созданного отчета об ошибке или None, если отчет не был создан.
        """
        # В демонстрационном режиме просто показываем, что сообщение пойдет в Bugzilla,
        # но не пытаемся отправить его через REST API
        if not self.bugzilla_url or not self.api_key:
            # Для демонстрации отображаем, что отчет был бы отправлен
            logging.info("Демонстрационный режим: Отчет об ошибке был бы отправлен в Bugzilla.")
            logging.info(f"Заголовок: {title}")
            logging.info(f"Описание: {description}")
            if error_context:
                logging.info(f"Контекст: {error_context}")
            return "demo-bug-id"
        
        try:
            # Формируем данные для отправки
            data = {
                "product": "PathFinder",
                "component": "Algorithm",
                "summary": title,
                "version": "1.0",
                "description": description,
                "op_sys": "All",
                "platform": "All",
                "priority": "P1",
                "severity": "normal"
            }
            
            # Добавляем информацию о контексте ошибки, если она предоставлена
            if error_context:
                data["description"] += f"\n\nКонтекст ошибки:\n"
                data["description"] += f"Модуль: {error_context.module}\n"
                data["description"] += f"Функция: {error_context.function}\n"
                data["description"] += f"Строка: {error_context.line}\n"
                
                if error_context.variables:
                    data["description"] += f"Переменные:\n"
                    for key, value in error_context.variables.items():
                        data["description"] += f"  {key}: {value}\n"
            
            # Добавляем информацию об окружении
            data["description"] += f"\nОкружение: {self.config.get_environment().value}"
            
            # Отправляем запрос к Bugzilla API
            headers = {
                "Content-Type": "application/json",
                "X-BUGZILLA-API-KEY": self.api_key
            }
            
            response = requests.post(
                f"{self.bugzilla_url}/rest/bug",
                headers=headers,
                data=json.dumps(data)
            )
            
            # Проверяем ответ
            if response.status_code == 201:
                bug_id = response.json().get("id")
                logging.info(f"Отчет об ошибке успешно отправлен в Bugzilla. ID: {bug_id}")
                return bug_id
            else:
                logging.error(f"Ошибка при отправке отчета в Bugzilla: {response.text}")
                return None
        except Exception as e:
            logging.error(f"Исключение при отправке отчета в Bugzilla: {e}")
            return None
    
    def add_comment(self, bug_id, comment):
        """
        @brief Добавляет комментарий к отчету об ошибке в Bugzilla.
        
        @param bug_id ID отчета об ошибке.
        @param comment Текст комментария.
        
        @return True, если комментарий успешно добавлен, иначе False.
        """
        if not self.bugzilla_url or not self.api_key:
            logging.info(f"Демонстрационный режим: комментарий был бы добавлен к отчету {bug_id}: {comment}")
            return True
        
        try:
            # Формируем данные для отправки
            data = {
                "comment": {
                    "body": comment
                }
            }
            
            # Отправляем запрос к Bugzilla API
            headers = {
                "Content-Type": "application/json",
                "X-BUGZILLA-API-KEY": self.api_key
            }
            
            response = requests.post(
                f"{self.bugzilla_url}/rest/bug/{bug_id}/comment",
                headers=headers,
                data=json.dumps(data)
            )
            
            # Проверяем ответ
            if response.status_code == 201:
                logging.info(f"Комментарий успешно добавлен к отчету об ошибке {bug_id}.")
                return True
            else:
                logging.error(f"Ошибка при добавлении комментария: {response.text}")
                return False
        except Exception as e:
            logging.error(f"Ошибка при добавлении комментария: {e}")
            return False
    
    def update_bug_status(self, bug_id, status):
        """
        @brief Обновляет статус отчета об ошибке в Bugzilla.
        
        @param bug_id ID отчета об ошибке.
        @param status Новый статус (CONFIRMED, IN_PROGRESS, RESOLVED, VERIFIED).
        
        @return True, если статус успешно обновлен, иначе False.
        """
        if not self.bugzilla_url or not self.api_key:
            logging.info(f"Демонстрационный режим: статус отчета {bug_id} был бы обновлен на {status}")
            return True
        
        try:
            # Формируем данные для отправки
            data = {
                "status": status
            }
            
            # Если статус RESOLVED, добавляем resolution
            if status == "RESOLVED":
                data["resolution"] = "FIXED"
            
            # Отправляем запрос к Bugzilla API
            headers = {
                "Content-Type": "application/json",
                "X-BUGZILLA-API-KEY": self.api_key
            }
            
            response = requests.put(
                f"{self.bugzilla_url}/rest/bug/{bug_id}",
                headers=headers,
                data=json.dumps(data)
            )
            
            # Проверяем ответ
            if response.status_code == 200:
                logging.info(f"Статус отчета об ошибке {bug_id} успешно обновлен на {status}.")
                return True
            else:
                logging.error(f"Ошибка при обновлении статуса: {response.text}")
                return False
        except Exception as e:
            logging.error(f"Ошибка при обновлении статуса: {e}")
            return False 