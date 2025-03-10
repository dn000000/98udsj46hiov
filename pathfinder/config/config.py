"""
@file config.py
@brief Модуль для управления конфигурацией проекта.

@details
Этот модуль содержит классы и функции для управления конфигурацией
проекта в разных окружениях (разработка, тестирование, продакшн).
"""

import os
import json
import logging
from enum import Enum

class Environment(Enum):
    """
    @brief Перечисление доступных окружений.
    """
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

class Config:
    """
    @brief Класс для управления конфигурацией проекта.
    
    @details
    Класс Config предоставляет методы для загрузки и доступа к
    конфигурационным параметрам проекта в зависимости от окружения.
    """
    
    # Значения по умолчанию для разных окружений
    DEFAULT_CONFIGS = {
        Environment.DEVELOPMENT: {
            "log_level": "DEBUG",
            "visualization_enabled": True,
            "error_reporting": {
                "enabled": True,
                "report_to_bugzilla": False,
                "send_notifications": False
            },
            "performance": {
                "use_optimized_algorithms": False,
                "cache_results": False
            }
        },
        Environment.TESTING: {
            "log_level": "INFO",
            "visualization_enabled": True,
            "error_reporting": {
                "enabled": True,
                "report_to_bugzilla": True,
                "send_notifications": True
            },
            "performance": {
                "use_optimized_algorithms": True,
                "cache_results": True
            }
        },
        Environment.PRODUCTION: {
            "log_level": "WARNING",
            "visualization_enabled": False,
            "error_reporting": {
                "enabled": True,
                "report_to_bugzilla": True,
                "send_notifications": True
            },
            "performance": {
                "use_optimized_algorithms": True,
                "cache_results": True
            }
        }
    }
    
    def __init__(self, env=None):
        """
        @brief Инициализация объекта Config.
        
        @param env Окружение (development, testing, production). Если не указано,
                  берется из переменной окружения PATHFINDER_ENV или по умолчанию development.
        
        @code
        # Пример использования:
        from config.config import Config, Environment
        
        # Создаем конфигурацию для разработки
        dev_config = Config(Environment.DEVELOPMENT)
        
        # Получаем значение параметра
        log_level = dev_config.get("log_level")
        
        # Проверяем, включена ли визуализация
        if dev_config.get("visualization_enabled"):
            # Отображаем визуализацию
            pass
        @endcode
        """
        # Определяем окружение
        if env is None:
            env_str = os.environ.get("PATHFINDER_ENV", "development")
            try:
                self.env = Environment(env_str)
            except ValueError:
                logging.warning(f"Неизвестное окружение: {env_str}. Используем development.")
                self.env = Environment.DEVELOPMENT
        elif isinstance(env, Environment):
            self.env = env
        else:
            try:
                self.env = Environment(env)
            except ValueError:
                logging.warning(f"Неизвестное окружение: {env}. Используем development.")
                self.env = Environment.DEVELOPMENT
        
        # Загружаем конфигурацию
        self.config = self._load_config()
        
        # Настраиваем логирование
        self._setup_logging()
    
    def _load_config(self):
        """
        @brief Загружает конфигурацию для текущего окружения.
        
        @return Словарь с конфигурационными параметрами.
        """
        # Путь к файлу конфигурации
        config_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(config_dir, f"{self.env.value}.json")
        
        # Если файл существует, загружаем из него
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Ошибка при загрузке конфигурации из {config_file}: {e}")
                # В случае ошибки используем значения по умолчанию
                return self.DEFAULT_CONFIGS[self.env].copy()
        else:
            # Если файла нет, используем значения по умолчанию
            return self.DEFAULT_CONFIGS[self.env].copy()
    
    def _setup_logging(self):
        """
        @brief Настраивает логирование на основе конфигурации.
        """
        log_level_str = self.config.get("log_level", "INFO")
        log_level = getattr(logging, log_level_str, logging.INFO)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def get(self, key, default=None):
        """
        @brief Возвращает значение конфигурационного параметра.
        
        @param key Ключ параметра. Может быть вложенным, разделенным точками.
        @param default Значение по умолчанию, если параметр не найден.
        
        @return Значение параметра или default, если параметр не найден.
        """
        if "." in key:
            # Обрабатываем вложенные ключи
            parts = key.split(".")
            value = self.config
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default
            return value
        else:
            # Простой ключ
            return self.config.get(key, default)
    
    def set(self, key, value):
        """
        @brief Устанавливает значение конфигурационного параметра.
        
        @param key Ключ параметра. Может быть вложенным, разделенным точками.
        @param value Новое значение параметра.
        """
        if "." in key:
            # Обрабатываем вложенные ключи
            parts = key.split(".")
            config = self.config
            for part in parts[:-1]:
                if part not in config:
                    config[part] = {}
                config = config[part]
            config[parts[-1]] = value
        else:
            # Простой ключ
            self.config[key] = value
    
    def save(self):
        """
        @brief Сохраняет текущую конфигурацию в файл.
        
        @return True, если сохранение успешно, иначе False.
        """
        config_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(config_dir, f"{self.env.value}.json")
        
        try:
            # Создаем директорию, если она не существует
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"Ошибка при сохранении конфигурации в {config_file}: {e}")
            return False
    
    def get_environment(self):
        """
        @brief Возвращает текущее окружение.
        
        @return Объект Environment, представляющий текущее окружение.
        """
        return self.env
    
    def is_development(self):
        """
        @brief Проверяет, является ли текущее окружение окружением разработки.
        
        @return True, если текущее окружение - development, иначе False.
        """
        return self.env == Environment.DEVELOPMENT
    
    def is_testing(self):
        """
        @brief Проверяет, является ли текущее окружение окружением тестирования.
        
        @return True, если текущее окружение - testing, иначе False.
        """
        return self.env == Environment.TESTING
    
    def is_production(self):
        """
        @brief Проверяет, является ли текущее окружение продакшн-окружением.
        
        @return True, если текущее окружение - production, иначе False.
        """
        return self.env == Environment.PRODUCTION 