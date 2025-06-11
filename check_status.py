#!/usr/bin/env python3
"""
Быстрая проверка статуса проекта анализа ликвидности
"""

import os
import sys
from pathlib import Path

def check_project_status():
    """Проверка статуса всего проекта"""
    
    print("🔍 ПРОВЕРКА СТАТУСА ПРОЕКТА")
    print("=" * 50)
    
    # Проверка основных файлов
    main_files = [
        'liquidity_analyzer.py',
        'gui_app.py', 
        'menu.py',
        'batch_analyzer.py',
        'requirements.txt',
        'README.md'
    ]
    
    print("\n📁 ОСНОВНЫЕ ФАЙЛЫ:")
    for file in main_files:
        status = "✅" if os.path.exists(file) else "❌"
        print(f"   {status} {file}")
    
    # Проверка запускалок
    launchers = [
        'run_gui.sh',
        'run_gui.bat', 
        'Запуск анализатора.command'
    ]
    
    print("\n🚀 ФАЙЛЫ ЗАПУСКА:")
    for launcher in launchers:
        status = "✅" if os.path.exists(launcher) else "❌"
        executable = " (исполняемый)" if os.access(launcher, os.X_OK) else ""
        print(f"   {status} {launcher}{executable}")
    
    # Проверка папок
    folders = ['files', 'results', 'venv', '__pycache__']
    
    print("\n📂 ПАПКИ:")
    for folder in folders:
        if os.path.exists(folder):
            if folder == 'files':
                count = len(list(Path(folder).glob("*.csv"))) + len(list(Path(folder).glob("*.xlsx")))
                print(f"   ✅ {folder}/ ({count} файлов данных)")
            elif folder == 'results':
                count = len(list(Path(folder).glob("*.xlsx")))
                print(f"   ✅ {folder}/ ({count} результатов)")
            elif folder == 'venv':
                print(f"   ✅ {folder}/ (виртуальное окружение)")
            else:
                print(f"   ✅ {folder}/")
        else:
            print(f"   ❌ {folder}/")
    
    # Проверка зависимостей
    print("\n📚 ЗАВИСИМОСТИ:")
    try:
        import pandas
        print("   ✅ pandas")
    except ImportError:
        print("   ❌ pandas")
    
    try:
        import openpyxl  
        print("   ✅ openpyxl")
    except ImportError:
        print("   ❌ openpyxl")
        
    try:
        import tkinter
        print("   ✅ tkinter (GUI)")
    except ImportError:
        print("   ❌ tkinter (GUI)")
    
    # Проверка последних результатов
    results_dir = Path("results")
    if results_dir.exists():
        xlsx_files = list(results_dir.glob("*.xlsx"))
        if xlsx_files:
            latest = max(xlsx_files, key=lambda x: x.stat().st_mtime)
            print(f"\n📊 ПОСЛЕДНИЙ РЕЗУЛЬТАТ:")
            print(f"   📈 {latest.name}")
            print(f"   📅 {latest.stat().st_mtime}")
    
    print("\n" + "=" * 50)
    print("🎯 РЕКОМЕНДАЦИИ ДЛЯ ЗАПУСКА:")
    print("")
    print("   GUI:      ./run_gui.sh")
    print("   Меню:     python menu.py") 
    print("   Анализ:   python liquidity_analyzer.py")
    print("   Массово:  python batch_analyzer.py")
    print("")
    print("🎉 Проект готов к использованию!")

if __name__ == "__main__":
    check_project_status()
