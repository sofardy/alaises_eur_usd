#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Інтерактивний інтерфейс для аналізатора ліквідності
"""

import os
import sys
import pandas as pd
from datetime import datetime
from config import Config
from validator import validate_input_file

def print_header():
    """Виведення заголовку"""
    print("\n" + "="*60)
    print("🚀 АНАЛІЗАТОР ЛІКВІДНОСТІ EUR/USD")
    print("   Торгові сесії: Азія, Франкфурт, Лондон, Нью-Йорк")
    print("="*60)

def print_menu():
    """Виведення меню"""
    print("\n📋 МЕНЮ:")
    print("1. 🔍 Валідація вхідних даних")
    print("2. ⚡ Запуск повного аналізу")
    print("3. 📊 Показати результати")
    print("4. 📈 Детальна статистика")
    print("5. 🗂️  Список файлів")
    print("6. ⚙️  Налаштування")
    print("0. 🚪 Вихід")
    print("-" * 30)

def validate_data():
    """Валідація даних"""
    print("\n🔍 ВАЛІДАЦІЯ ДАНИХ")
    
    # Перевіряємо чи існує файл даних
    if not os.path.exists(Config.DEFAULT_INPUT_FILE):
        print(f"❌ Файл {Config.DEFAULT_INPUT_FILE} не знайдено!")
        return False
    
    return validate_input_file(Config.DEFAULT_INPUT_FILE)

def run_analysis():
    """Запуск аналізу"""
    print("\n⚡ ЗАПУСК АНАЛІЗУ")
    
    if not os.path.exists(Config.DEFAULT_INPUT_FILE):
        print(f"❌ Файл {Config.DEFAULT_INPUT_FILE} не знайдено!")
        return
    
    print("🔄 Запускаю аналіз...")
    try:
        from liquidity_analyzer import LiquidityAnalyzer
        
        analyzer = LiquidityAnalyzer()
        df = analyzer.load_data(Config.DEFAULT_INPUT_FILE)
        results = analyzer.analyze_period(df)
        analyzer.save_results(results, Config.DEFAULT_OUTPUT_FILE)
        
        print(f"✅ Аналіз завершено! Результати збережено у {Config.DEFAULT_OUTPUT_FILE}")
        
        # Коротка статистика
        print(f"\n📊 Коротка статистика:")
        print(f"   Оброблено днів: {len(results)}")
        print(f"   London Sweep High: {(results['london_sweep_high'] == 'Yes').sum()}")
        print(f"   London Sweep Low: {(results['london_sweep_low'] == 'Yes').sum()}")
        print(f"   Continue: {(results['sweep_type'] == 'Continue').sum()}")
        print(f"   Sweep and Reverse: {(results['sweep_type'] == 'Sweep and Reverse').sum()}")
        
    except Exception as e:
        print(f"❌ Помилка при аналізі: {e}")

def show_results():
    """Показати результати"""
    print("\n📊 РЕЗУЛЬТАТИ АНАЛІЗУ")
    
    if not os.path.exists(Config.DEFAULT_OUTPUT_FILE):
        print(f"❌ Файл результатів {Config.DEFAULT_OUTPUT_FILE} не знайдено!")
        print("   Спочатку запустіть аналіз (опція 2)")
        return
    
    try:
        df = pd.read_excel(Config.DEFAULT_OUTPUT_FILE, sheet_name='Analysis_Results')
        stats_df = pd.read_excel(Config.DEFAULT_OUTPUT_FILE, sheet_name='Statistics')
        
        print(f"📅 Період: {df['date'].min()} - {df['date'].max()}")
        print(f"📊 Оброблено днів: {len(df)}")
        
        print("\n🏆 ТОП-5 днів за розширенням:")
        top5 = df.nlargest(5, 'extension_pips')[['date', 'day_of_week', 'extension_pips', 'sweep_type']]
        for _, row in top5.iterrows():
            print(f"   {row['date']} ({row['day_of_week']:<9}): {row['extension_pips']:>6.1f} пунктів - {row['sweep_type']}")
        
        print(f"\n📈 Середнє розширення: {df['extension_pips'].mean():.1f} пунктів")
        print(f"📉 Rebalance rate: {(df['rebalance'] == 'Yes').sum()}/{len(df)} ({(df['rebalance'] == 'Yes').sum()/len(df)*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ Помилка при читанні результатів: {e}")

def show_detailed_stats():
    """Детальна статистика"""
    print("\n📈 ДЕТАЛЬНА СТАТИСТИКА")
    
    if not os.path.exists(Config.DEFAULT_OUTPUT_FILE):
        print(f"❌ Файл результатів не знайдено!")
        return
    
    try:
        df = pd.read_excel(Config.DEFAULT_OUTPUT_FILE, sheet_name='Analysis_Results')
        stats_df = pd.read_excel(Config.DEFAULT_OUTPUT_FILE, sheet_name='Statistics')
        
        print("\n📊 Загальна статистика:")
        for _, row in stats_df.iterrows():
            print(f"   {row['Metric']:<25}: {row['Value']:>3} ({row['Percentage']:>6.1f}%)")
        
        print("\n📅 Аналіз по днях тижня:")
        day_stats = df.groupby('day_of_week').agg({
            'extension_pips': 'mean',
            'sweep_type': lambda x: (x == 'Continue').sum()
        }).round(1)
        
        for day, row in day_stats.iterrows():
            print(f"   {day:<10}: {row['extension_pips']:>6.1f} пунктів, Continue: {int(row['sweep_type'])}")
        
        print(f"\n🎯 Кореляції:")
        print(f"   Asia Range vs Extension: {df[['asia_high', 'asia_low', 'extension_pips']].corr().iloc[0,2]:.3f}")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")

def list_files():
    """Список файлів"""
    print("\n🗂️  ФАЙЛИ В ПРОЕКТІ:")
    
    files = os.listdir('.')
    files.sort()
    
    for file in files:
        if file.startswith('.'):
            continue
            
        size = os.path.getsize(file)
        if size > 1024*1024:
            size_str = f"{size/(1024*1024):.1f} MB"
        elif size > 1024:
            size_str = f"{size/1024:.1f} KB"
        else:
            size_str = f"{size} B"
            
        if file.endswith(('.py', '.csv', '.xlsx', '.txt', '.md')):
            print(f"   📄 {file:<30} ({size_str:>8})")
        elif os.path.isdir(file):
            print(f"   📁 {file}/")
        else:
            print(f"   📄 {file:<30} ({size_str:>8})")

def show_settings():
    """Налаштування"""
    print("\n⚙️  ПОТОЧНІ НАЛАШТУВАННЯ:")
    print(f"   Вхідний файл: {Config.DEFAULT_INPUT_FILE}")
    print(f"   Вихідний файл: {Config.DEFAULT_OUTPUT_FILE}")
    print(f"   Часова зона: UTC+{Config.UTC_OFFSET}")
    print(f"   Розмір пункту: {Config.PIP_SIZE}")
    print(f"   Допуск Asia Mid: ±{int(Config.TOLERANCE/Config.PIP_SIZE)} пунктів")
    
    print("\n📅 Торгові сесії (UTC+3):")
    for name, session in Config.SESSIONS.items():
        print(f"   {name.capitalize():<10}: {session['start']:02d}:00 - {session['end']:02d}:00")

def main():
    """Головна функція"""
    print_header()
    
    while True:
        print_menu()
        
        try:
            choice = input("Оберіть опцію (0-6): ").strip()
            
            if choice == '0':
                print("\n👋 До побачення!")
                break
            elif choice == '1':
                validate_data()
            elif choice == '2':
                run_analysis()
            elif choice == '3':
                show_results()
            elif choice == '4':
                show_detailed_stats()
            elif choice == '5':
                list_files()
            elif choice == '6':
                show_settings()
            else:
                print("❌ Невірний вибір. Спробуйте ще раз.")
                
        except KeyboardInterrupt:
            print("\n\n👋 До побачення!")
            break
        except Exception as e:
            print(f"❌ Помилка: {e}")
        
        input("\nНатисніть Enter для продовження...")

if __name__ == "__main__":
    main()
