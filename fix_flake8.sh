#!/bin/bash
# Скрипт автоматического исправления flake8 ошибок
# Penguin Tamer Project
# Дата: 2025-10-09

set -e

echo "🔧 Начинаю автоматическое исправление flake8 ошибок..."
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода с цветом
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Проверка наличия инструментов
echo "📦 Проверка наличия инструментов..."

if ! command -v autopep8 &> /dev/null; then
    print_warning "autopep8 не установлен. Устанавливаю..."
    pip install autopep8
fi

if ! command -v autoflake &> /dev/null; then
    print_warning "autoflake не установлен. Устанавливаю..."
    pip install autoflake
fi

print_status "Все инструменты готовы"
echo ""

# Сохранение текущего состояния
echo "💾 Создаю резервную копию..."
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r src/ "$BACKUP_DIR/"
cp -r tests/ "$BACKUP_DIR/"
print_status "Резервная копия создана в $BACKUP_DIR"
echo ""

# 1. Удаление trailing whitespace
echo "🧹 Шаг 1/6: Удаление trailing whitespace (W291)..."
autopep8 --in-place --select=W291 --recursive src/ tests/
print_status "Trailing whitespace удалён"
echo ""

# 2. Очистка пустых строк с пробелами
echo "🧹 Шаг 2/6: Очистка пустых строк (W293)..."
autopep8 --in-place --select=W293 --recursive src/ tests/
print_status "Пустые строки очищены"
echo ""

# 3. Добавление newline в конце файлов
echo "🧹 Шаг 3/6: Добавление newline в конце файлов (W292)..."
find src/ tests/ -name "*.py" -type f | while read file; do
    if [ -n "$(tail -c1 "$file")" ]; then
        echo "" >> "$file"
    fi
done
print_status "Newline добавлены"
echo ""

# 4. Исправление пустых строк между функциями
echo "🧹 Шаг 4/6: Исправление пустых строк (E302, E305, E303)..."
autopep8 --in-place --select=E302,E303,E305,E306 --recursive src/ tests/
print_status "Пустые строки между функциями исправлены"
echo ""

# 5. Удаление неиспользуемых импортов
echo "🧹 Шаг 5/6: Удаление неиспользуемых импортов (F401)..."
autoflake --in-place --remove-all-unused-imports --recursive src/ tests/
print_status "Неиспользуемые импорты удалены"
echo ""

# 6. Проверка результата
echo "🔍 Шаг 6/6: Проверка результата..."
echo ""

BEFORE=$(flake8 src/ tests/ --max-line-length=120 --statistics --count 2>&1 | tail -1 | awk '{print $1}')
AFTER=$(flake8 src/ tests/ --max-line-length=120 --statistics --count 2>&1 | tail -1 | awk '{print $1}')

echo "📊 Результаты:"
echo "   Проблем осталось: $AFTER"
echo ""

if [ "$AFTER" -lt 100 ]; then
    print_status "Отлично! Большинство проблем исправлено!"
elif [ "$AFTER" -lt 200 ]; then
    print_warning "Хорошо, но осталось ещё поработать"
else
    print_error "Требуется ручное исправление оставшихся проблем"
fi

echo ""
echo "📝 Оставшиеся проблемы требуют ручного исправления:"
echo "   - E501: Длинные строки (>120 символов)"
echo "   - E722: Bare except (нужно указать тип исключения)"
echo "   - F841: Неиспользуемые переменные"
echo "   - E402: Импорты не в начале файла"
echo ""

echo "💡 Следующие шаги:"
echo "   1. Просмотрите изменения: git diff"
echo "   2. Запустите тесты: pytest tests/"
echo "   3. Исправьте оставшиеся проблемы вручную"
echo "   4. Создайте коммит: git commit -am 'style: auto-fix flake8 issues'"
echo ""

echo "✨ Готово! Проверьте изменения перед коммитом."
