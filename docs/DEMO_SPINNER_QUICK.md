# Двухфазный спиннер - Краткая справка

## 🎯 Что это?

Спиннер с двумя фазами перед ответами LLM в демо-режиме:
1. **"Connecting..."** - имитация подключения к LLM
2. **"Thinking..."** - имитация генерации ответа

## ⚡ Быстрый старт

### Настройки в `config_demo.yaml`

```yaml
# Базовые настройки
spinner_enabled: true              # Включить/отключить

# Фаза 1: "Connecting..."
spinner_phase1_text: "Connecting..."
spinner_phase1_min_duration: 0.3   # Минимум (секунды)
spinner_phase1_max_duration: 0.8   # Максимум (секунды)

# Фаза 2: "Thinking..."
spinner_phase2_text: "Thinking..."
spinner_phase2_min_duration: 0.5   # Минимум (секунды)
spinner_phase2_max_duration: 2.0   # Максимум (секунды)
```

## 📦 Готовые пресеты

### Быстро (0.5-1.0 сек)
```yaml
spinner_phase1_min_duration: 0.2
spinner_phase1_max_duration: 0.4
spinner_phase2_min_duration: 0.3
spinner_phase2_max_duration: 0.6
```

### Нормально (0.8-2.8 сек) - по умолчанию
```yaml
spinner_phase1_min_duration: 0.3
spinner_phase1_max_duration: 0.8
spinner_phase2_min_duration: 0.5
spinner_phase2_max_duration: 2.0
```

### Медленно (2.5-5.0 сек)
```yaml
spinner_phase1_min_duration: 1.0
spinner_phase1_max_duration: 2.0
spinner_phase2_min_duration: 1.5
spinner_phase2_max_duration: 3.0
```

## 🧪 Тестирование

```bash
# Комплексный тест (4 сценария)
python test_two_phase_spinner.py

# Визуальная демонстрация (медленные фазы)
python demo_two_phase_visual.py
```

## 💡 Примеры

### Отключить спиннер
```yaml
spinner_enabled: false
```

### Русские тексты
```yaml
spinner_phase1_text: "Подключение к серверу..."
spinner_phase2_text: "Генерация ответа..."
```

### Только вторая фаза (быстрое подключение)
```yaml
spinner_phase1_min_duration: 0.1
spinner_phase1_max_duration: 0.2
spinner_phase2_min_duration: 1.0
spinner_phase2_max_duration: 2.0
```

## 📚 Полная документация

См. `docs/DEMO_TWO_PHASE_SPINNER.md`
