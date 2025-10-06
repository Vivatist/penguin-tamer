# 🔧 Git Hooks - Быстрая справка

## Проблема решена! ✅

Pre-commit хук обновлен и теперь использует новую структуру тестов.

## Что сделано

1. ✅ Обновлен `.git/hooks/pre-commit` - запускает `python run_tests.py --fast`
2. ✅ Создан `.git/hooks/pre-push` - запускает `python run_tests.py` (все тесты)
3. ✅ Добавлена команда `make install-hooks` для переустановки
4. ✅ Создана документация в `docs/GIT_HOOKS.md`

## Использование

### Обычный workflow

```bash
# Делаете изменения
vim src/penguin_tamer/cli.py

# Коммитите - автоматически запустятся быстрые тесты (~1 сек)
git add .
git commit -m "feat: новая фича"
# 🔍 Running pre-commit tests...
# ✅ All tests passed!

# Push - автоматически запустятся все тесты (~3 сек)
git push
# 🚀 Running pre-push tests...
# ✅ All tests passed!
```

### Если нужно пропустить проверку

```bash
# Пропустить pre-commit
git commit --no-verify -m "WIP: работа в процессе"

# Пропустить pre-push
git push --no-verify
```

### Переустановить хуки

```bash
make install-hooks        # Linux/Mac
make.bat install-hooks    # Windows
```

## Что проверяется

| Хук | Команда | Время | Что проверяет |
|-----|---------|-------|---------------|
| **pre-commit** | `python run_tests.py --fast` | ~1 сек | Быстрые smoke-тесты (1 тест) |
| **pre-push** | `python run_tests.py` | ~3 сек | Все тесты (14 тестов) |

## Подробная документация

📖 См. [docs/GIT_HOOKS.md](GIT_HOOKS.md) для полной документации.

## Команды

```bash
# Проверить локально (без коммита)
python run_tests.py --fast    # Быстрые
python run_tests.py           # Все

# Протестировать хук вручную
.git/hooks/pre-commit

# Посмотреть содержимое хука
cat .git/hooks/pre-commit
```

Теперь можете спокойно коммитить и пушить - хуки работают! 🎉
