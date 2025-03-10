#!/usr/bin/env python
"""
@file configure.py
@brief Скрипт для настройки окружения проекта.

@details
Этот скрипт позволяет настроить окружение проекта (development, testing, production)
и создать соответствующие конфигурационные файлы.
"""

import os
import sys
import json
import argparse
import logging
from config import Config, Environment

def setup_parser():
    """
    @brief Настраивает парсер аргументов командной строки.
    
    @return Настроенный парсер аргументов.
    """
    parser = argparse.ArgumentParser(description="Настройка окружения проекта PathFinder")
    
    parser.add_argument("--env", "-e", type=str, choices=["development", "testing", "production"],
                        default="development", help="Окружение для настройки")
    
    parser.add_argument("--log-level", "-l", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Уровень логирования")
    
    parser.add_argument("--visualization", "-v", type=bool,
                        help="Включить визуализацию (True/False)")
    
    parser.add_argument("--error-reporting", "-r", type=bool,
                        help="Включить отчеты об ошибках (True/False)")
    
    parser.add_argument("--bugzilla-reporting", "-b", type=bool,
                        help="Включить отправку отчетов в Bugzilla (True/False)")
    
    parser.add_argument("--notifications", "-n", type=bool,
                        help="Включить уведомления (True/False)")
    
    parser.add_argument("--optimized", "-o", type=bool,
                        help="Использовать оптимизированные алгоритмы (True/False)")
    
    parser.add_argument("--cache", "-c", type=bool,
                        help="Включить кэширование результатов (True/False)")
    
    return parser

def configure_environment(args):
    """
    @brief Настраивает окружение проекта на основе аргументов командной строки.
    
    @param args Аргументы командной строки.
    
    @return True, если настройка успешна, иначе False.
    """
    try:
        # Создаем конфигурацию для указанного окружения
        env = Environment(args.env)
        config = Config(env)
        
        # Обновляем параметры конфигурации, если они указаны
        if args.log_level:
            config.set("log_level", args.log_level)
            
        if args.visualization is not None:
            config.set("visualization_enabled", args.visualization)
            
        if args.error_reporting is not None:
            config.set("error_reporting.enabled", args.error_reporting)
            
        if args.bugzilla_reporting is not None:
            config.set("error_reporting.report_to_bugzilla", args.bugzilla_reporting)
            
        if args.notifications is not None:
            config.set("error_reporting.send_notifications", args.notifications)
            
        if args.optimized is not None:
            config.set("performance.use_optimized_algorithms", args.optimized)
            
        if args.cache is not None:
            config.set("performance.cache_results", args.cache)
        
        # Сохраняем конфигурацию
        if config.save():
            logging.info(f"Конфигурация для окружения {args.env} успешно сохранена.")
            return True
        else:
            logging.error(f"Не удалось сохранить конфигурацию для окружения {args.env}.")
            return False
    except Exception as e:
        logging.error(f"Ошибка при настройке окружения: {e}")
        return False

def create_default_configs():
    """
    @brief Создает конфигурационные файлы по умолчанию для всех окружений.
    
    @return True, если создание успешно, иначе False.
    """
    try:
        for env in Environment:
            config = Config(env)
            if not config.save():
                logging.error(f"Не удалось создать конфигурацию по умолчанию для окружения {env.value}.")
                return False
        
        logging.info("Конфигурации по умолчанию для всех окружений успешно созданы.")
        return True
    except Exception as e:
        logging.error(f"Ошибка при создании конфигураций по умолчанию: {e}")
        return False

def main():
    """
    @brief Основная функция скрипта.
    """
    # Настраиваем логирование
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Парсим аргументы командной строки
    parser = setup_parser()
    args = parser.parse_args()
    
    # Настраиваем окружение
    if configure_environment(args):
        # Выводим информацию о текущей конфигурации
        config = Config(Environment(args.env))
        logging.info(f"Текущая конфигурация для окружения {args.env}:")
        logging.info(json.dumps(config.config, indent=2, ensure_ascii=False))
    else:
        logging.error("Не удалось настроить окружение.")
        sys.exit(1)

if __name__ == "__main__":
    main() 