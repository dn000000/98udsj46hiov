#!/bin/bash
echo "Диагностика Bugzilla..."
echo ""
echo "Статус контейнеров:"
docker-compose ps
echo ""
echo "Логи bugzilla:"
docker-compose logs --tail=50 bugzilla
echo ""
echo "Логи базы данных:"
docker-compose logs --tail=20 db
echo ""
echo "Тест соединения с сервисом:"
curl -I http://localhost
echo ""
echo "Для полного сброса данных используйте команду: docker-compose down -v" 