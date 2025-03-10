@echo off
echo ===================================================
echo Генерация документации Doxygen для проекта PathFinder
echo ===================================================
echo.

REM Проверяем наличие Doxygen
where doxygen >nul 2>&1
if %errorlevel% neq 0 (
    echo Ошибка: Doxygen не найден в системе.
    echo Установите Doxygen, выполнив:
    echo   choco install doxygen.install
    echo Или скачайте и установите вручную с http://www.doxygen.nl/download.html
    pause
    exit /b 1
)

echo Запуск генерации документации...
python generate_docs.py %*

if %errorlevel% neq 0 (
    echo Ошибка при генерации документации.
    pause
    exit /b 1
)

echo.
echo Документация успешно сгенерирована!
echo.

rem pause 