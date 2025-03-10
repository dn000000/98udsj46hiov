.PHONY: run test coverage lint clean docs

# Переменные
PYTHON = python
SRC_DIR = src
TESTS_DIR = tests
DOCS_DIR = docs
VENV_DIR = venv
COVERAGE_DIR = coverage_report

# Основные команды
run:
	$(PYTHON) $(SRC_DIR)/main.py

setup:
	pip install -r requirements.txt

test:
	pytest $(TESTS_DIR)

coverage:
	$(PYTHON) run_tests.py

lint:
	pylint $(SRC_DIR)/*.py
	pylint $(TESTS_DIR)/*.py

clean:
	rm -rf $(COVERAGE_DIR)
	rm -rf __pycache__
	rm -rf $(SRC_DIR)/__pycache__
	rm -rf $(TESTS_DIR)/__pycache__
	rm -rf .pytest_cache
	rm -rf .coverage

docs:
	mkdir -p $(DOCS_DIR)/sphinx
	sphinx-quickstart -q -p PathFinder -a "itsnotworkingatall" -v "1.0" --ext-autodoc --ext-viewcode --ext-todo $(DOCS_DIR)/sphinx
	sphinx-apidoc -o $(DOCS_DIR)/sphinx/source $(SRC_DIR)
	cd $(DOCS_DIR)/sphinx && $(MAKE) html

help:
	@echo "Доступные команды:"
	@echo "  run       - Запуск приложения"
	@echo "  setup     - Установка зависимостей"
	@echo "  test      - Запуск тестов"
	@echo "  coverage  - Запуск тестов с отчетом о покрытии"
	@echo "  lint      - Статический анализ кода"
	@echo "  clean     - Очистка проекта"
	@echo "  docs      - Генерация документации Sphinx"
	@echo "  help      - Показать эту справку" 