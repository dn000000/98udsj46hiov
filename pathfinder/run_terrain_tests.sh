#!/bin/bash
echo "==================================================="
echo "Тестирование компонентов Этапа 3 проекта PathFinder"
echo "==================================================="
echo ""

echo "Запуск модульных тестов..."
python run_terrain_tests.py

echo ""
echo "Запуск демонстрации с разными типами местности..."
python examples/terrain_demo.py

echo ""
echo "==================================================="
echo "Для запуска полной демонстрации с DevOps-компонентами выполните:"
echo "python examples/terrain_and_devops_demo.py --env development --demo all"
echo "===================================================" 