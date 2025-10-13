# Почему изменение значения по умолчанию в dataclass не работало

## Проблема

При изменении значения в определении класса:

```python
@dataclass
class RobotTimingConfig:
    spinner_total_time: float = 10.0  # Изменили с 0.5 на 10.0
```

Спиннер всё равно показывался 0.5 секунды, а не 10 секунд.

## Причина

Python dataclass создаёт экземпляры при импорте модуля. Порядок выполнения:

1. **Определение класса** (строки 11-65):
   ```python
   @dataclass
   class RobotTimingConfig:
       spinner_total_time: float = 0.5  # Исходное значение
   ```

2. **Создание экземпляра** (строка 84):
   ```python
   DEFAULT_ROBOT_TIMING = RobotTimingConfig()  # Создаётся СРАЗУ с значением 0.5
   ```

3. **Изменение определения класса** (позже):
   ```python
   @dataclass
   class RobotTimingConfig:
       spinner_total_time: float = 10.0  # Изменили значение
   ```

**НО!** Экземпляр `DEFAULT_ROBOT_TIMING` уже создан с `spinner_total_time=0.5` и не меняется!

## Решение

Явно указать значение при создании экземпляра:

```python
DEFAULT_ROBOT_TIMING = RobotTimingConfig(
    spinner_total_time=10.0,  # Явно указываем нужное значение
)
```

Теперь при импорте создаётся экземпляр с правильным значением.

## Как работают dataclass defaults

```python
@dataclass
class Config:
    value: int = 5

# При создании БЕЗ параметров:
config1 = Config()  # config1.value = 5 (использует default)

# При создании С параметром:
config2 = Config(value=10)  # config2.value = 10 (переопределяет default)

# Если изменить определение класса:
@dataclass
class Config:
    value: int = 20  # Новый default

config3 = Config()  # config3.value = 20 (новый default)
# НО config1.value всё ещё = 5 (старое значение)!
```

## Правильный способ изменения defaults

### Вариант 1: Явное указание при создании (используется)
```python
DEFAULT_ROBOT_TIMING = RobotTimingConfig(
    spinner_total_time=10.0,  # Явно
)
```

### Вариант 2: Создать новый preset
```python
CUSTOM_ROBOT_TIMING = RobotTimingConfig(
    spinner_total_time=10.0,
    # ... другие параметры
)
```

### Вариант 3: Изменить значение после создания (НЕ рекомендуется)
```python
DEFAULT_ROBOT_TIMING = RobotTimingConfig()
DEFAULT_ROBOT_TIMING.spinner_total_time = 10.0  # Изменяем после
```

## Итог

✅ **Теперь работает**: `DEFAULT_ROBOT_TIMING.spinner_total_time = 10.0`

Спиннер будет показываться 10 секунд:
- 4 секунды: "Connecting..." (40% от 10)
- 6 секунд: "Ai thinking..." (60% от 10)
