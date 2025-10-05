# Решение проблемы с альтернативным именем команды

## Проблема
После установки в интерактивном режиме с выбором имени `ai`, работает только команда `pt`, а `ai` не найдена.

## Причина
Вероятные причины:
1. Симлинк не был создан во время установки (из-за прав доступа или задержки в создании `pt`)
2. Каталог с симлинком не в PATH
3. Нужен перезапуск терминала

## Решения

### Вариант 1: Используйте скрипт create_alias.sh (рекомендуется)

```bash
# Скачайте и запустите скрипт
curl -sSL -o create_alias.sh https://raw.githubusercontent.com/Vivatist/penguin-tamer/main/create_alias.sh
bash create_alias.sh
```

Скрипт:
- Автоматически найдет путь к `pt`
- Спросит желаемое имя команды
- Создаст симлинк
- Проверит результат

### Вариант 2: Создайте симлинк вручную

```bash
# Найдите путь к pt
PT_PATH=$(which pt)
echo "pt находится в: $PT_PATH"

# Создайте симлинк для ai
ln -sf "$PT_PATH" "$(dirname "$PT_PATH")/ai"

# Проверьте
which ai
ai --version
```

Если получаете ошибку прав доступа:
```bash
sudo ln -sf "$PT_PATH" "$(dirname "$PT_PATH")/ai"
```

### Вариант 3: Используйте alias в shell

Если симлинк не работает, используйте alias:

**Для bash:**
```bash
echo "alias ai='pt'" >> ~/.bashrc
source ~/.bashrc
```

**Для zsh:**
```bash
echo "alias ai='pt'" >> ~/.zshrc
source ~/.zshrc
```

**Для fish:**
```bash
echo "alias ai='pt'" >> ~/.config/fish/config.fish
source ~/.config/fish/config.fish
```

### Вариант 4: Переустановите с исправленным скриптом

```bash
# Удалите текущую установку
pipx uninstall penguin-tamer

# Установите заново
curl -sSL -o install.sh https://raw.githubusercontent.com/Vivatist/penguin-tamer/main/install.sh
bash install.sh
# Выберите 'ai' когда будет предложено
```

Новая версия скрипта:
- ✅ Ждет 1 секунду после установки
- ✅ Ищет `pt` в нескольких местах
- ✅ Показывает подробные сообщения
- ✅ Предлагает альтернативы при ошибке

## Проверка результата

После любого из вариантов проверьте:

```bash
# Проверьте, что команда найдена
which ai
which pt

# Проверьте версию
ai --version
pt --version

# Они должны показывать одинаковую версию
```

## Дополнительная диагностика

Если ничего не помогло:

```bash
# 1. Проверьте, где установлен pt
which pt
ls -la $(which pt)

# 2. Проверьте содержимое bin директории
ls -la ~/.local/bin/ | grep -E "(pt|ai)"

# 3. Проверьте PATH
echo $PATH | tr ':' '\n' | grep local

# 4. Проверьте, что pipx видит установку
pipx list | grep penguin-tamer
```

## Помощь

Если проблема сохраняется, создайте issue с выводом команд:
```bash
which pt
ls -la ~/.local/bin/
echo $PATH
pipx list
```

GitHub Issues: https://github.com/Vivatist/penguin-tamer/issues
