# WiFiDash Makefile
# 构建和开发任务 / Build and development tasks

.PHONY: help install install-dev test lint format clean build upload run

PYTHON := python3
PIP := pip3

help:
	@echo "WiFiDash 构建命令 / Build Commands:"
	@echo "  make install      - 安装依赖 / Install dependencies"
	@echo "  make install-dev  - 安装开发依赖 / Install dev dependencies"
	@echo "  make test         - 运行测试 / Run tests"
	@echo "  make lint         - 代码检查 / Lint code"
	@echo "  make format       - 格式化代码 / Format code"
	@echo "  make clean        - 清理构建文件 / Clean build files"
	@echo "  make build        - 构建包 / Build package"
	@echo "  make run          - 运行应用 / Run application"

install:
	$(PIP) install -r requirements.txt

install-dev:
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .

test:
	$(PYTHON) -m pytest tests/ -v --tb=short

test-cov:
	$(PYTHON) -m pytest tests/ --cov=wifidash --cov-report=html

lint:
	flake8 src/wifidash --max-line-length=100
	mypy src/wifidash

format:
	black src/wifidash tests --line-length=100
	isort src/wifidash tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	$(PYTHON) -m build

upload: build
	twine upload dist/*

run:
	$(PYTHON) -m wifidash

run-cli:
	$(PYTHON) -m wifidash scan
