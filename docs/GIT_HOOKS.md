# Git Hooks для Penguin Tamer

Автоматические проверки перед коммитом и push.

## Настроенные хуки

### 1. Pre-commit hook
**Файл:** `.git/hooks/pre-commit`

**Что делает:**
- Запускает быстрые тесты (`pytest -m fast`)
- Выполняется перед каждым `git commit`
- Блокирует коммит, если тесты не прошли

**Обход:**
```bash
git commit --no-verify -m "message"
```

### 2. Pre-push hook
**Файл:** `.git/hooks/pre-push`

**Что делает:**
- Запускает ВСЕ тесты (`python run_tests.py`)
- Выполняется перед каждым `git push`
- Блокирует push, если тесты не прошли

**Обход:**
```bash
git push --no-verify
```

## Установка хуков

Хуки уже установлены и готовы к работе! Но если нужно переустановить:

### Pre-commit (быстрые тесты)
```bash
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "🔍 Running pre-commit tests..."
python run_tests.py --fast
if [ $? -ne 0 ]; then
    echo "❌ Fast tests failed! Commit aborted."
    exit 1
fi
echo "✅ All tests passed!"
exit 0
EOF
chmod +x .git/hooks/pre-commit
```

### Pre-push (все тесты)
```bash
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
echo "🚀 Running pre-push tests..."
python run_tests.py
if [ $? -ne 0 ]; then
    echo "❌ Tests failed! Push aborted."
    exit 1
fi
echo "✅ All tests passed!"
exit 0
EOF
chmod +x .git/hooks/pre-push
```

## Временное отключение

### Отключить для одного коммита
```bash
git commit --no-verify -m "WIP: работа в процессе"
```

### Отключить для одного push
```bash
git push --no-verify
```

### Полное удаление хука
```bash
rm .git/hooks/pre-commit  # Удалить pre-commit
rm .git/hooks/pre-push    # Удалить pre-push
```

## Workflow

### Обычный рабочий процесс

```bash
# 1. Вносите изменения
vim src/penguin_tamer/cli.py

# 2. Коммитите (автоматически запустятся быстрые тесты)
git add .
git commit -m "feat: добавил новую фичу"
# 🔍 Running pre-commit tests...
# ✅ All tests passed!

# 3. Push (автоматически запустятся все тесты)
git push
# 🚀 Running pre-push tests...
# ✅ All tests passed!
```

### Если тесты не прошли

```bash
git commit -m "fix: исправление"
# 🔍 Running pre-commit tests...
# ❌ Fast tests failed! Commit aborted.

# Вариант 1: Исправить тесты
python run_tests.py --fast  # Проверить локально
# Исправить код...
git commit -m "fix: исправление"  # Попробовать снова

# Вариант 2: Пропустить проверку (не рекомендуется)
git commit --no-verify -m "WIP: временное решение"
```

## Что проверяется

### Pre-commit (быстрые)
- ✅ Базовая функциональность работает
- ✅ Smoke-тесты проходят
- ⏱️ Время выполнения: ~1 секунда

### Pre-push (полные)
- ✅ Все unit-тесты
- ✅ Все функциональные тесты
- ✅ Command executor тесты (11 тестов)
- ✅ LLM client тесты (3 теста)
- ⏱️ Время выполнения: ~3-5 секунд

## Преимущества

✅ **Автоматическая проверка** - не забудете запустить тесты  
✅ **Быстрая обратная связь** - узнаете об ошибках до коммита  
✅ **Чистая история** - в репозитории только работающий код  
✅ **CI/CD дружелюбно** - меньше сломанных билдов на GitHub  

## Устранение проблем

### Хук не запускается
```bash
# Проверьте права доступа
ls -l .git/hooks/pre-commit
# Должно быть: -rwxr-xr-x

# Установите права
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push
```

### Python не найден
```bash
# Проверьте, что Python в PATH
which python
python --version

# Или используйте полный путь в хуке
# python -> /usr/bin/python3
```

### Хук вызывает ошибку
```bash
# Протестируйте хук вручную
.git/hooks/pre-commit

# Посмотрите вывод и исправьте проблему
```

## Кастомизация

### Изменить команду тестирования

Отредактируйте файл `.git/hooks/pre-commit`:
```bash
# Было:
python run_tests.py --fast

# Можно изменить на:
pytest tests/ -v -x  # Остановиться на первой ошибке
pytest tests/ -k "not slow"  # Пропустить медленные
make test-fast  # Через Makefile
```

### Добавить другие проверки

```bash
#!/bin/bash
echo "🔍 Running checks..."

# Тесты
python run_tests.py --fast || exit 1

# Форматирование (если установлен black)
# black --check src/ || exit 1

# Линтинг (если установлен flake8)
# flake8 src/ || exit 1

echo "✅ All checks passed!"
```

## Shared hooks (для команды)

Хуки в `.git/hooks/` не коммитятся в репозиторий. Для команды:

1. **Создайте директорию для хуков:**
```bash
mkdir -p .githooks
```

2. **Сохраните хуки туда:**
```bash
cp .git/hooks/pre-commit .githooks/
cp .git/hooks/pre-push .githooks/
git add .githooks/
git commit -m "chore: добавил общие git hooks"
```

3. **Настройте git использовать эту директорию:**
```bash
git config core.hooksPath .githooks
```

4. **Или создайте скрипт установки:**
```bash
# install-hooks.sh
#!/bin/bash
cp .githooks/pre-commit .git/hooks/
cp .githooks/pre-push .git/hooks/
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push
echo "✅ Hooks installed!"
```

## См. также

- [tests/README.md](../tests/README.md) - Документация по тестам
- [Makefile](../Makefile) - Автоматизация через make
- [run_tests.py](../run_tests.py) - Запуск тестов
- [pytest.ini](../pytest.ini) - Конфигурация pytest
