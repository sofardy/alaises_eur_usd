#!/bin/bash

echo "🔧 Исправление зависимостей для анализа ликвидности EUR/USD"
echo "============================================================"

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.8 или выше."
    exit 1
fi

echo "✅ Python найден: $(python3 --version)"

# Создание виртуального окружения если его нет
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
    echo "✅ Виртуальное окружение создано"
else
    echo "✅ Виртуальное окружение уже существует"
fi

# Активация виртуального окружения и установка зависимостей
echo "🔄 Активация виртуального окружения и установка зависимостей..."
source venv/bin/activate

# Обновление pip
pip install --upgrade pip

# Установка зависимостей
pip install -r requirements.txt

# Проверка установки openpyxl
echo "🧪 Проверка установки openpyxl..."
if python -c "import openpyxl; print('✅ openpyxl установлен успешно')" 2>/dev/null; then
    echo "✅ Все зависимости установлены корректно"
else
    echo "❌ Ошибка при установке openpyxl"
    exit 1
fi

echo ""
echo "🚀 Готово! Теперь можно запускать анализ:"
echo "   source venv/bin/activate"
echo "   python menu.py"
echo ""
