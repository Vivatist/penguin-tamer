.PHONY: help install test test-fast test-cov clean install-hooks

help:
	@echo "Команды:"
	@echo "  make install       - Установить зависимости"
	@echo "  make install-hooks - Установить git hooks"
	@echo "  make test          - Запустить все тесты"
	@echo "  make test-fast     - Запустить быстрые тесты"
	@echo "  make test-cov      - Запустить тесты с покрытием"
	@echo "  make clean         - Очистить временные файлы"

install:
	pip install -r requirements.txt
	pip install pytest pytest-cov pytest-timeout

install-hooks:
	@echo "Установка git hooks..."
	@echo '#!/bin/bash' > .git/hooks/pre-commit
	@echo 'echo "🔍 Running pre-commit tests..."' >> .git/hooks/pre-commit
	@echo 'python run_tests.py --fast' >> .git/hooks/pre-commit
	@echo 'if [ $$? -ne 0 ]; then' >> .git/hooks/pre-commit
	@echo '    echo ""' >> .git/hooks/pre-commit
	@echo '    echo "❌ Fast tests failed! Commit aborted."' >> .git/hooks/pre-commit
	@echo '    echo "   Fix the tests or use \"git commit --no-verify\" to skip."' >> .git/hooks/pre-commit
	@echo '    exit 1' >> .git/hooks/pre-commit
	@echo 'fi' >> .git/hooks/pre-commit
	@echo 'echo ""' >> .git/hooks/pre-commit
	@echo 'echo "✅ All tests passed! Proceeding with commit."' >> .git/hooks/pre-commit
	@echo 'exit 0' >> .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo '#!/bin/bash' > .git/hooks/pre-push
	@echo 'echo "🚀 Running pre-push tests..."' >> .git/hooks/pre-push
	@echo 'python run_tests.py' >> .git/hooks/pre-push
	@echo 'if [ $$? -ne 0 ]; then' >> .git/hooks/pre-push
	@echo '    echo ""' >> .git/hooks/pre-push
	@echo '    echo "❌ Tests failed! Push aborted."' >> .git/hooks/pre-push
	@echo '    echo "   Fix the tests or use \"git push --no-verify\" to skip."' >> .git/hooks/pre-push
	@echo '    exit 1' >> .git/hooks/pre-push
	@echo 'fi' >> .git/hooks/pre-push
	@echo 'echo ""' >> .git/hooks/pre-push
	@echo 'echo "✅ All tests passed! Proceeding with push."' >> .git/hooks/pre-push
	@echo 'exit 0' >> .git/hooks/pre-push
	@chmod +x .git/hooks/pre-push
	@echo "✅ Git hooks установлены!"
	@echo "   Pre-commit: быстрые тесты перед коммитом"
	@echo "   Pre-push: все тесты перед push"

test:
	python run_tests.py

test-fast:
	python run_tests.py --fast

test-cov:
	python run_tests.py --cov

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	rm -rf tests/__pycache__ src/penguin_tamer/__pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
