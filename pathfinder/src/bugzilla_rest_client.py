"""
REST API клиент для Bugzilla.

Этот модуль предоставляет интерфейс, похожий на REST API, но использует
BugzillaBrowser для взаимодействия с Bugzilla через веб-интерфейс.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union

from bugzilla_browser import BugzillaBrowser

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class BugzillaRestClient:
    """
    Клиент для работы с Bugzilla через REST-подобный интерфейс.
    
    Этот класс предоставляет REST-подобный API, но под капотом использует
    BugzillaBrowser для взаимодействия с Bugzilla через веб-интерфейс.
    """
    
    def __init__(self, url: str = "http://localhost", headless: bool = True):
        """
        Инициализация клиента.
        
        Args:
            url: URL-адрес Bugzilla.
            headless: Запускать браузер в фоновом режиме (без GUI) или с отображением.
        """
        self.url = url
        self.headless = headless
        self.browser = None
        self.authenticated = False
        self._token = None
    
    def login(self, username: str, password: str) -> bool:
        """
        Аутентификация пользователя.
        
        Args:
            username: Имя пользователя (email).
            password: Пароль.
            
        Returns:
            bool: True, если аутентификация успешна, иначе False.
        """
        try:
            self.browser = BugzillaBrowser(url=self.url, headless=self.headless)
            result = self.browser.authenticate(username, password)
            self.authenticated = result
            if result:
                self._token = f"dummy_token_for_{username}"
            return result
        except Exception as e:
            logger.error(f"Ошибка при аутентификации: {str(e)}")
            return False
    
    def logout(self) -> bool:
        """
        Выход из системы.
        
        Returns:
            bool: True, если выход успешно выполнен, иначе False.
        """
        try:
            if self.browser:
                self.browser.close()
                self.browser = None
                self.authenticated = False
                self._token = None
            return True
        except Exception as e:
            logger.error(f"Ошибка при выходе из системы: {str(e)}")
            return False
    
    def get_bugs(self, 
                 product: Optional[str] = "PathFinder", 
                 component: Optional[str] = None, 
                 status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Получение списка ошибок.
        
        Args:
            product: Название продукта.
            component: Название компонента.
            status: Статус ошибок.
            
        Returns:
            List[Dict[str, Any]]: Список словарей с информацией о найденных ошибках.
        """
        if not self.authenticated or not self.browser:
            logger.error("Необходимо аутентифицироваться перед получением ошибок")
            return []
        
        try:
            return self.browser.get_bugs(product=product, component=component, status=status)
        except Exception as e:
            logger.error(f"Ошибка при получении списка ошибок: {str(e)}")
            return []
    
    def get_bug(self, bug_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение информации об ошибке.
        
        Args:
            bug_id: ID ошибки.
            
        Returns:
            Optional[Dict[str, Any]]: Словарь с информацией об ошибке или None.
        """
        if not self.authenticated or not self.browser:
            logger.error("Необходимо аутентифицироваться перед получением информации об ошибке")
            return None
        
        try:
            return self.browser.get_bug_details(bug_id)
        except Exception as e:
            logger.error(f"Ошибка при получении информации об ошибке: {str(e)}")
            return None
    
    def create_bug(self, 
                  summary: str, 
                  description: str,
                  product: str = "PathFinder",
                  component: str = "Core",
                  version: str = "1.0",
                  priority: str = "Normal",
                  severity: str = "normal") -> Optional[Dict[str, Any]]:
        """
        Создание новой ошибки.
        
        Args:
            summary: Заголовок ошибки.
            description: Описание ошибки.
            product: Название продукта.
            component: Компонент.
            version: Версия.
            priority: Приоритет.
            severity: Серьезность.
            
        Returns:
            Optional[Dict[str, Any]]: Информация о созданной ошибке или None.
        """
        if not self.authenticated or not self.browser:
            logger.error("Необходимо аутентифицироваться перед созданием ошибки")
            return None
        
        try:
            result = self.browser.create_bug(
                summary=summary,
                description=description,
                component=component,
                version=version,
                priority=priority,
                severity=severity
            )
            
            # Преобразуем в формат, аналогичный REST API
            if result and result.get('success', False):
                response = {
                    'status': 'success',
                    'bug': {
                        'id': result.get('id', 'unknown')
                    }
                }
                
                if 'warning' in result:
                    response['warning'] = result['warning']
                
                return response
            return None
        except Exception as e:
            logger.error(f"Ошибка при создании ошибки: {str(e)}")
            return None
    
    def add_comment(self, bug_id: str, comment: str) -> bool:
        """
        Добавление комментария к ошибке.
        
        Args:
            bug_id: ID ошибки.
            comment: Текст комментария.
            
        Returns:
            bool: True, если комментарий добавлен успешно, иначе False.
        """
        if not self.authenticated or not self.browser:
            logger.error("Необходимо аутентифицироваться перед добавлением комментария")
            return False
        
        try:
            return self.browser.add_comment(bug_id, comment)
        except Exception as e:
            logger.error(f"Ошибка при добавлении комментария: {str(e)}")
            return False
    
    def update_bug(self, bug_id: str, **fields) -> bool:
        """
        Обновление ошибки.
        
        Пока не реализовано, но в будущем можно добавить.
        
        Args:
            bug_id: ID ошибки.
            **fields: Поля для обновления.
            
        Returns:
            bool: True, если обновление успешно, иначе False.
        """
        logger.warning("Метод update_bug пока не реализован")
        return False
    
    def __enter__(self):
        """
        Метод для использования с контекстным менеджером.
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Метод для использования с контекстным менеджером.
        """
        self.logout() 