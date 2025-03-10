#!/usr/bin/env python
"""
@file send_notification.py
@brief Скрипт для отправки уведомлений.

@details
Этот скрипт позволяет отправлять уведомления о различных событиях
проекта через Telegram.
"""

import os
import sys
import argparse
import logging
from telegram_notifier import TelegramNotifier

def setup_parser():
    """
    @brief Настраивает парсер аргументов командной строки.
    
    @return Настроенный парсер аргументов.
    """
    parser = argparse.ArgumentParser(description="Отправка уведомлений о событиях проекта PathFinder")
    
    parser.add_argument("--event", "-e", type=str, required=True,
                        choices=["error", "warning", "info", "deployment"],
                        help="Тип события для уведомления")
    
    parser.add_argument("--title", "-t", type=str,
                        help="Заголовок уведомления")
    
    parser.add_argument("--description", "-d", type=str,
                        help="Описание события")
    
    parser.add_argument("--env", type=str,
                        choices=["development", "testing", "production"],
                        help="Окружение (для уведомлений о деплое)")
    
    parser.add_argument("--status", type=str,
                        choices=["success", "failure"],
                        help="Статус события (для уведомлений о деплое)")
    
    parser.add_argument("--version", "-v", type=str,
                        help="Версия приложения (для уведомлений о деплое)")
    
    return parser

def send_notification(args):
    """
    @brief Отправляет уведомление на основе аргументов командной строки.
    
    @param args Аргументы командной строки.
    
    @return True, если уведомление успешно отправлено, иначе False.
    """
    try:
        # Создаем объект для отправки уведомлений
        notifier = TelegramNotifier()
        
        # Отправляем уведомление в зависимости от типа события
        if args.event == "error":
            if not args.title or not args.description:
                logging.error("Для уведомления об ошибке необходимо указать заголовок и описание.")
                return False
                
            return notifier.send_error_notification(args.title, args.description)
            
        elif args.event == "warning":
            if not args.title or not args.description:
                logging.error("Для уведомления о предупреждении необходимо указать заголовок и описание.")
                return False
                
            return notifier.send_warning_notification(args.title, args.description)
            
        elif args.event == "info":
            if not args.title or not args.description:
                logging.error("Для информационного уведомления необходимо указать заголовок и описание.")
                return False
                
            return notifier.send_info_notification(args.title, args.description)
            
        elif args.event == "deployment":
            if not args.env or not args.status:
                logging.error("Для уведомления о деплое необходимо указать окружение и статус.")
                return False
                
            return notifier.send_deployment_notification(args.env, args.status, args.version)
            
        else:
            logging.error(f"Неизвестный тип события: {args.event}")
            return False
    except Exception as e:
        logging.error(f"Ошибка при отправке уведомления: {e}")
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
    
    # Отправляем уведомление
    if send_notification(args):
        logging.info("Уведомление успешно отправлено.")
    else:
        logging.error("Не удалось отправить уведомление.")
        sys.exit(1)

if __name__ == "__main__":
    main() 