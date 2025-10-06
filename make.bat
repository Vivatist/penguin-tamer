@echo off
REM Windows batch файл для автоматизации тестирования

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="install" goto install
if "%1"=="install-hooks" goto install-hooks
if "%1"=="test" goto test
if "%1"=="test-fast" goto test-fast
if "%1"=="test-cov" goto test-cov
if "%1"=="clean" goto clean
goto help

:help
echo Команды:
echo   make.bat install       - Установить зависимости
echo   make.bat install-hooks - Установить git hooks
echo   make.bat test          - Запустить все тесты
echo   make.bat test-fast     - Запустить быстрые тесты
echo   make.bat test-cov      - Запустить тесты с покрытием
echo   make.bat clean         - Очистить временные файлы
goto end

:install
echo Установка зависимостей...
pip install -r requirements.txt
pip install pytest pytest-cov pytest-timeout
goto end

:install-hooks
echo Установка git hooks...
echo #!/bin/bash > .git\hooks\pre-commit
echo echo "Running pre-commit tests..." >> .git\hooks\pre-commit
echo python run_tests.py --fast >> .git\hooks\pre-commit
echo if [ $? -ne 0 ]; then >> .git\hooks\pre-commit
echo     echo "" >> .git\hooks\pre-commit
echo     echo "Tests failed! Commit aborted." >> .git\hooks\pre-commit
echo     exit 1 >> .git\hooks\pre-commit
echo fi >> .git\hooks\pre-commit
echo echo "All tests passed!" >> .git\hooks\pre-commit
echo exit 0 >> .git\hooks\pre-commit
echo #!/bin/bash > .git\hooks\pre-push
echo echo "Running pre-push tests..." >> .git\hooks\pre-push
echo python run_tests.py >> .git\hooks\pre-push
echo if [ $? -ne 0 ]; then >> .git\hooks\pre-push
echo     echo "" >> .git\hooks\pre-push
echo     echo "Tests failed! Push aborted." >> .git\hooks\pre-push
echo     exit 1 >> .git\hooks\pre-push
echo fi >> .git\hooks\pre-push
echo echo "All tests passed!" >> .git\hooks\pre-push
echo exit 0 >> .git\hooks\pre-push
echo Git hooks установлены!
echo   Pre-commit: быстрые тесты перед коммитом
echo   Pre-push: все тесты перед push
goto end

:test
python run_tests.py
goto end

:test-fast
python run_tests.py --fast
goto end

:test-cov
python run_tests.py --cov
goto end

:clean
echo Очистка временных файлов...
if exist __pycache__ rmdir /s /q __pycache__
if exist .pytest_cache rmdir /s /q .pytest_cache
if exist .coverage del .coverage
if exist htmlcov rmdir /s /q htmlcov
if exist tests\__pycache__ rmdir /s /q tests\__pycache__
if exist src\penguin_tamer\__pycache__ rmdir /s /q src\penguin_tamer\__pycache__
del /s /q *.pyc 2>nul
goto end

:end
exit /b 0

