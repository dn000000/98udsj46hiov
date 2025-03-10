@echo off
echo ====================================
echo = Запуск BugZilla 5.2 для PathFinder =
echo ====================================
cd %~dp0

echo.
echo [1/6] Проверка наличия архива с исходниками...
if not exist bugzilla-5.2.tar.gz (
    echo Архив не найден. Создаем тестовый архив...
    call .\create-dummy-archive.bat
    if not exist bugzilla-5.2.tar.gz (
        echo ОШИБКА: Не удалось создать архив bugzilla-5.2.tar.gz!
        echo Пожалуйста, добавьте архив вручную и запустите скрипт снова.
        exit /b 1
    )
) else (
    echo Архив bugzilla-5.2.tar.gz найден.
)

echo [2/6] Проверка структуры архива...
echo Запуск быстрой проверки архива...
call .\extract-archive.bat
if %ERRORLEVEL% neq 0 (
    echo ОШИБКА: Проверка архива завершилась с ошибкой!
    exit /b 1
)

echo [3/6] Остановка существующих контейнеров...
docker-compose down >nul 2>&1

echo [4/6] Сборка образа Bugzilla из исходников...
echo Это может занять некоторое время при первом запуске...
echo Включаем подробный вывод для отладки...
docker-compose build --no-cache --progress=plain

echo [5/6] Запуск контейнеров...
docker-compose up -d

echo [6/6] Ожидание запуска сервисов...
echo.
echo BugZilla запускается... Это может занять до 2 минут.
echo.
echo Для проверки логов во время загрузки выполните:
echo docker-compose logs -f bugzilla
echo.
echo Дождитесь запуска и перейдите по адресу: http://localhost:8080
timeout /t 30 >nul

echo.
echo ====================================
echo = Проверка состояния контейнера =
echo ====================================
docker ps | findstr bugzilla
if %ERRORLEVEL% neq 0 (
    echo ОШИБКА: Контейнер Bugzilla не запущен!
    echo Проверьте логи:
    docker-compose logs bugzilla
    exit /b 1
)
echo Контейнер Bugzilla успешно запущен и работает.

echo.
echo ====================================
echo = Проверка доступности Bugzilla =
echo ====================================
echo.
curl -I http://localhost:8080

echo.
echo ====================================
echo = Информация о доступе =
echo ====================================
echo.
echo Адрес: http://localhost:8080
echo.
echo Учетные данные для входа:
echo - Администратор: admin@example.com / admin123
echo - Разработчик: developer@example.com / developer123 (будет создан после первого входа)
echo - Тестировщик: tester@example.com / tester123 (будет создан после первого входа)
echo - Пользователь: user@example.com / user123 (будет создан после первого входа)
echo.
echo ====================================
echo = Диагностика =
echo ====================================
echo.
echo Если BugZilla недоступна, выполните:
echo .\debug-bugzilla.bat
echo.
echo Для просмотра логов выполните:
echo docker-compose logs -f bugzilla
echo.
echo Для остановки BugZilla выполните:
echo .\stop-bugzilla.bat
echo.