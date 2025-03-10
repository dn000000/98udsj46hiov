@echo off
echo Остановка BugZilla для проекта PathFinder...
cd %~dp0
docker-compose down
echo.
echo BugZilla остановлена.
echo.