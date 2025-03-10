"""
Модуль для интеграции с BugZilla.

Этот модуль предоставляет функции для взаимодействия с BugZilla через веб-интерфейс.
"""

import requests
import json
import logging
import re
from bs4 import BeautifulSoup

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BugzillaWebClient:
    """
    Клиент для работы с веб-интерфейсом BugZilla.
    """
    
    def __init__(self, url="http://localhost", login=None, password=None):
        """
        Инициализация клиента BugZilla.
        
        Args:
            url (str): URL веб-интерфейса BugZilla.
            login (str): Логин пользователя.
            password (str): Пароль пользователя.
        """
        self.url = url
        self.login = login
        self.password = password
        self.session = requests.Session()
        self.authenticated = False
    
    def authenticate(self, login=None, password=None):
        """
        Аутентификация пользователя.
        
        Args:
            login (str): Логин пользователя. Если None, используется login из инициализации.
            password (str): Пароль пользователя. Если None, используется password из инициализации.
            
        Returns:
            bool: True, если аутентификация успешна, иначе False.
        """
        if login:
            self.login = login
        if password:
            self.password = password
            
        if not self.login or not self.password:
            logger.error("Не указаны логин или пароль")
            return False
            
        try:
            # Сначала получаем страницу с параметром GoAheadAndLogIn=1
            logger.info(f"Получение начальной страницы с {self.url}/index.cgi?GoAheadAndLogIn=1")
            login_page = self.session.get(f"{self.url}/index.cgi?GoAheadAndLogIn=1")
            logger.info(f"Получен ответ с кодом {login_page.status_code}")
            
            # Сохраняем HTML ответ для отладки
            with open("login_page.html", "w", encoding="utf-8") as f:
                f.write(login_page.text)
            logger.info("Сохранен файл login_page.html для отладки")
            
            soup = BeautifulSoup(login_page.text, 'html.parser')
            token_input = soup.find('input', {'name': 'Bugzilla_login_token'})
            
            if not token_input:
                logger.error("Не удалось найти токен для входа")
                
                # Поиск форм входа
                login_forms = soup.find_all('form')
                logger.info(f"Найдено {len(login_forms)} форм на странице")
                for idx, form in enumerate(login_forms):
                    logger.info(f"Форма #{idx}: {form.get('action', 'Нет action')} ID: {form.get('id', 'Нет id')}")
                    inputs = form.find_all('input')
                    for input_tag in inputs:
                        logger.info(f"  - Input: {input_tag.get('name', 'Нет имени')} - {input_tag.get('type', 'Нет типа')}")
                
                return False
            
            login_token = token_input.get('value', '')
            logger.info(f"Получен токен для входа: {login_token}")
            
            # Выполняем вход
            login_data = {
                'Bugzilla_login': self.login,
                'Bugzilla_password': self.password,
                'Bugzilla_login_token': login_token,
                'GoAheadAndLogIn': '1'
            }
            
            logger.info(f"Отправка данных аутентификации на {self.url}/index.cgi")
            login_response = self.session.post(f"{self.url}/index.cgi", data=login_data)
            logger.info(f"Получен ответ с кодом {login_response.status_code}")
            
            # Сохраняем HTML ответ для отладки
            with open("login_response.html", "w", encoding="utf-8") as f:
                f.write(login_response.text)
            logger.info("Сохранен файл login_response.html для отладки")
            
            # Проверяем успешность входа
            if 'index.cgi?logout=1' in login_response.text:
                logger.info(f"Успешная аутентификация пользователя {self.login}")
                self.authenticated = True
                return True
            else:
                # Еще одна попытка, проверяя имя пользователя в ответе
                username_match = re.search(r'userprefs.cgi\?tab=account">([^<]+)</a>', login_response.text)
                if username_match:
                    logger.info(f"Успешная аутентификация пользователя {username_match.group(1)}")
                    self.authenticated = True
                    return True
                    
                logger.error(f"Ошибка аутентификации")
                # Проверяем наличие сообщения об ошибке
                soup = BeautifulSoup(login_response.text, 'html.parser')
                error_msgs = soup.find_all('div', {'class': 'error_msg'})
                for msg in error_msgs:
                    logger.error(f"Сообщение об ошибке: {msg.text.strip()}")
                return False
        except Exception as e:
            logger.error(f"Ошибка при аутентификации: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def get_bugs(self, product="PathFinder", component=None, status=None, priority=None):
        """
        Получение списка ошибок.
        
        Args:
            product (str): Название продукта.
            component (str): Название компонента.
            status (str): Статус ошибки.
            priority (str): Приоритет ошибки.
            
        Returns:
            list: Список ошибок.
        """
        if not self.authenticated:
            logger.error("Необходимо аутентифицироваться перед запросом")
            return []
        
        try:
            # Формируем URL для запроса
            url = f"{self.url}/buglist.cgi?product={product}&resolution=---"
            
            if component:
                url += f"&component={component}"
            
            if status:
                url += f"&bug_status={status}"
            
            if priority:
                url += f"&priority={priority}"
            
            # Выполняем запрос
            response = self.session.get(url)
            
            # Парсим HTML для получения списка ошибок
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Проверяем, есть ли сообщение о том, что ошибок не найдено
            if "No bugs found" in response.text or "Ошибок не найдено" in response.text:
                logger.info("Ошибок не найдено")
                return []
            
            bugs = []
            
            # Ищем таблицу ошибок
            bug_table = soup.find('table', {'class': 'bz_buglist'})
            
            if bug_table:
                bug_rows = bug_table.find_all('tr', {'class': 'bz_bugitem'})
                logger.info(f"Найдено {len(bug_rows)} ошибок")
                
                for row in bug_rows:
                    bug_info = {}
                    
                    # Извлекаем ID
                    id_cell = row.find('td', {'class': 'bz_id_column'})
                    if id_cell:
                        bug_info['id'] = id_cell.text.strip()
                    
                    # Извлекаем заголовок
                    summary_cell = row.find('td', {'class': 'bz_summary_column'})
                    if summary_cell:
                        bug_info['summary'] = summary_cell.text.strip()
                    
                    # Извлекаем статус
                    status_cell = row.find('td', {'class': 'bz_status_column'})
                    if status_cell:
                        bug_info['status'] = status_cell.text.strip()
                    
                    # Извлекаем приоритет
                    priority_cell = row.find('td', {'class': 'bz_priority_column'})
                    if priority_cell:
                        bug_info['priority'] = priority_cell.text.strip()
                    
                    bugs.append(bug_info)
            else:
                # Пробуем найти ошибки в другом формате
                bug_links = soup.find_all('a', href=re.compile(r'show_bug\.cgi\?id=\d+'))
                if bug_links:
                    logger.info(f"Найдено {len(bug_links)} ссылок на ошибки")
                    for link in bug_links:
                        bug_id_match = re.search(r'id=(\d+)', link['href'])
                        if bug_id_match:
                            bug_id = bug_id_match.group(1)
                            bug_info = {
                                'id': bug_id,
                                'summary': link.text.strip(),
                                'status': 'Unknown',
                                'priority': 'Unknown'
                            }
                            bugs.append(bug_info)
            
            return bugs
        except Exception as e:
            logger.error(f"Ошибка при получении списка ошибок: {str(e)}")
            return []
    
    def get_bug_details(self, bug_id):
        """
        Получение подробной информации о конкретной ошибке.
        
        Args:
            bug_id (str): ID ошибки.
            
        Returns:
            dict: Информация об ошибке.
        """
        if not self.authenticated:
            logger.error("Необходимо аутентифицироваться перед запросом")
            return {}
        
        try:
            # Выполняем запрос
            response = self.session.get(f"{self.url}/show_bug.cgi?id={bug_id}")
            
            # Парсим HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Проверяем, найдена ли ошибка
            if "Bug not found" in response.text or "Ошибка не найдена" in response.text:
                logger.error(f"Ошибка с ID {bug_id} не найдена")
                return {}
            
            bug_info = {'id': bug_id}
            
            # Извлекаем информацию о заголовке
            title = soup.find('title')
            if title:
                bug_info['summary'] = title.text.strip().replace(f"Bug {bug_id}", "").strip()
            
            # Извлекаем информацию о статусе
            status_field = soup.find('span', {'id': 'static_bug_status'})
            if status_field:
                bug_info['status'] = status_field.text.strip()
            
            # Извлекаем информацию о приоритете
            priority_field = soup.find('select', {'id': 'priority'})
            if priority_field:
                selected_option = priority_field.find('option', {'selected': True})
                if selected_option:
                    bug_info['priority'] = selected_option.text.strip()
            
            # Извлекаем информацию о компоненте
            component_field = soup.find('select', {'id': 'component'})
            if component_field:
                selected_option = component_field.find('option', {'selected': True})
                if selected_option:
                    bug_info['component'] = selected_option.text.strip()
            
            # Извлекаем комментарии
            comments = []
            comment_divs = soup.find_all('div', {'class': 'bz_comment'})
            for comment_div in comment_divs:
                comment_text_div = comment_div.find('pre', {'class': 'bz_comment_text'})
                if comment_text_div:
                    comments.append(comment_text_div.text.strip())
            
            bug_info['comments'] = comments
            
            return bug_info
        except Exception as e:
            logger.error(f"Ошибка при получении деталей ошибки: {str(e)}")
            return {}
    
    def create_bug(self, summary, description, component="Core", version="1.0", priority="Normal", severity="normal"):
        """
        Создание новой ошибки.
        
        Args:
            summary (str): Заголовок ошибки.
            description (str): Описание ошибки.
            component (str): Компонент.
            version (str): Версия.
            priority (str): Приоритет.
            severity (str): Серьезность.
            
        Returns:
            dict: Информация о созданной ошибке или None, если произошла ошибка.
        """
        if not self.authenticated:
            logger.error("Необходимо аутентифицироваться перед созданием ошибки")
            return None
        
        try:
            # Получаем форму создания ошибки
            new_bug_form = self.session.get(f"{self.url}/enter_bug.cgi?product=PathFinder")
            
            # Парсим HTML
            soup = BeautifulSoup(new_bug_form.text, 'html.parser')
            
            # Получаем токен
            token_input = soup.find('input', {'name': 'token'})
            if not token_input:
                logger.error("Не удалось найти токен для создания ошибки")
                return None
            
            token = token_input.get('value', '')
            
            # Проверяем доступные компоненты и версии
            component_select = soup.find('select', {'name': 'component'})
            components = []
            if component_select:
                component_options = component_select.find_all('option')
                components = [option.get('value') for option in component_options if option.get('value')]
            
            version_select = soup.find('select', {'name': 'version'})
            versions = []
            if version_select:
                version_options = version_select.find_all('option')
                versions = [option.get('value') for option in version_options if option.get('value')]
            
            # Проверяем, что указанные компонент и версия доступны
            if component not in components and components:
                logger.warning(f"Компонент {component} недоступен. Используем {components[0]}")
                component = components[0]
            
            if version not in versions and versions:
                logger.warning(f"Версия {version} недоступна. Используем {versions[0]}")
                version = versions[0]
            
            # Отключаем отправку почты, чтобы обойти проблему с sendmail
            mailrecipient_input = soup.find('input', {'name': 'makeemailprivate'})
            mail_data = {}
            if mailrecipient_input:
                mail_data['makeemailprivate'] = '1'
            
            # Заполняем форму создания ошибки
            new_bug_data = {
                'product': 'PathFinder',
                'component': component,
                'version': version,
                'rep_platform': 'All',
                'op_sys': 'All',
                'priority': priority,
                'bug_severity': severity,
                'short_desc': summary,
                'comment': description,
                'token': token,
                **mail_data  # Добавляем данные для отключения отправки почты
            }
            
            # Отправляем форму
            create_response = self.session.post(f"{self.url}/post_bug.cgi", data=new_bug_data)
            
            # Проверяем успешность создания ошибки
            if "Bug " in create_response.text and " created" in create_response.text:
                # Извлекаем ID созданной ошибки
                match = re.search(r'Bug\s+(\d+)\s+created', create_response.text)
                if match:
                    bug_id = match.group(1)
                    logger.info(f"Создана ошибка с ID {bug_id}")
                    return {'id': bug_id, 'success': True}
                else:
                    logger.warning("Ошибка создана, но не удалось определить ID")
                    return {'success': True}
            else:
                # Проверяем наличие ошибки с sendmail
                if "couldn't find a sendmail executable" in create_response.text:
                    logger.error("Ошибка при создании: не найден исполняемый файл sendmail")
                    return None
                
                logger.error("Ошибка при создании ошибки")
                return None
        except Exception as e:
            logger.error(f"Ошибка при создании ошибки: {str(e)}")
            return None
    
    def add_comment(self, bug_id, comment):
        """
        Добавление комментария к ошибке.
        
        Args:
            bug_id (str): ID ошибки.
            comment (str): Текст комментария.
            
        Returns:
            bool: True, если комментарий добавлен успешно, иначе False.
        """
        if not self.authenticated:
            logger.error("Необходимо аутентифицироваться перед добавлением комментария")
            return False
        
        try:
            # Получаем страницу ошибки
            bug_page = self.session.get(f"{self.url}/show_bug.cgi?id={bug_id}")
            
            # Парсим HTML
            soup = BeautifulSoup(bug_page.text, 'html.parser')
            
            # Получаем токен
            token_input = soup.find('input', {'name': 'token'})
            if not token_input:
                logger.error("Не удалось найти токен для добавления комментария")
                return False
            
            token = token_input.get('value', '')
            
            # Заполняем форму комментария
            comment_data = {
                'id': bug_id,
                'comment': comment,
                'token': token
            }
            
            # Отправляем форму
            response = self.session.post(f"{self.url}/process_bug.cgi", data=comment_data)
            
            # Проверяем успешность добавления комментария
            if "Changes submitted" in response.text:
                logger.info(f"Добавлен комментарий к ошибке с ID {bug_id}")
                return True
            else:
                logger.error("Ошибка при добавлении комментария")
                return False
        except Exception as e:
            logger.error(f"Ошибка при добавлении комментария: {str(e)}")
            return False


# Пример использования
if __name__ == "__main__":
    client = BugzillaWebClient()
    
    # Аутентификация
    if client.authenticate("developer@example.com", "developer123"):
        print("Аутентификация успешна")
        
        # Получение списка ошибок
        bugs = client.get_bugs()
        print(f"Получено {len(bugs)} ошибок")
        
        # Вывод информации об ошибках
        for bug in bugs:
            print(f"ID: {bug.get('id')}, Заголовок: {bug.get('summary')}, Статус: {bug.get('status')}")
            
        # Создание новой ошибки
        new_bug = client.create_bug(
            summary="Тестовая ошибка",
            description="Это тестовая ошибка, созданная через клиент",
            component="Core"
        )
        
        if new_bug:
            print(f"Создана новая ошибка с ID: {new_bug.get('id')}")
            
            # Добавление комментария
            if client.add_comment(new_bug.get('id'), "Тестовый комментарий"):
                print("Комментарий успешно добавлен")
    else:
        print("Ошибка аутентификации") 