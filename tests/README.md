# Тесты Penguin Tamer

Все тесты проекта находятся в этой директории.

## Структура

```
tests/
├── README.md                  # Этот файл
├── conftest.py               # Конфигурация pytest
├── test_command_executor.py  # Тесты исполнения команд
└── test_llm_client.py        # Тесты LLM клиента
```

## Запуск тестов

### Все тесты
```bash
python run_tests.py
# или
pytest tests/ -v
```

### Быстрые тесты (smoke tests)
```bash
python run_tests.py --fast
# или
pytest tests/ -m fast -v
```

### С покрытием кода
```bash
python run_tests.py --cov
# или
pytest tests/ -v --cov=src/penguin_tamer --cov-report=html
```

### Makefile/make.bat
```bash
# Linux/Mac
make test
make test-fast
make test-cov

# Windows
make.bat test
make.bat test-fast
make.bat test-cov
```

## Типы тестов

### test_command_executor.py
- **TestSuccessfulExecution**: Успешное выполнение команд
- **TestExecutionErrors**: Обработка ошибок
- **TestStreamingOutput**: Проверка потоковой передачи вывода
- **TestSpecialCases**: Граничные случаи (пустые команды, Unicode)
- **TestExecutorFactory**: Создание правильного исполнителя для ОС
- **TestQuickSmoke**: Быстрая проверка (@pytest.mark.fast)

### test_llm_client.py
- **TestLLMClient**: Базовые тесты клиента (инициализация, ошибки)
- **TestLLMClientIntegration**: Интеграционные тесты (требуют API ключ, пропускаются)

## Маркеры pytest

- `@pytest.mark.fast` - Быстрые smoke-тесты
- `@pytest.mark.slow` - Медленные тесты (долгое выполнение)
- `@pytest.mark.skip` - Пропустить тест
- `@pytest.mark.integration` - Интеграционные тесты (требуют внешние ресурсы)

## CI/CD

Тесты автоматически запускаются в GitHub Actions при каждом push/PR:
- Ubuntu + Windows
- Python 3.9, 3.11, 3.12
- См. `.github/workflows/tests.yml`

## Требования

```bash
pip install pytest pytest-cov pytest-timeout
```

Или используйте автоматическую установку:
```bash
make install       # Linux/Mac
make.bat install   # Windows
```
