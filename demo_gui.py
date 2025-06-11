#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация GUI приложения
Показывает как легко использовать анализатор ликвидности
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import os

def show_demo():
    """Показать демо GUI возможностей"""
    
    root = tk.Tk()
    root.title("📋 Демо: Простой запуск анализатора")
    root.geometry("600x500")
    root.configure(bg='#f5f5f5')
    
    # Заголовок
    title_frame = ttk.Frame(root)
    title_frame.pack(pady=20, padx=20, fill='x')
    
    title_label = ttk.Label(
        title_frame, 
        text="🎯 ПРОСТОЙ ЗАПУСК - Для 'простых смертных'", 
        font=('Arial', 16, 'bold')
    )
    title_label.pack()
    
    subtitle_label = ttk.Label(
        title_frame, 
        text="Анализ ликвидности EUR/USD без терминала!", 
        font=('Arial', 11)
    )
    subtitle_label.pack(pady=5)
    
    # Основная информация
    info_frame = ttk.LabelFrame(root, text="🚀 Как запустить", padding=15)
    info_frame.pack(pady=10, padx=20, fill='both', expand=True)
    
    info_text = """
🖱️ САМЫЙ ПРОСТОЙ СПОСОБ:

📍 macOS/Linux:
   Двойной клик → "Запуск анализатора.command"

📍 Windows:
   Двойной клик → "run_gui.bat"

✨ АВТОМАТИЧЕСКИ:
   • Установит Python библиотеки
   • Создаст нужные папки
   • Откроет красивый интерфейс
   • Поможет обработать данные

🎯 БОЛЬШЕ НЕ НУЖНО:
   ❌ Знать программирование
   ❌ Работать с терминалом
   ❌ Устанавливать библиотеки вручную
   ❌ Помнить команды
   
✅ ПРОСТО НУЖНО:
   📁 Поместить файлы в папку files/
   🖱️ Нажать кнопку "Анализ"
   ☕ Подождать результат
   📊 Получить Excel с данными
    """
    
    info_label = ttk.Label(
        info_frame, 
        text=info_text,
        font=('Arial', 10),
        justify='left'
    )
    info_label.pack(anchor='w')
    
    # Кнопки
    buttons_frame = ttk.Frame(root)
    buttons_frame.pack(pady=20)
    
    def launch_gui():
        """Запуск GUI приложения"""
        root.destroy()
        os.system("python gui_app.py")
    
    def show_instructions():
        """Показать инструкции"""
        messagebox.showinfo(
            "📋 Инструкции", 
            "1. Поместите CSV/XLSX файлы в папку 'files/'\n"
            "2. Запустите: 'Запуск анализатора.command'\n"
            "3. Выберите вкладку для анализа\n"
            "4. Нажмите 'Запустить анализ'\n"
            "5. Результаты появятся в папке 'results/'"
        )
    
    def open_files_folder():
        """Открыть папку files"""
        if not os.path.exists("files"):
            os.makedirs("files")
        
        if os.name == 'posix':  # macOS/Linux
            os.system("open files/")
        else:  # Windows
            os.system("explorer files")
    
    launch_btn = ttk.Button(
        buttons_frame,
        text="🚀 Запустить GUI приложение",
        command=launch_gui,
        style='Accent.TButton'
    )
    launch_btn.pack(side='left', padx=10)
    
    instructions_btn = ttk.Button(
        buttons_frame,
        text="📋 Инструкции",
        command=show_instructions
    )
    instructions_btn.pack(side='left', padx=10)
    
    files_btn = ttk.Button(
        buttons_frame,
        text="📁 Открыть папку files",
        command=open_files_folder
    )
    files_btn.pack(side='left', padx=10)
    
    # Информация внизу
    footer_frame = ttk.Frame(root)
    footer_frame.pack(side='bottom', pady=10)
    
    footer_label = ttk.Label(
        footer_frame,
        text="💡 Создано специально для простого использования!",
        font=('Arial', 9, 'italic')
    )
    footer_label.pack()
    
    root.mainloop()

if __name__ == "__main__":
    show_demo()
