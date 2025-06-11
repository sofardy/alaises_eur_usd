#!/bin/bash
# Скрипт для запуску аналізу ліквідності EUR/USD

echo "🚀 Запуск аналізу ліквідності EUR/USD..."

# Перевіряємо чи існує віртуальне середовище
if [ ! -d "venv" ]; then
    echo "📦 Створюю віртуальне середовище..."
    python3 -m venv venv
fi

# Активуємо віртуальне середовище
echo "🔧 Активую віртуальне середовище..."
source venv/bin/activate

# Встановлюємо залежності якщо потрібно
echo "📚 Перевіряю залежності..."
pip install -q pandas numpy openpyxl

# Запускаємо аналіз
echo "⚡ Запускаю аналіз..."
python liquidity_analyzer.py

echo "✅ Готово! Перевірте файл liquidity_analysis_results.xlsx"
