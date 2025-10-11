# Быстрая настройка Demo Mode

## Где хранятся демо-файлы?

**Автоматически в директории конфигурации пользователя:**

- **Windows**: `%LOCALAPPDATA%\penguin-tamer\`
- **Linux**: `~/.config/penguin-tamer/`
- **macOS**: `~/Library/Application Support/penguin-tamer/`

## Запись сессии

Отредактируйте `config.yaml`:

```yaml
global:
  demo_mode: "record"
  demo_file: "demo_sessions/my_recording.json"
```

Запустите приложение → работайте как обычно → всё записывается!

**Важно**: При каждом запуске создаётся новый файл с временной меткой!
Например: `my_recording_2025-01-11_15-30-45.json`

## Воспроизведение

Найдите созданный файл с временной меткой и укажите его полное имя:

```yaml
global:
  demo_mode: "play"
  demo_file: "demo_sessions/my_recording_2025-01-11_15-30-45.json"
  demo_spinner: 1500
```

Запустите приложение → вводите что угодно → воспроизводятся записанные ответы!

## Выключить

```yaml
global:
  demo_mode: "off"
```

## Просмотр записей

### Windows
```cmd
explorer %LOCALAPPDATA%\penguin-tamer\demo_sessions
```

### Linux/macOS
```bash
ls ~/.config/penguin-tamer/demo_sessions/
```

## Типичные пути

```yaml
# При записи: demo_sessions/session1_2025-01-11_15-30-45.json
# При воспроизведении: укажите полное имя с меткой времени
demo_file: "demo_sessions/session1_2025-01-11_15-30-45.json"

# Разные папки для организации
demo_file: "presentations/demo.json"  # → presentations/demo_2025-01-11_15-30-45.json
demo_file: "tutorials/lesson1.json"   # → tutorials/lesson1_2025-01-11_15-30-45.json

# Абсолютный путь - с временной меткой
demo_file: "C:/MyDemos/special.json"  # → C:/MyDemos/special_2025-01-11_15-30-45.json
```

## Советы

- **Для презентаций**: `demo_spinner: 2000` (драматическая пауза)
- **Для быстрого теста**: `demo_spinner: 500` (минимальная задержка)
- **Организация**: Создавайте папки типа `demo_sessions/`, `tutorials/`, `presentations/`

## Проблемы?

**Файл не найден при play**: Проверьте что путь правильный и файл существует
**Не записывается**: Проверьте что `demo_mode: "record"` и права на запись
**Закончились ответы**: Запишите больше или перезапустите приложение

Полная документация: `docs/DEMO_MODE.md`
