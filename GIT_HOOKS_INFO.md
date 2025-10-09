# Git Hooks - Информация

## Автоматическое тестирование при коммитах и push

В проекте настроены Git хуки для автоматического запуска тестов:

### 🔹 Pre-commit Hook

**Когда запускается:** При каждом `git commit`

**Что делает:** Запускает **быстрые тесты** (1 тест, ~0.3 секунды)

**Команда:**
```bash
.venv/Scripts/python.exe tests/run_tests.py --fast
```

**Как увидеть процесс:**
- ✅ **Терминал Git Bash/CMD** - вывод виден полностью
- ⚠️ **VS Code GUI (Source Control)** - вывод может не отображаться в реальном времени
- ✅ **VS Code встроенный терминал** - вывод виден полностью

### 🔹 Pre-push Hook

**Когда запускается:** При каждом `git push`

**Что делает:** Запускает **ВСЕ тесты** (31 тест, ~20 секунд)

**Команда:**
```bash
.venv/Scripts/python.exe tests/run_tests.py
```

## Почему я не вижу процесс тестирования?

### В VS Code GUI (Source Control панель)

VS Code может не показывать stdout вывод Git хуков в реальном времени через GUI.

**Решение 1:** Используйте встроенный терминал VS Code
```bash
git commit -m "your message"
```

**Решение 2:** Смотрите логи в Output панели
- `Ctrl+Shift+U` → выберите "Git" в выпадающем списке

**Решение 3:** Используйте Git Bash/CMD напрямую

### Пример вывода при коммите

```
==========================================
🔄 RUNNING PRE-COMMIT TESTS...
==========================================

Running: C:\...\python.exe -m pytest tests/ -m fast -v

===== test session starts =====
...
tests/test_command_executor.py::TestQuickSmoke::test_basic_echo PASSED [100%]

====== 1 passed, 30 deselected in 0.26s =====

==========================================
✅ ALL TESTS PASSED! PROCEEDING WITH COMMIT.
==========================================

[main abc1234] your commit message
```

## Как пропустить тесты (не рекомендуется)

Если тесты мешают или вы хотите закоммитить без проверки:

```bash
# Пропустить pre-commit тесты
git commit --no-verify -m "message"

# Пропустить pre-push тесты
git push --no-verify
```

⚠️ **Внимание:** Используйте `--no-verify` только в крайних случаях!

## Статус тестов

- ✅ **Pre-commit:** 1 быстрый тест (~0.3 сек)
- ✅ **Pre-push:** 31 полный тест (~20 сек)
- ✅ **Все тесты проходят**

## Проверка хуков вручную

```bash
# Проверить pre-commit хук
bash .git/hooks/pre-commit

# Проверить pre-push хук
bash .git/hooks/pre-push
```

## Логи Git в VS Code

Чтобы увидеть полный вывод Git операций в VS Code:

1. Откройте **Output** панель: `Ctrl+Shift+U` (или View → Output)
2. В выпадающем меню выберите **"Git"**
3. Все Git команды и вывод хуков будут отображаться здесь

## Настройки VS Code для лучшей видимости

В `settings.json`:
```json
{
  "git.terminalGitEditor": true,
  "git.verboseCommit": true
}
```

---

**Последнее обновление:** 9 октября 2025 г.
