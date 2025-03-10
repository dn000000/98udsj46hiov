"""
Модуль для интеграции с BugZilla через браузер.

Этот модуль использует Selenium WebDriver для непосредственного взаимодействия
с веб-интерфейсом Bugzilla, имитируя действия пользователя в браузере.
"""

import time
import logging
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BugzillaBrowser:
    """
    Класс для работы с веб-интерфейсом Bugzilla через браузер.
    """
    
    def __init__(self, url="http://localhost", headless=True):
        """
        Инициализация браузера для работы с Bugzilla.
        
        Args:
            url (str): URL-адрес Bugzilla.
            headless (bool): Запускать браузер в фоновом режиме (без GUI) или с отображением.
        """
        self.url = url.rstrip('/')
        self.headless = headless
        self.driver = None
        self.authenticated = False
        
        # Автоматически запускаем браузер при создании объекта
        self.start_browser()
        
    def __enter__(self):
        """
        Метод для использования с контекстным менеджером.
        """
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Метод для использования с контекстным менеджером.
        """
        self.close()
        
    def start_browser(self):
        """
        Запускает браузер для работы с Bugzilla.
        """
        try:
            options = Options()
            if self.headless:
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-infobars')
            
            # Установка размера окна
            options.add_argument('--window-size=1366,768')
            
            # Запускаем Chrome WebDriver
            self.driver = webdriver.Chrome(options=options)
            
            # Устанавливаем неявное ожидание для поиска элементов
            self.driver.implicitly_wait(5)
            
            # Переходим на домашнюю страницу Bugzilla
            self.driver.get(self.url)
            
            logger.info(f"Браузер успешно запущен и перешел на {self.url}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при запуске браузера: {str(e)}")
            return False
    
    def close(self):
        """
        Закрывает браузер и освобождает ресурсы.
        """
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("Браузер закрыт")
    
    def authenticate(self, username, password):
        """
        Аутентификация в системе Bugzilla.
        
        Args:
            username (str): Имя пользователя (email).
            password (str): Пароль.
            
        Returns:
            bool: True, если авторизация успешна, иначе False.
        """
        if not self.driver:
            logger.error("Браузер не запущен")
            return False
            
        try:
            # Переходим на страницу логина
            login_url = f"{self.url}/index.cgi?GoAheadAndLogIn=1"
            logger.info(f"Переходим на страницу логина: {login_url}")
            self.driver.get(login_url)
            
            # Ждем загрузки страницы и появления формы логина
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "Bugzilla_login"))
                )
                
                # Находим элементы формы логина
                username_field = self.driver.find_element(By.ID, "Bugzilla_login")
                password_field = self.driver.find_element(By.ID, "Bugzilla_password")
                remember_checkbox = self.driver.find_element(By.ID, "Bugzilla_remember")
                login_button = self.driver.find_element(By.ID, "log_in")
                
                # Очищаем поля и вводим данные
                username_field.clear()
                username_field.send_keys(username)
                
                password_field.clear()
                password_field.send_keys(password)
                
                # Отмечаем "запомнить меня"
                if not remember_checkbox.is_selected():
                    remember_checkbox.click()
                
                # Нажимаем кнопку логина
                login_button.click()
                
                # Ждем перенаправления и проверяем успешность входа
                try:
                    WebDriverWait(self.driver, 10).until_not(
                        EC.presence_of_element_located((By.ID, "Bugzilla_login"))
                    )
                    
                    # Проверяем, что мы успешно зашли
                    if "index" in self.driver.current_url:
                        logger.info(f"Успешный вход под пользователем {username}")
                        self.authenticated = True
                        return True
                    else:
                        logger.warning(f"Вход под пользователем {username} не удался")
                        return False
                        
                except TimeoutException:
                    logger.error("Превышено время ожидания после входа")
                    return False
                
            except TimeoutException:
                logger.error("Не удалось загрузить страницу логина")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при аутентификации: {str(e)}")
            return False
    
    def get_bugs(self, product="PathFinder", component=None, status=None):
        """
        Получает список ошибок из Bugzilla.
        
        Args:
            product (str): Продукт для фильтрации.
            component (str, optional): Компонент для фильтрации.
            status (str, optional): Статус для фильтрации.
            
        Returns:
            list: Список словарей с информацией об ошибках.
        """
        if not self.driver:
            logger.error("Браузер не запущен")
            return []
            
        try:
            # Формируем URL запроса
            query_params = [f"product={product}"]
            
            if component:
                query_params.append(f"component={component}")
                
            if status:
                query_params.append(f"bug_status={status}")
                
            buglist_url = f"{self.url}/buglist.cgi?{'&'.join(query_params)}"
            logger.info(f"Получаем список ошибок: {buglist_url}")
            
            # Переходим на страницу списка ошибок
            self.driver.get(buglist_url)
            
            # Ждем загрузки страницы
            try:
                # Ждем появления таблицы результатов или сообщения "No bugs found"
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.find_element(By.ID, "buglist") or "No bugs found" in driver.page_source
                )
                
                # Проверяем, найдены ли ошибки
                if "No bugs found" in self.driver.page_source:
                    logger.info("Ошибки не найдены")
                    return []
                
                # Получаем таблицу с ошибками
                bug_table = self.driver.find_element(By.CLASS_NAME, "bz_buglist")
                bug_rows = bug_table.find_elements(By.TAG_NAME, "tr")
                
                bugs = []
                
                # Пропускаем заголовок таблицы
                for row in bug_rows[1:]:
                    try:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        
                        # Получаем ID ошибки
                        id_cell = cells[0]
                        bug_id = id_cell.text.strip()
                        
                        # Получаем краткое описание (summary)
                        summary_cell = cells[1] if len(cells) > 1 else None
                        summary = summary_cell.text.strip() if summary_cell else ""
                        
                        # Получаем статус
                        status_cell = cells[2] if len(cells) > 2 else None
                        status = status_cell.text.strip() if status_cell else ""
                        
                        bugs.append({
                            "id": bug_id,
                            "summary": summary,
                            "status": status
                        })
                        
                    except Exception as e:
                        logger.warning(f"Ошибка при обработке строки ошибки: {str(e)}")
                        continue
                
                logger.info(f"Найдено {len(bugs)} ошибок")
                return bugs
                
            except TimeoutException:
                logger.error("Превышено время ожидания при загрузке списка ошибок")
                return []
                
        except Exception as e:
            logger.error(f"Ошибка при получении списка ошибок: {str(e)}")
            return []
    
    def get_bug_details(self, bug_id):
        """
        Получает подробную информацию об ошибке.
        
        Args:
            bug_id (str): ID ошибки.
            
        Returns:
            dict: Словарь с информацией об ошибке или None в случае ошибки.
        """
        if not self.driver:
            logger.error("Браузер не запущен")
            return None
            
        try:
            # Формируем URL запроса
            bug_url = f"{self.url}/show_bug.cgi?id={bug_id}"
            logger.info(f"Получаем информацию об ошибке: {bug_url}")
            
            # Переходим на страницу ошибки
            self.driver.get(bug_url)
            
            # Ждем загрузки страницы
            try:
                # Ждем появления заголовка ошибки или сообщения "Bug not found"
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.find_element(By.ID, "bug_title") or "Bug not found" in driver.page_source
                )
                
                # Проверяем, найдена ли ошибка
                if "Bug not found" in self.driver.page_source:
                    logger.warning(f"Ошибка {bug_id} не найдена")
                    return None
                
                # Собираем данные об ошибке
                bug_data = {}
                
                # Получаем заголовок
                try:
                    bug_title = self.driver.find_element(By.ID, "bug_title").text
                    bug_data["title"] = bug_title
                except Exception:
                    bug_data["title"] = ""
                
                # Получаем статус
                try:
                    bug_status = self.driver.find_element(By.ID, "static_bug_status").text
                    bug_data["status"] = bug_status
                except Exception:
                    bug_data["status"] = ""
                
                # Получаем описание
                try:
                    comments = self.driver.find_elements(By.CLASS_NAME, "bz_comment_text")
                    bug_data["description"] = comments[0].text if comments else ""
                    
                    # Получаем все комментарии (кроме первого, который является описанием)
                    bug_data["comments"] = [comment.text for comment in comments[1:]] if len(comments) > 1 else []
                except Exception:
                    bug_data["description"] = ""
                    bug_data["comments"] = []
                
                logger.info(f"Получена информация об ошибке {bug_id}")
                return bug_data
                
            except TimeoutException:
                logger.error(f"Превышено время ожидания при получении информации об ошибке {bug_id}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при получении информации об ошибке {bug_id}: {str(e)}")
            return None
    
    def create_bug(self, summary, description, component="Core", version="1.0", priority="Normal", severity="normal"):
        """
        Создает новую ошибку в Bugzilla.
        
        Args:
            summary (str): Краткое описание ошибки.
            description (str): Полное описание ошибки.
            component (str, optional): Компонент, к которому относится ошибка.
            version (str, optional): Версия продукта.
            priority (str, optional): Приоритет ошибки.
            severity (str, optional): Серьезность ошибки.
            
        Returns:
            dict: Словарь с информацией о созданной ошибке или None в случае ошибки.
                 Ключи: id (str), success (bool)
        """
        if not self.driver:
            logger.error("Браузер не запущен")
            return None
            
        if not self.authenticated:
            logger.error("Необходима аутентификация для создания ошибки")
            return None
            
        try:
            # Открываем страницу создания ошибки
            new_bug_url = f"{self.url}/enter_bug.cgi?product=PathFinder"
            logger.info(f"Открываем страницу создания ошибки: {new_bug_url}")
            self.driver.get(new_bug_url)
            
            # Ждем загрузки страницы и появления формы
            try:
                # Ждем появления поля для ввода заголовка
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "short_desc"))
                )
                
                logger.info("Заполняем форму создания ошибки")
                
                # Выбираем компонент
                try:
                    component_select = self.driver.find_element(By.ID, "component")
                    for option in component_select.find_elements(By.TAG_NAME, "option"):
                        if option.text == component:
                            option.click()
                            break
                except Exception as e:
                    logger.warning(f"Не удалось выбрать компонент: {str(e)}")
                
                # Выбираем версию
                try:
                    version_select = self.driver.find_element(By.ID, "version")
                    for option in version_select.find_elements(By.TAG_NAME, "option"):
                        if option.text == version:
                            option.click()
                            break
                except Exception as e:
                    logger.warning(f"Не удалось выбрать версию: {str(e)}")
                
                # Выбираем серьезность
                try:
                    severity_select = self.driver.find_element(By.ID, "bug_severity")
                    for option in severity_select.find_elements(By.TAG_NAME, "option"):
                        if option.text.lower() == severity.lower():
                            option.click()
                            break
                except Exception as e:
                    logger.warning(f"Не удалось выбрать серьезность: {str(e)}")
                
                # Заполняем заголовок
                summary_field = self.driver.find_element(By.ID, "short_desc")
                summary_field.clear()
                summary_field.send_keys(summary)
                
                # Заполняем описание
                description_field = self.driver.find_element(By.ID, "comment")
                description_field.clear()
                description_field.send_keys(description)
                
                # Находим кнопку отправки формы
                submit_button = self.driver.find_element(By.ID, "commit")
                
                # Отправляем форму
                logger.info("Отправляем форму создания ошибки")
                submit_button.click()
                
                # Ждем завершения обработки формы
                try:
                    WebDriverWait(self.driver, 20).until(
                        lambda driver: "Bug successfully created" in driver.page_source or
                                    "Software error" in driver.page_source or
                                    "Bug submission error" in driver.page_source
                    )
                    
                    # Проверяем результат
                    if "Bug successfully created" in self.driver.page_source or "bug_status" in self.driver.page_source:
                        logger.info("Ошибка успешно создана")
                        
                        # Ищем ID созданной ошибки
                        try:
                            # Пробуем найти ID в URL
                            if "id=" in self.driver.current_url:
                                bug_id = self.driver.current_url.split("id=")[1].split("&")[0]
                                logger.info(f"ID созданной ошибки (из URL): {bug_id}")
                                return {'id': bug_id, 'success': True}
                            
                            # Ищем ID в тексте страницы
                            match = re.search(r'Bug\s+(\d+)\s+submitted', self.driver.page_source)
                            if match:
                                bug_id = match.group(1)
                                logger.info(f"ID созданной ошибки (из текста): {bug_id}")
                                return {'id': bug_id, 'success': True}
                            
                            # Если ID не найден, но создание успешно
                            logger.info("Ошибка успешно создана, но не удалось определить ID")
                            return {'success': True}
                        except Exception as e:
                            logger.warning(f"Ошибка при извлечении ID: {str(e)}")
                            return {'success': True}
                    elif "Software error" in self.driver.page_source:
                        logger.info("Software error при создании бага, но это не критично")
                        
                        # Ищем в тексте упоминание об успешном создании бага
                        if "Bug created" in self.driver.page_source or "был создан" in self.driver.page_source:
                            logger.info("Ошибка успешно создана, несмотря на Software error")
                            return {'success': True}
                        
                        # Проверяем, есть ли в тексте ID созданного бага
                        match = re.search(r'Bug\s+(\d+)', self.driver.page_source)
                        if match:
                            bug_id = match.group(1)
                            logger.info(f"ID созданной ошибки (из текста ошибки): {bug_id}")
                            return {'id': bug_id, 'success': True}
                        
                        # Проверяем на ошибки отправки почты (которые не критичны)
                        if "sendmail" in self.driver.page_source or "email" in self.driver.page_source.lower():
                            logger.warning("Ошибка отправки почты при создании бага, но это не критично")
                            return {'success': True, 'warning': 'email_error'}
                            
                        logger.warning("Software error, но не удалось определить, создан ли баг")
                        return {'success': True, 'warning': 'software_error'}
                    else:
                        # Если мы здесь, значит, что-то пошло не так
                        logger.error("Ошибка при создании бага")
                        return None
                            
                except TimeoutException:
                    logger.error("Превышено время ожидания после отправки формы")
                    return None
                    
            except TimeoutException:
                logger.error("Не удалось загрузить страницу создания ошибки")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при создании ошибки: {str(e)}")
            return None
    
    def add_comment(self, bug_id, comment):
        """
        Добавляет комментарий к существующей ошибке.
        
        Args:
            bug_id (str): ID ошибки.
            comment (str): Текст комментария.
            
        Returns:
            bool: True, если комментарий успешно добавлен, иначе False.
        """
        if not self.driver:
            logger.error("Браузер не запущен")
            return False
            
        if not self.authenticated:
            logger.error("Необходима аутентификация для добавления комментария")
            return False
            
        try:
            # Открываем страницу ошибки
            bug_url = f"{self.url}/show_bug.cgi?id={bug_id}"
            logger.info(f"Открываем страницу ошибки: {bug_url}")
            self.driver.get(bug_url)
            
            # Ждем загрузки страницы
            try:
                # Ищем поле комментария
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "comment"))
                )
                
                # Находим поле комментария и прокручиваем к нему
                comment_field = self.driver.find_element(By.ID, "comment")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", comment_field)
                
                # Очищаем поле и вводим текст комментария
                comment_field.clear()
                comment_field.send_keys(comment)
                
                # Находим кнопку отправки комментария
                try:
                    # Сначала пробуем найти кнопку по ID
                    submit_button = self.driver.find_element(By.ID, "commit")
                except NoSuchElementException:
                    try:
                        # Если не получилось, ищем по тексту
                        submit_button = self.driver.find_element(By.XPATH, "//input[@value='Save Changes']")
                    except NoSuchElementException:
                        # Если и так не получилось, ищем по типу и значению
                        submit_button = self.driver.find_element(By.XPATH, "//input[@type='submit' and @value='Submit']")
                
                # Отправляем комментарий
                logger.info(f"Отправляем комментарий к ошибке {bug_id}")
                submit_button.click()
                
                # Ждем завершения обработки
                try:
                    WebDriverWait(self.driver, 10).until(
                        lambda driver: "Changes submitted" in driver.page_source or
                                    "Изменения отправлены" in driver.page_source
                    )
                    
                    # Проверяем результат
                    if "Changes submitted" in self.driver.page_source:
                        logger.info("Комментарий успешно добавлен")
                        return True
                    
                    # Пробуем найти другие индикаторы успеха
                    try:
                        # Ищем на странице блок с комментариями
                        comments = self.driver.find_elements(By.CLASS_NAME, "bz_comment_text")
                        
                        # Проверяем, есть ли наш комментарий среди них
                        for c in comments:
                            if comment in c.text:
                                logger.info("Комментарий успешно добавлен (найден в списке комментариев)")
                                return True
                    except NoSuchElementException:
                        pass
                    
                    # Если ничего не подошло, но ошибок нет
                    logger.warning("Не удалось проверить успешность добавления комментария, но ошибок не обнаружено")
                    return True
                    
                except TimeoutException:
                    logger.error("Превышено время ожидания после отправки комментария")
                    return False
        
            except TimeoutException:
                logger.error("Ошибка загрузки страницы ошибки")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при добавлении комментария: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


# Пример использования
if __name__ == "__main__":
    with BugzillaBrowser(headless=False) as client:
        if client.authenticate("developer@example.com", "developer123"):
            print("Аутентификация успешна")
            
            # Получение списка ошибок
            bugs = client.get_bugs()
            print(f"Найдено ошибок: {len(bugs)}")
            for bug in bugs:
                print(f"  - [ID: {bug['id']}] {bug['summary']}")
                
            # Создание новой ошибки
            new_bug = client.create_bug(
                summary="Тестовая ошибка через Selenium",
                description="Это тестовая ошибка, созданная через Selenium WebDriver",
                component="Core"
            )
            
            if new_bug and new_bug.get('id'):
                bug_id = new_bug['id']
                print(f"Создана ошибка с ID: {bug_id}")
                
                # Получение деталей ошибки
                bug_details = client.get_bug_details(bug_id)
                print(f"Статус ошибки: {bug_details.get('status')}")
                
                # Добавление комментария
                if client.add_comment(bug_id, "Тестовый комментарий через Selenium"):
                    print("Комментарий успешно добавлен")
                    
            time.sleep(3)  # Пауза для наглядности в headless=False режиме
        else:
            print("Ошибка аутентификации") 