#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Фінальна демонстрація проекту аналізу ліквідності EUR/USD
"""

import os
import pandas as pd
from datetime import datetime

def print_project_info():
    """Інформація про проект"""
    print("🚀 АНАЛІЗАТОР ЛІКВІДНОСТІ EUR/USD")
    print("=" * 50)
    print("📋 Проект реалізує повний аналіз торгових сесій:")
    print("   • Азія (02:00-10:00 UTC+3)")
    print("   • Франкфурт (09:00-10:00 UTC+3)")  
    print("   • Лондон (10:00-15:00 UTC+3)")
    print("   • Нью-Йорк (15:00-19:00 UTC+3)")
    print()

def show_project_structure():
    """Структура проекту"""
    print("📁 СТРУКТУРА ПРОЕКТУ:")
    print("-" * 25)
    
    files_info = {
        'liquidity_analyzer.py': '🔧 Основний аналізатор',
        'interactive.py': '🖥️  Інтерактивний інтерфейс',
        'validator.py': '✅ Валідація даних',
        'show_results.py': '📊 Демонстрація результатів',
        'config.py': '⚙️  Конфігурація',
        'run_analysis.sh': '🚀 Скрипт автозапуску',
        'requirements.txt': '📚 Залежності',
        'README.md': '📖 Документація',
        'DAT_MT_EURUSD_M1_202505.csv': '📈 Вхідні дані (1.7MB)',
        'liquidity_analysis_results.xlsx': '📊 Результати аналізу'
    }
    
    for file, desc in files_info.items():
        if os.path.exists(file):
            size = os.path.getsize(file)
            if size > 1024*1024:
                size_str = f"({size/(1024*1024):.1f}MB)"
            elif size > 1024:
                size_str = f"({size/1024:.0f}KB)"
            else:
                size_str = f"({size}B)"
            print(f"   {desc:<30} {size_str:>8}")
        else:
            print(f"   {desc:<30} {'❌':>8}")
    print()

def show_analysis_results():
    """Показати результати аналізу"""
    results_file = 'liquidity_analysis_results.xlsx'
    
    if not os.path.exists(results_file):
        print("❌ Файл результатів не знайдено!")
        print("   Запустіть: python liquidity_analyzer.py")
        return
    
    print("📊 РЕЗУЛЬТАТИ АНАЛІЗУ:")
    print("-" * 25)
    
    # Основні результати
    df = pd.read_excel(results_file, sheet_name='Analysis_Results')
    stats_df = pd.read_excel(results_file, sheet_name='Statistics')
    
    print(f"📅 Період аналізу: {df['date'].min()} - {df['date'].max()}")
    print(f"📊 Торгових днів: {len(df)}")
    print(f"📈 Записів у вхідних даних: 31,215 (M1 дані)")
    print()
    
    # Ключові метрики
    print("🎯 КЛЮЧОВІ МЕТРИКИ:")
    key_metrics = [
        'London Sweep High', 'London Sweep Low', 'Continue', 
        'Sweep and Reverse', 'No Sweep', 'Rebalance Yes'
    ]
    
    for metric in key_metrics:
        row = stats_df[stats_df['Metric'] == metric]
        if not row.empty:
            value = row.iloc[0]['Value']
            percentage = row.iloc[0]['Percentage']
            print(f"   {metric:<20}: {value:>2} ({percentage:>5.1f}%)")
    print()
    
    # Топ дні
    print("🏆 ТОП-3 ДНІ ЗА РОЗШИРЕННЯМ:")
    top3 = df.nlargest(3, 'extension_pips')
    for i, (_, row) in enumerate(top3.iterrows(), 1):
        print(f"   {i}. {row['date']} ({row['day_of_week']:<9}): {row['extension_pips']:>6.1f} пунктів - {row['sweep_type']}")
    print()
    
    # Статистика по сесіям
    print("📈 СЕРЕДНІ ПОКАЗНИКИ:")
    print(f"   Розширення Лондон: {df['extension_pips'].mean():.1f} ± {df['extension_pips'].std():.1f} пунктів")
    print(f"   Розширення NY вгору: {df['ny_up_extension_pips'].mean():.1f} пунктів")
    print(f"   Розширення NY вниз: {df['ny_down_extension_pips'].mean():.1f} пунктів")
    print(f"   Asia Range: {((df['asia_high'] - df['asia_low']) / 0.00010).mean():.1f} пунктів")
    print()

def show_technical_features():
    """Технічні особливості"""
    print("⚙️  ТЕХНІЧНІ ОСОБЛИВОСТІ:")
    print("-" * 30)
    print("✅ Повна реалізація технічного завдання")
    print("✅ Обробка M1 даних (31,215 записів)")
    print("✅ Автоматичне переведення у UTC+3")
    print("✅ Валідація якості даних")
    print("✅ Розрахунок всіх типів sweep")
    print("✅ Аналіз rebalance та retests")
    print("✅ Статистика по днях тижня")
    print("✅ Експорт результатів у Excel")
    print("✅ Інтерактивний інтерфейс")
    print("✅ Модульна архітектура")
    print()

def show_usage_examples():
    """Приклади використання"""
    print("🔧 СПОСОБИ ЗАПУСКУ:")
    print("-" * 20)
    print("1. Інтерактивний режим:")
    print("   python interactive.py")
    print()
    print("2. Автоматичний запуск:")
    print("   ./run_analysis.sh")
    print()
    print("3. Прямий запуск аналізу:")
    print("   python liquidity_analyzer.py")
    print()
    print("4. Показ результатів:")
    print("   python show_results.py")
    print()

def main():
    """Головна демонстрація"""
    print_project_info()
    show_project_structure()
    show_analysis_results()
    show_technical_features()
    show_usage_examples()
    
    print("🎉 ПРОЕКТ ГОТОВИЙ ДО ВИКОРИСТАННЯ!")
    print("=" * 40)
    print("📖 Детальна документація: README.md")
    print("🚀 Швидкий старт: ./run_analysis.sh")
    print("🖥️  Інтерактивний режим: python interactive.py")

if __name__ == "__main__":
    main()
