@echo off
echo ===================================================
echo Настройка и запуск проекта PathFinder
echo ===================================================
echo.

REM Проверяем наличие виртуального окружения
if not exist "venv" (
    echo Создание виртуального окружения...
    python3 -m venv venv
    if %errorlevel% neq 0 (
        echo Ошибка при создании виртуального окружения.
        pause
        exit /b 1
    )
)

REM Активируем виртуальное окружение и устанавливаем зависимости
echo Активация виртуального окружения и установка зависимостей...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Ошибка при установке зависимостей.
    pause
    exit /b 1
)

REM Запускаем BugZilla
echo.
echo Запуск BugZilla...
cd bugzilla
start /b cmd /c "start-bugzilla.bat"
cd ..

REM Запускаем тесты
echo.
echo Запуск тестов...
python3 -m pytest tests

echo.
echo ===================================================
echo Выберите действие:
echo 1. Запустить основное приложение (поиск пути)
echo 2. Запустить демонстрацию поиска равноудаленной точки
echo 3. Открыть BugZilla в браузере
echo 4. Выход
echo ===================================================
echo.

:menu
set /p choice="Введите номер действия (1-4): "

if "%choice%"=="1" (
    echo.
    echo Запуск основного приложения...
    python3 src/main.py
    goto menu
) else if "%choice%"=="2" (
    echo.
    echo Запуск демонстрации поиска равноудаленной точки...
    python3 src/equidistant_demo.py
    goto menu
) else if "%choice%"=="3" (
    echo.
    echo Открытие BugZilla в браузере...
    start http://localhost:8080/bugzilla
    goto menu
) else if "%choice%"=="4" (
    echo.
    echo Остановка BugZilla...
    cd bugzilla
    call stop-bugzilla.bat
    cd ..
    echo.
    deactivate
    echo Выход из программы.
    exit /b 0
) else (
    echo.
    echo Неверный выбор. Пожалуйста, введите число от 1 до 4.
    goto menu
) 