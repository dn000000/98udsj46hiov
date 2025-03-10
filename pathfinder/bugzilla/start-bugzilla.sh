#!/bin/bash
echo "Запуск Bugzilla..."
docker-compose down
docker-compose build
docker-compose up -d
echo ""
echo "Bugzilla запускается, пожалуйста подождите..."
echo "Сервис будет доступен по адресу http://localhost:80"
echo ""
echo "Учетные данные:"
echo " - Администратор: admin@example.com / admin123"
echo " - Разработчик:   developer@example.com / developer123"
echo " - Тестировщик:   tester@example.com / tester123"
echo " - Пользователь:  user@example.com / user123"
echo ""
echo "Полная инициализация может занять до 3 минут. Если сайт не открывается, подождите."
echo "Для диагностики используйте скрипт debug-bugzilla.sh" 