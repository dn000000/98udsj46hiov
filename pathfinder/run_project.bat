@echo off
echo ===================================================
echo Запуск проекта PathFinder
echo ===================================================
echo.

echo Проверка зависимостей...
python3 -c "import numpy, matplotlib, pytest, requests" 2>nul
if %errorlevel% neq 0 (
    echo Установка зависимостей...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Ошибка при установке зависимостей.
        pause
        exit /b 1
    )
)

echo.
echo Запуск BugZilla...
cd bugzilla
start /b cmd /c "start-bugzilla.bat"
cd ..

echo.
echo Запуск тестов...
python3 run_all_tests.py

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
    python src/main.py
    goto menu
) else if "%choice%"=="2" (
    echo.
    echo Запуск демонстрации поиска равноудаленной точки...
    python src/equidistant_demo.py
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
    echo Выход из программы.
    exit /b 0
) else (
    echo.
    echo Неверный выбор. Пожалуйста, введите число от 1 до 4.
    goto menu
) 