#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI приложение для анализа ликвидности EUR/USD
Простой графический интерфейс для "простых смертных"
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
import os
import subprocess
from pathlib import Path
import time

# Добавляем текущую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from liquidity_analyzer import LiquidityAnalyzer
    from batch_liquidity_analyzer import BatchLiquidityAnalyzer
except ImportError as e:
    print(f"Ошибка импорта: {e}")

class LiquidityAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Анализ ликвидности EUR/USD - Простой интерфейс")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Переменные
        self.is_processing = False
        self.current_thread = None
        
        self.setup_ui()
        self.check_dependencies()
    
    def setup_ui(self):
        """Создание интерфейса"""
        
        # Заголовок
        title_frame = ttk.Frame(self.root)
        title_frame.pack(pady=10, padx=20, fill='x')
        
        title_label = ttk.Label(
            title_frame, 
            text="📊 Анализ ликвидности EUR/USD", 
            font=('Arial', 16, 'bold')
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame, 
            text="Простой интерфейс без терминала", 
            font=('Arial', 10)
        )
        subtitle_label.pack()
        
        # Основная область с вкладками
        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=10, padx=20, fill='both', expand=True)
        
        # Вкладка 1: Один файл
        self.single_frame = ttk.Frame(notebook)
        notebook.add(self.single_frame, text="📄 Один файл")
        self.setup_single_file_tab()
        
        # Вкладка 2: Массовая обработка
        self.batch_frame = ttk.Frame(notebook)
        notebook.add(self.batch_frame, text="📁 Массовая обработка")
        self.setup_batch_tab()
        
        # Вкладка 3: Справка
        self.help_frame = ttk.Frame(notebook)
        notebook.add(self.help_frame, text="❓ Справка")
        self.setup_help_tab()
        
        # Статус бар
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side='bottom', fill='x', padx=20, pady=5)
        
        self.status_label = ttk.Label(
            self.status_frame, 
            text="✅ Готов к работе", 
            font=('Arial', 9)
        )
        self.status_label.pack(side='left')
        
        self.progress = ttk.Progressbar(
            self.status_frame, 
            mode='indeterminate'
        )
        self.progress.pack(side='right', padx=(10, 0))
    
    def setup_single_file_tab(self):
        """Настройка вкладки для анализа одного файла"""
        
        # Выбор файла
        file_frame = ttk.LabelFrame(self.single_frame, text="📂 Выбор файла", padding=10)
        file_frame.pack(pady=10, padx=10, fill='x')
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=60)
        file_entry.pack(side='left', fill='x', expand=True)
        
        browse_btn = ttk.Button(
            file_frame, 
            text="📁 Выбрать файл", 
            command=self.browse_file
        )
        browse_btn.pack(side='right', padx=(10, 0))
        
        # Кнопка анализа
        analyze_frame = ttk.Frame(self.single_frame)
        analyze_frame.pack(pady=10)
        
        self.analyze_btn = ttk.Button(
            analyze_frame,
            text="🚀 Запустить анализ",
            command=self.start_single_analysis,
            style='Accent.TButton'
        )
        self.analyze_btn.pack()
        
        # Лог
        log_frame = ttk.LabelFrame(self.single_frame, text="📝 Процесс анализа", padding=10)
        log_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        self.single_log = scrolledtext.ScrolledText(
            log_frame, 
            height=15, 
            wrap=tk.WORD,
            font=('Consolas', 9)
        )
        self.single_log.pack(fill='both', expand=True)
    
    def setup_batch_tab(self):
        """Настройка вкладки массовой обработки"""
        
        # Информация о папках
        info_frame = ttk.LabelFrame(self.batch_frame, text="📁 Папки проекта", padding=10)
        info_frame.pack(pady=10, padx=10, fill='x')
        
        files_info = ttk.Label(
            info_frame, 
            text="📥 Входные файлы: папка 'files/' (поместите туда CSV/XLSX файлы)"
        )
        files_info.pack(anchor='w')
        
        results_info = ttk.Label(
            info_frame, 
            text="📤 Результаты: папка 'results/' (Excel файлы с анализом)"
        )
        results_info.pack(anchor='w')
        
        # Статус папок
        status_frame = ttk.LabelFrame(self.batch_frame, text="📊 Статус", padding=10)
        status_frame.pack(pady=10, padx=10, fill='x')
        
        self.files_count_label = ttk.Label(status_frame, text="Подсчет файлов...")
        self.files_count_label.pack(anchor='w')
        
        # Кнопки
        buttons_frame = ttk.Frame(self.batch_frame)
        buttons_frame.pack(pady=10)
        
        refresh_btn = ttk.Button(
            buttons_frame,
            text="🔄 Обновить статус",
            command=self.update_batch_status
        )
        refresh_btn.pack(side='left', padx=5)
        
        self.batch_analyze_btn = ttk.Button(
            buttons_frame,
            text="🚀 Обработать все файлы",
            command=self.start_batch_analysis,
            style='Accent.TButton'
        )
        self.batch_analyze_btn.pack(side='left', padx=5)
        
        open_results_btn = ttk.Button(
            buttons_frame,
            text="📂 Открыть папку результатов",
            command=self.open_results_folder
        )
        open_results_btn.pack(side='left', padx=5)
        
        # Лог
        batch_log_frame = ttk.LabelFrame(self.batch_frame, text="📝 Процесс обработки", padding=10)
        batch_log_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        self.batch_log = scrolledtext.ScrolledText(
            batch_log_frame, 
            height=15, 
            wrap=tk.WORD,
            font=('Consolas', 9)
        )
        self.batch_log.pack(fill='both', expand=True)
        
        # Обновляем статус при запуске
        self.root.after(1000, self.update_batch_status)
    
    def setup_help_tab(self):
        """Настройка вкладки справки"""
        
        help_text = """
🎯 КАК ПОЛЬЗОВАТЬСЯ ПРОГРАММОЙ

📋 ТРЕБОВАНИЯ:
• Python 3.8 или новее
• Файлы данных в формате CSV или XLSX
• Формат данных: Date, Time, Open, High, Low, Close

📂 СТРУКТУРА ФАЙЛОВ:
• files/ - поместите сюда ваши CSV/XLSX файлы с данными
• results/ - здесь появятся результаты анализа в Excel

🚀 СПОСОБЫ РАБОТЫ:

1️⃣ АНАЛИЗ ОДНОГО ФАЙЛА:
   • Перейдите на вкладку "📄 Один файл"
   • Нажмите "📁 Выбрать файл" и выберите CSV/XLSX
   • Нажмите "🚀 Запустить анализ"
   • Дождитесь завершения и найдите результат в папке results/

2️⃣ МАССОВАЯ ОБРАБОТКА:
   • Скопируйте все файлы данных в папку files/
   • Перейдите на вкладку "📁 Массовая обработка"
   • Нажмите "🔄 Обновить статус" чтобы увидеть количество файлов
   • Нажмите "🚀 Обработать все файлы"
   • Дождитесь завершения (может занять много времени!)
   • Результаты появятся в папке results/

📊 РЕЗУЛЬТАТЫ:
• Каждый файл создает Excel с двумя листами:
  - Analysis_Results: детальные данные по дням
  - Statistics: общая статистика
• При массовой обработке создается сводный отчет

🔧 ФОРМАТ ВХОДНЫХ ДАННЫХ:
• Date: YYYY.MM.DD (например: 2024.01.15)
• Time: HH:MM (например: 09:30)
• Open, High, Low, Close: цены в формате 1.23456
• Volume: игнорируется

⚠️ ВАЖНЫЕ МОМЕНТЫ:
• Не закрывайте программу во время анализа
• Большие файлы (годы данных) обрабатываются долго
• При ошибках смотрите лог в нижней части окна
• Результаты автоматически открываются в папке

❓ ПРИ ПРОБЛЕМАХ:
• Проверьте формат входных данных
• Убедитесь что файлы не повреждены
• Перезапустите программу если что-то зависло
        """
        
        help_scroll = scrolledtext.ScrolledText(
            self.help_frame, 
            wrap=tk.WORD,
            font=('Arial', 10)
        )
        help_scroll.pack(fill='both', expand=True, padx=10, pady=10)
        help_scroll.insert('1.0', help_text)
        help_scroll.config(state='disabled')
    
    def check_dependencies(self):
        """Проверка зависимостей"""
        try:
            import pandas
            import openpyxl
            self.log_message("✅ Все зависимости установлены", target='both')
        except ImportError as e:
            self.log_message(f"❌ Отсутствуют зависимости: {e}", target='both')
            messagebox.showerror(
                "Ошибка зависимостей", 
                f"Не установлены необходимые библиотеки:\n{e}\n\n"
                "Запустите в терминале:\npip install pandas openpyxl"
            )
    
    def browse_file(self):
        """Выбор файла для анализа"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл данных",
            filetypes=[
                ("CSV файлы", "*.csv"),
                ("Excel файлы", "*.xlsx"),
                ("Все файлы", "*.*")
            ]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def update_batch_status(self):
        """Обновление статуса массовой обработки"""
        files_dir = Path("files")
        results_dir = Path("results")
        
        if files_dir.exists():
            csv_files = list(files_dir.glob("*.csv"))
            xlsx_files = list(files_dir.glob("*.xlsx"))
            total_files = len(csv_files) + len(xlsx_files)
        else:
            total_files = 0
        
        if results_dir.exists():
            result_files = len(list(results_dir.glob("*.xlsx")))
        else:
            result_files = 0
        
        status_text = f"📥 Входных файлов: {total_files} | 📤 Результатов: {result_files}"
        self.files_count_label.config(text=status_text)
    
    def log_message(self, message, target='single'):
        """Добавление сообщения в лог"""
        timestamp = time.strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        if target in ['single', 'both']:
            self.single_log.insert(tk.END, full_message)
            self.single_log.see(tk.END)
        
        if target in ['batch', 'both']:
            self.batch_log.insert(tk.END, full_message)
            self.batch_log.see(tk.END)
        
        self.root.update()
    
    def set_processing_state(self, processing):
        """Установка состояния обработки"""
        self.is_processing = processing
        
        if processing:
            self.analyze_btn.config(state='disabled')
            self.batch_analyze_btn.config(state='disabled')
            self.progress.start()
            self.status_label.config(text="⏳ Обработка...")
        else:
            self.analyze_btn.config(state='normal')
            self.batch_analyze_btn.config(state='normal')
            self.progress.stop()
            self.status_label.config(text="✅ Готов к работе")
    
    def start_single_analysis(self):
        """Запуск анализа одного файла"""
        if self.is_processing:
            return
        
        file_path = self.file_path_var.get().strip()
        if not file_path:
            messagebox.showwarning("Предупреждение", "Выберите файл для анализа")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("Ошибка", "Выбранный файл не существует")
            return
        
        # Очистка лога
        self.single_log.delete(1.0, tk.END)
        
        # Запуск в отдельном потоке
        self.current_thread = threading.Thread(
            target=self.run_single_analysis,
            args=(file_path,)
        )
        self.current_thread.daemon = True
        self.current_thread.start()
    
    def run_single_analysis(self, file_path):
        """Выполнение анализа одного файла"""
        try:
            self.set_processing_state(True)
            self.log_message(f"🚀 Начинаем анализ файла: {os.path.basename(file_path)}")
            
            # Создание анализатора
            analyzer = LiquidityAnalyzer()
            
            # Загрузка данных
            self.log_message("📊 Загрузка данных...")
            df = analyzer.load_data(file_path)
            self.log_message(f"✅ Загружено {len(df)} записей")
            
            # Анализ
            self.log_message("🔍 Выполнение анализа...")
            results = analyzer.analyze_period(df)
            self.log_message(f"✅ Проанализировано {len(results)} дней")
            
            # Сохранение
            output_name = f"analysis_{os.path.splitext(os.path.basename(file_path))[0]}_{int(time.time())}.xlsx"
            output_path = os.path.join("results", output_name)
            
            # Создание папки results если не существует
            os.makedirs("results", exist_ok=True)
            
            self.log_message("💾 Сохранение результатов...")
            analyzer.save_results(results, output_path)
            
            self.log_message(f"🎉 Анализ завершен! Результат: {output_path}")
            
            # Предложение открыть файл
            if messagebox.askyesno("Готово!", f"Анализ завершен!\n\nОткрыть файл результатов?\n{output_path}"):
                self.open_file(output_path)
            
        except Exception as e:
            self.log_message(f"❌ Ошибка: {str(e)}")
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")
        
        finally:
            self.set_processing_state(False)
    
    def start_batch_analysis(self):
        """Запуск массовой обработки"""
        if self.is_processing:
            return
        
        files_dir = Path("files")
        if not files_dir.exists():
            messagebox.showwarning("Предупреждение", "Папка 'files' не существует")
            return
        
        files = list(files_dir.glob("*.csv")) + list(files_dir.glob("*.xlsx"))
        if not files:
            messagebox.showwarning("Предупреждение", "В папке 'files' нет файлов CSV или XLSX")
            return
        
        # Подтверждение
        if not messagebox.askyesno(
            "Подтверждение", 
            f"Найдено {len(files)} файлов для обработки.\n\n"
            "Это может занять много времени!\n\nПродолжить?"
        ):
            return
        
        # Очистка лога
        self.batch_log.delete(1.0, tk.END)
        
        # Запуск в отдельном потоке
        self.current_thread = threading.Thread(target=self.run_batch_analysis)
        self.current_thread.daemon = True
        self.current_thread.start()
    
    def run_batch_analysis(self):
        """Выполнение массовой обработки"""
        try:
            self.set_processing_state(True)
            self.log_message("🚀 Начинаем массовую обработку", target='batch')
            
            # Создание анализатора
            batch_analyzer = BatchLiquidityAnalyzer()
            
            # Запуск обработки
            def progress_callback(current, total, filename):
                self.log_message(f"📊 [{current}/{total}] Обрабатываем: {filename}", target='batch')
            
            summary_file = batch_analyzer.process_all_files(
                input_folder="files",
                output_folder="results",
                progress_callback=progress_callback
            )
            
            self.log_message(f"🎉 Массовая обработка завершена!", target='batch')
            self.log_message(f"📈 Сводный отчет: {summary_file}", target='batch')
            
            # Обновление статуса
            self.update_batch_status()
            
            # Предложение открыть папку
            if messagebox.askyesno("Готово!", "Массовая обработка завершена!\n\nОткрыть папку с результатами?"):
                self.open_results_folder()
            
        except Exception as e:
            self.log_message(f"❌ Ошибка: {str(e)}", target='batch')
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")
        
        finally:
            self.set_processing_state(False)
    
    def open_results_folder(self):
        """Открытие папки с результатами"""
        results_path = os.path.abspath("results")
        if os.path.exists(results_path):
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", results_path])
            elif sys.platform == "win32":  # Windows
                subprocess.run(["explorer", results_path])
            else:  # Linux
                subprocess.run(["xdg-open", results_path])
        else:
            messagebox.showinfo("Информация", "Папка results пока не создана")
    
    def open_file(self, file_path):
        """Открытие файла"""
        if os.path.exists(file_path):
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", file_path])
            elif sys.platform == "win32":  # Windows
                subprocess.run(["start", file_path], shell=True)
            else:  # Linux
                subprocess.run(["xdg-open", file_path])

def main():
    """Главная функция"""
    # Создание папок если не существуют
    os.makedirs("files", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    
    # Создание и запуск GUI
    root = tk.Tk()
    app = LiquidityAnalysisGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Выход из программы...")

if __name__ == "__main__":
    main()
