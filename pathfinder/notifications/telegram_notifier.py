"""
@file telegram_notifier.py
@brief Модуль для отправки уведомлений через Telegram.

@details
Этот модуль предоставляет функциональность для отправки уведомлений
о событиях проекта через Telegram бота.
"""

import os
import logging
import requests
import json
import sys
from datetime import datetime

# Добавляем путь к корневому каталогу проекта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Пробуем импортировать модули через разные пути
try:
    from pathfinder.config.config import Config, Environment
except ImportError:
    try:
        from config.config import Config, Environment
    except ImportError:
        # Определяем минимальный интерфейс для работы без модуля config
        class Environment:
            DEVELOPMENT = "development"
            TESTING = "testing"
            PRODUCTION = "production"

class TelegramNotifier:
    """
    @brief Класс для отправки уведомлений через Telegram.
    
    @details
    Класс TelegramNotifier предоставляет методы для отправки уведомлений
    о различных событиях проекта через Telegram бота.
    """
    
    def __init__(self, bot_token=None, chat_id=None):
        """
        @brief Инициализация объекта TelegramNotifier.
        
        @param bot_token Токен Telegram бота. Если не указан, берется из переменной окружения TELEGRAM_BOT_TOKEN.
        @param chat_id ID чата для отправки уведомлений. Если не указан, берется из переменной окружения TELEGRAM_CHAT_ID.
        
        @code
        # Пример использования:
        from pathfinder.notifications.telegram_notifier import TelegramNotifier
        
        # Создаем объект для отправки уведомлений
        notifier = TelegramNotifier()
        
        # Отправляем уведомление об ошибке
        notifier.send_error_notification("Произошла ошибка в модуле X", "Подробное описание ошибки")
        @endcode
        """
        self.bot_token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")
        
        if not self.bot_token or not self.chat_id:
            logging.warning("Не указаны токен бота или ID чата. Уведомления не будут отправляться.")
        
        # Загружаем конфигурацию
        self.config = Config()
    
    def send_message(self, message):
        """
        @brief Отправляет сообщение в Telegram.
        
        @param message Текст сообщения.
        
        @return True, если сообщение успешно отправлено, иначе False.
        """
        if not self.bot_token or not self.chat_id:
            logging.info(f"Демонстрационный режим: уведомление было бы отправлено в Telegram: {message}")
            return True
        
        # Проверяем, включены ли уведомления в конфигурации
        if not self.config.get("error_reporting.send_notifications", False):
            logging.info("Отправка уведомлений отключена в конфигурации.")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                logging.info("Сообщение успешно отправлено в Telegram.")
                return True
            else:
                logging.error(f"Ошибка при отправке сообщения в Telegram: {response.text}")
                return False
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения в Telegram: {e}")
            return False
    
    def send_error_notification(self, title, description, error_context=None):
        """
        @brief Отправляет уведомление об ошибке.
        
        @param title Заголовок уведомления.
        @param description Описание ошибки.
        @param error_context Контекст ошибки (объект ErrorContext).
        
        @return True, если уведомление успешно отправлено, иначе False.
        """
        message = f"🔴 *ОШИБКА: {title}*\n\n"
        message += f"📝 *Описание:* {description}\n"
        message += f"🕒 *Время:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if error_context:
            message += f"📋 *Контекст:*\n"
            message += f"  - Модуль: {error_context.module}\n"
            message += f"  - Функция: {error_context.function}\n"
            message += f"  - Строка: {error_context.line}\n"
            
            if error_context.variables:
                message += f"  - Переменные:\n"
                for key, value in error_context.variables.items():
                    message += f"    - {key}: {value}\n"
        
        message += f"\n🌍 *Окружение:* {self.config.get_environment().value}"
        
        return self.send_message(message)
    
    def send_warning_notification(self, title, description):
        """
        @brief Отправляет уведомление о предупреждении.
        
        @param title Заголовок уведомления.
        @param description Описание предупреждения.
        
        @return True, если уведомление успешно отправлено, иначе False.
        """
        message = f"🟡 *ПРЕДУПРЕЖДЕНИЕ: {title}*\n\n"
        message += f"📝 *Описание:* {description}\n"
        message += f"🕒 *Время:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        message += f"\n🌍 *Окружение:* {self.config.get_environment().value}"
        
        return self.send_message(message)
    
    def send_info_notification(self, title, description):
        """
        @brief Отправляет информационное уведомление.
        
        @param title Заголовок уведомления.
        @param description Описание информации.
        
        @return True, если уведомление успешно отправлено, иначе False.
        """
        message = f"🔵 *ИНФОРМАЦИЯ: {title}*\n\n"
        message += f"📝 *Описание:* {description}\n"
        message += f"🕒 *Время:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        message += f"\n🌍 *Окружение:* {self.config.get_environment().value}"
        
        return self.send_message(message)
    
    def send_deployment_notification(self, environment, status, version=None):
        """
        @brief Отправляет уведомление о деплое.
        
        @param environment Окружение, на которое выполняется деплой.
        @param status Статус деплоя (success, failure).
        @param version Версия приложения.
        
        @return True, если уведомление успешно отправлено, иначе False.
        """
        if status == "success":
            message = f"🟢 *ДЕПЛОЙ УСПЕШЕН*\n\n"
        else:
            message = f"🔴 *ДЕПЛОЙ НЕУДАЧЕН*\n\n"
            
        message += f"🌍 *Окружение:* {environment}\n"
        
        if version:
            message += f"📦 *Версия:* {version}\n"
            
        message += f"🕒 *Время:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_message(message) 