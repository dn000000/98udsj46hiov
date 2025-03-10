# BugZilla для проекта PathFinder

## Описание

Данная конфигурация предназначена для запуска BugZilla в Docker-контейнере. BugZilla - это система управления ошибками, которая позволяет отслеживать ошибки, задачи и улучшения в проекте.

## Требования

- Docker
- Docker Compose

## Запуск

### Windows

Для запуска BugZilla в Windows выполните скрипт `start-bugzilla.bat`:

```
start-bugzilla.bat
```

### Linux

Для запуска BugZilla в Linux выполните скрипт `start-bugzilla.sh`:

```bash
chmod +x *.sh  # Добавление прав на выполнение скриптов
./start-bugzilla.sh
```

После запуска BugZilla будет доступна по адресу: http://localhost

> **Важно**: Для полной инициализации системы может потребоваться до 3 минут после запуска контейнеров. Если сайт не открывается, подождите или выполните скрипт диагностики.

## Остановка

### Windows

Для остановки BugZilla выполните скрипт `stop-bugzilla.bat`:

```
stop-bugzilla.bat
```

### Linux

Для остановки BugZilla выполните скрипт `stop-bugzilla.sh`:

```bash
./stop-bugzilla.sh
```

## Полный сброс

Если вам необходимо полностью сбросить данные BugZilla и начать с чистой установки:

### Windows
```
docker-compose down -v
start-bugzilla.bat
```

### Linux
```bash
docker-compose down -v
./start-bugzilla.sh
```

## Отладка

Если возникли проблемы с запуском BugZilla, используйте скрипт диагностики:

### Windows
```
debug-bugzilla.bat
```

### Linux
```bash
./debug-bugzilla.sh
```

Этот скрипт выведет информацию о контейнерах, их логи и проверит доступность сервиса.

## Учетные данные

В системе предустановлены следующие учетные записи:

| Роль | Email | Пароль |
|------|-------|--------|
| Администратор | admin@example.com | admin123 |
| Разработчик | developer@example.com | developer123 |
| Тестировщик | tester@example.com | tester123 |
| Пользователь | user@example.com | user123 |

## Структура проекта

В BugZilla создан проект PathFinder со следующими компонентами:

- **Core** - основной функционал приложения
- **UI** - пользовательский интерфейс
- **Documentation** - документация

## Демонстрационные ошибки

В системе созданы демонстрационные ошибки для тестирования:

1. "BFS algorithm fails to find path in some cases" (Core, High)
2. "Path visualization incorrect" (UI, Medium)
3. "Add support for A* algorithm" (Core, Low)
4. "Application crashes with empty maze" (Core, Highest)

## Структура файлов

- `docker-compose.yml` - конфигурация Docker Compose
- `Dockerfile` - файл сборки образа BugZilla
- `bugzilla.conf` - конфигурация Apache для BugZilla
- `entrypoint.sh` - скрипт инициализации контейнера
- `*.bat` - скрипты для Windows
- `*.sh` - скрипты для Linux

## Возможные проблемы и их решения

### Ошибка "No such file or directory"

Если в логах контейнера вы видите ошибку о том, что файл не найден, возможно неправильно настроены пути. Используйте скрипт диагностики для определения правильной структуры файлов.

### Apache не запускается

Если Apache не запускается внутри контейнера, попробуйте перезапустить его вручную:

```
docker exec bugzilla apachectl restart
```

### База данных недоступна

Проверьте, запущен ли контейнер MySQL и правильно ли настроены параметры подключения:

```
docker logs bugzilla-mysql
```

### Полное пересоздание контейнеров

Если предыдущие решения не помогли, удалите все контейнеры и данные и начните с чистого листа:

```
docker-compose down -v
docker-compose up -d
```

## Особенности конфигурации

Конфигурация реализована с использованием Docker Compose и включает:

1. **Контейнер с MySQL** - для хранения данных BugZilla
2. **Контейнер с BugZilla** - с предустановленными настройками
3. **Скрипт инициализации** - автоматически создает пользователей, компоненты и демо-ошибки

Все данные сохраняются в Docker volumes, поэтому они не будут потеряны при перезапуске контейнеров, если не используется флаг `-v` при остановке.

## Генерация отчетов

BugZilla предоставляет возможность генерации различных отчетов:

1. Перейдите в раздел "Reports" в верхнем меню
2. Выберите тип отчета:
   - Табличные отчеты (Tabular Reports)
   - Графические отчеты (Graphical Reports)
   - Отчеты по поиску (Search)

### Примеры отчетов

- **Отчет по статусам ошибок**: Reports > Graphical Reports > Status
- **Отчет по приоритетам**: Reports > Graphical Reports > Priority
- **Отчет по компонентам**: Reports > Graphical Reports > Component
- **Отчет по активности**: Reports > Graphical Reports > Bug Trends

## Использование REST API

REST API BugZilla доступен по адресу: http://localhost/rest/

### Аутентификация 

Для взаимодействия с API используйте базовую HTTP-аутентификацию (BasicAuth) с учетными данными:

```
Логин: developer@example.com
Пароль: developer123
```

### Пример запроса с использованием BasicAuth

```bash
curl -u "developer@example.com:developer123" http://localhost/rest/bug?product=PathFinder
```

### Доступные эндпоинты

- `/rest/version` - получение версии Bugzilla
- `/rest/bug` - работа со списком ошибок
- `/rest/bug/<id>` - получение информации о конкретной ошибке
- `/rest/product` - работа с продуктами
- `/rest/user` - информация о пользователях

### Полная документация по API

Подробная документация по REST API Bugzilla 5.0.4 доступна по ссылке:
https://bugzilla.readthedocs.io/en/5.0/api/ 