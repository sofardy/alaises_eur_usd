#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интерактивное меню для анализа ликвидности EUR/USD
Позволяет выбрать режим работы: одиночный файл или массовая обработка
"""

import os
import sys
import glob
from liquidity_analyzer import LiquidityAnalyzer
from batch_analyzer import BatchLiquidityAnalyzer

def show_main_menu():
    """Показать главное меню"""
    print("\n" + "="*70)
    print("🔬 АНАЛИЗ ЛИКВИДНОСТИ EUR/USD ПО ТОРГОВЫМ СЕССИЯМ")
    print("="*70)
    print()
    print("Выберите режим работы:")
    print()
    print("1️⃣  Анализ одного файла (интерактивный режим)")
    print("2️⃣  Массовая обработка файлов (папка files/)")
    print("3️⃣  Показать статус папок")
    print("4️⃣  Помощь и инструкции")
    print("0️⃣  Выход")
    print()
    print("="*70)

def show_folder_status():
    """Показать статус папок files/ и results/"""
    print("\n📁 СТАТУС ПАПОК:")
    print("-" * 50)
    
    # Проверяем папку files/
    files_dir = "files"
    results_dir = "results"
    
    if os.path.exists(files_dir):
        files_list = []
        for ext in ['*.csv', '*.xlsx', '*.CSV', '*.XLSX']:
            files_list.extend(glob.glob(os.path.join(files_dir, ext)))
        
        print(f"📂 Папка {files_dir}/: {'✅ существует' if os.path.exists(files_dir) else '❌ не найдена'}")
        if files_list:
            print(f"   📊 Найдено файлов данных: {len(files_list)}")
            for i, file_path in enumerate(files_list[:5], 1):  # Показываем первые 5
                print(f"      {i}. {os.path.basename(file_path)}")
            if len(files_list) > 5:
                print(f"      ... и еще {len(files_list) - 5} файлов")
        else:
            print("   📭 Файлы не найдены")
    else:
        print(f"📂 Папка {files_dir}/: ❌ не найдена")
    
    # Проверяем папку results/
    print(f"\n📂 Папка {results_dir}/: {'✅ существует' if os.path.exists(results_dir) else '❌ не найдена'}")
    if os.path.exists(results_dir):
        results_files = glob.glob(os.path.join(results_dir, "*.xlsx"))
        if results_files:
            print(f"   📈 Файлов результатов: {len(results_files)}")
            # Показываем последние 3 файла
            recent_files = sorted(results_files, key=os.path.getmtime, reverse=True)[:3]
            for i, file_path in enumerate(recent_files, 1):
                mtime = os.path.getmtime(file_path)
                from datetime import datetime
                time_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
                print(f"      {i}. {os.path.basename(file_path)} ({time_str})")
        else:
            print("   📭 Результаты не найдены")

def show_help():
    """Показать справку"""
    print("\n📖 СПРАВКА И ИНСТРУКЦИИ:")
    print("="*70)
    
    print("\n🔧 ПОДГОТОВКА ДАННЫХ:")
    print("   • Поддерживаемые форматы: CSV, XLSX")
    print("   • Структура данных: Date, Time, Open, High, Low, Close, Volume")
    print("   • Формат даты: YYYY.MM.DD")
    print("   • Формат времени: HH:MM")
    print("   • Часовая зона: UTC+0 (будет преобразована в UTC+3)")
    print("   • Таймфрейм: M1 (1-минутные свечи)")
    
    print("\n📁 СТРУКТУРА ПАПОК:")
    print("   files/     - поместите сюда файлы с данными для массовой обработки")
    print("   results/   - здесь будут сохранены результаты анализа")
    
    print("\n🎯 РЕЖИМЫ РАБОТЫ:")
    print("   1. Одиночный файл - интерактивный выбор файла, подробный вывод")
    print("   2. Массовая обработка - автоматическая обработка всех файлов в files/")
    
    print("\n📊 РЕЗУЛЬТАТЫ АНАЛИЗА:")
    print("   • Excel файл с двумя листами: Analysis_Results и Statistics")
    print("   • Анализ по сессиям: Азия, Франкфурт, Лондон, Нью-Йорк")
    print("   • Sweep анализ, Rebalance, Extensions, PDH/PDL и др.")
    
    print("\n💡 СОВЕТЫ:")
    print("   • Для больших объемов данных используйте массовую обработку")
    print("   • Имена файлов должны содержать валютную пару (например: EURUSD)")
    print("   • Файлы с ошибками будут записаны в сводный отчет")

def run_single_file_analysis():
    """Запустить анализ одного файла"""
    print("\n🔍 АНАЛИЗ ОДНОГО ФАЙЛА")
    print("-" * 30)
    
    # Запрашиваем путь к файлу
    while True:
        file_path = input("\n📁 Введите путь к файлу (или 'q' для возврата в меню): ").strip()
        
        if file_path.lower() == 'q':
            return
        
        if not file_path:
            print("❌ Путь не может быть пустым")
            continue
        
        if not os.path.exists(file_path):
            print(f"❌ Файл не найден: {file_path}")
            continue
        
        if not (file_path.lower().endswith('.csv') or file_path.lower().endswith('.xlsx')):
            print("❌ Поддерживаются только файлы CSV и XLSX")
            continue
        
        break
    
    # Запрашиваем путь для сохранения результатов
    while True:
        output_path = input("\n💾 Путь для сохранения результатов (Enter для автоматического): ").strip()
        
        if not output_path:
            # Автоматическое имя файла
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{base_name}_analysis_{timestamp}.xlsx"
            print(f"📄 Результаты будут сохранены в: {output_path}")
            break
        
        # Проверяем директорию
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            print(f"❌ Папка не существует: {output_dir}")
            continue
        
        break
    
    # Запускаем анализ
    try:
        print("\n🚀 Начинаем анализ...")
        analyzer = LiquidityAnalyzer()
        
        # Загружаем данные
        df = analyzer.load_data(file_path)
        if df is None:
            print("❌ Не удалось загрузить данные")
            return
        
        # Анализируем
        results = analyzer.analyze_data(df)
        if results is None or len(results) == 0:
            print("❌ Анализ не дал результатов")
            return
        
        # Сохраняем
        analyzer.save_results(results, output_path)
        
        print(f"\n✅ Анализ завершен успешно!")
        print(f"📊 Проанализировано дней: {len(results)}")
        print(f"📁 Результаты сохранены: {output_path}")
        
        # Предлагаем открыть файл
        if sys.platform == "darwin":  # macOS
            os.system(f"open '{output_path}'")
        elif sys.platform == "win32":  # Windows
            os.system(f'start "" "{output_path}"')
        
    except Exception as e:
        print(f"❌ Ошибка при анализе: {str(e)}")

def run_batch_analysis():
    """Запустить массовую обработку"""
    print("\n🔬 МАССОВАЯ ОБРАБОТКА ФАЙЛОВ")
    print("-" * 30)
    
    batch_analyzer = BatchLiquidityAnalyzer()
    batch_analyzer.process_all_files()
    
    input("\n⏸️ Нажмите Enter для возврата в меню...")

def main():
    """Главная функция меню"""
    
    while True:
        show_main_menu()
        
        try:
            choice = input("Ваш выбор (0-4): ").strip()
            
            if choice == "0":
                print("\n👋 До свидания!")
                break
            
            elif choice == "1":
                run_single_file_analysis()
            
            elif choice == "2":
                run_batch_analysis()
            
            elif choice == "3":
                show_folder_status()
                input("\n⏸️ Нажмите Enter для продолжения...")
            
            elif choice == "4":
                show_help()
                input("\n⏸️ Нажмите Enter для продолжения...")
            
            else:
                print("❌ Неверный выбор. Попробуйте еще раз.")
                input("\n⏸️ Нажмите Enter для продолжения...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Работа прервана пользователем.")
            break
        except Exception as e:
            print(f"\n❌ Неожиданная ошибка: {str(e)}")
            input("\n⏸️ Нажмите Enter для продолжения...")

if __name__ == "__main__":
    main()
