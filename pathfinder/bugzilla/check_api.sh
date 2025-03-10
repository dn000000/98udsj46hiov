#!/bin/bash

echo "Тестирование REST API Bugzilla"
echo "------------------------------"

# Фиксированный API ключ
API_KEY="DevAPIKey12345"

# Проверяем, существует ли файл с альтернативным API ключом
if [ -f "/var/www/html/bugzilla/api_key.txt" ]; then
    FILE_API_KEY=$(cat /var/www/html/bugzilla/api_key.txt)
    if [ ! -z "$FILE_API_KEY" ]; then
        API_KEY="$FILE_API_KEY"
    fi
fi

echo "Используем API ключ: $API_KEY"

# Проверка базовой доступности
echo -e "\nПроверка версии Bugzilla:"
curl -s http://localhost/rest/version | jq .

# Проверка аутентификации
echo -e "\nПроверка аутентификации:"
curl -s "http://localhost/rest/valid_login?login=developer@example.com&api_key=$API_KEY" | jq .

# Проверка получения информации о продукте
echo -e "\nПолучение информации о продукте PathFinder:"
curl -s "http://localhost/rest/product?names=PathFinder&api_key=$API_KEY" | jq .

# Создание тестовой ошибки
echo -e "\nСоздание тестовой ошибки:"
curl -s -X POST \
     -H "Content-Type: application/json" \
     -d '{
       "product": "PathFinder",
       "component": "Core",
       "summary": "Test bug via API",
       "version": "1.0",
       "description": "This is a test bug",
       "op_sys": "All",
       "platform": "All",
       "severity": "normal"
     }' \
     "http://localhost/rest/bug?api_key=$API_KEY" | jq . 