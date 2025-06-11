#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Система массовой обработки файлов для анализа ликвидности EUR/USD
Автоматически обрабатывает все файлы в папке files/ и сохраняет результаты в results/
"""

import os
import glob
import pandas as pd
from datetime import datetime
import traceback
from liquidity_analyzer import LiquidityAnalyzer

class BatchLiquidityAnalyzer:
    def __init__(self, files_dir="files", results_dir="results"):
        self.files_dir = files_dir
        self.results_dir = results_dir
        self.processed_files = []
        self.failed_files = []
        
        # Создаем папки если их нет
        os.makedirs(self.files_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
    
    def get_files_list(self):
        """Получить список всех CSV и XLSX файлов в папке files/"""
        patterns = [
            os.path.join(self.files_dir, "*.csv"),
            os.path.join(self.files_dir, "*.xlsx"),
            os.path.join(self.files_dir, "*.CSV"),
            os.path.join(self.files_dir, "*.XLSX")
        ]
        
        files = []
        for pattern in patterns:
            files.extend(glob.glob(pattern))
        
        return sorted(files)
    
    def extract_file_info(self, filepath):
        """Извлечь информацию о валютной паре и периоде из имени файла"""
        filename = os.path.basename(filepath)
        
        # Удаляем расширение
        name_without_ext = os.path.splitext(filename)[0]
        
        # Пытаемся найти валютную пару
        pair = "UNKNOWN"
        if "EURUSD" in filename.upper():
            pair = "EURUSD"
        elif "EUR_USD" in filename.upper():
            pair = "EURUSD"
        elif "GBPUSD" in filename.upper():
            pair = "GBPUSD"
        elif "USDJPY" in filename.upper():
            pair = "USDJPY"
        
        # Пытаемся найти период/год
        period = "UNKNOWN"
        for year in range(2020, 2030):
            if str(year) in filename:
                period = str(year)
                break
        
        # Если не нашли год, ищем месяц
        if period == "UNKNOWN":
            months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                     'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
            for month in months:
                if month in filename.upper():
                    period = month
                    break
        
        return pair, period, name_without_ext
    
    def process_single_file(self, filepath):
        """Обработать один файл"""
        print(f"\n🔍 Обрабатываем: {os.path.basename(filepath)}")
        
        try:
            # Извлекаем информацию из имени файла
            pair, period, base_name = self.extract_file_info(filepath)
            
            # Создаем анализатор
            analyzer = LiquidityAnalyzer()
            
            # Загружаем данные
            print("   📊 Загружаем данные...")
            df = analyzer.load_data(filepath)
            
            if df is None or len(df) == 0:
                raise ValueError("Не удалось загрузить данные из файла")
            
            print(f"   ✅ Загружено {len(df):,} записей")
            
            # Анализируем данные
            print("   🔬 Выполняем анализ...")
            results = analyzer.analyze_data(df)
            
            if results is None or len(results) == 0:
                raise ValueError("Анализ не дал результатов")
            
            print(f"   ✅ Проанализировано {len(results)} торговых дней")
            
            # Формируем имя выходного файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{base_name}_{pair}_{period}_analysis_{timestamp}.xlsx"
            output_path = os.path.join(self.results_dir, output_filename)
            
            # Сохраняем результаты
            print("   💾 Сохраняем результаты...")
            analyzer.save_results(results, output_path)
            
            print(f"   ✅ Результаты сохранены: {output_filename}")
            
            # Добавляем в список успешно обработанных
            self.processed_files.append({
                'input_file': filepath,
                'output_file': output_path,
                'pair': pair,
                'period': period,
                'records_count': len(df),
                'analysis_days': len(results),
                'processing_time': datetime.now()
            })
            
            return True
            
        except Exception as e:
            error_msg = f"Ошибка при обработке {filepath}: {str(e)}"
            print(f"   ❌ {error_msg}")
            
            # Добавляем в список неудачных
            self.failed_files.append({
                'input_file': filepath,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'processing_time': datetime.now()
            })
            
            return False
    
    def create_summary_report(self):
        """Создать сводный отчет по всем обработанным файлам"""
        if not self.processed_files and not self.failed_files:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_path = os.path.join(self.results_dir, f"batch_summary_{timestamp}.xlsx")
        
        with pd.ExcelWriter(summary_path, engine='openpyxl') as writer:
            
            # Лист успешно обработанных файлов
            if self.processed_files:
                processed_df = pd.DataFrame(self.processed_files)
                processed_df['processing_time'] = processed_df['processing_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
                processed_df.to_excel(writer, sheet_name='Processed_Files', index=False)
            
            # Лист ошибок
            if self.failed_files:
                failed_df = pd.DataFrame(self.failed_files)
                failed_df['processing_time'] = failed_df['processing_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
                failed_df.to_excel(writer, sheet_name='Failed_Files', index=False)
        
        print(f"\n📊 Сводный отчет сохранен: {os.path.basename(summary_path)}")
        return summary_path
    
    def run_batch_analysis(self):
        """Запустить массовую обработку всех файлов"""
        print("🚀 Запуск массовой обработки файлов...")
        print(f"📁 Папка с файлами: {os.path.abspath(self.files_dir)}")
        print(f"📁 Папка результатов: {os.path.abspath(self.results_dir)}")
        
        # Получаем список файлов
        files_list = self.get_files_list()
        
        if not files_list:
            print(f"\n❌ В папке '{self.files_dir}' не найдены файлы CSV или XLSX")
            print("   Поместите файлы с данными в эту папку и запустите снова")
            return
        
        print(f"\n📋 Найдено файлов для обработки: {len(files_list)}")
        for i, file_path in enumerate(files_list, 1):
            print(f"   {i}. {os.path.basename(file_path)}")
        
        # Обрабатываем каждый файл
        start_time = datetime.now()
        
        for i, file_path in enumerate(files_list, 1):
            print(f"\n{'='*60}")
            print(f"📁 Файл {i}/{len(files_list)}: {os.path.basename(file_path)}")
            print(f"{'='*60}")
            
            self.process_single_file(file_path)
        
        # Итоги обработки
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n{'='*60}")
        print("🏁 ИТОГИ МАССОВОЙ ОБРАБОТКИ")
        print(f"{'='*60}")
        print(f"⏱️  Время выполнения: {duration}")
        print(f"✅ Успешно обработано: {len(self.processed_files)} файлов")
        print(f"❌ Ошибки при обработке: {len(self.failed_files)} файлов")
        print(f"📊 Всего файлов: {len(files_list)}")
        
        if self.processed_files:
            print(f"\n📈 СТАТИСТИКА ОБРАБОТАННЫХ ДАННЫХ:")
            total_records = sum(f['records_count'] for f in self.processed_files)
            total_days = sum(f['analysis_days'] for f in self.processed_files)
            print(f"   📊 Всего M1 записей: {total_records:,}")
            print(f"   📅 Всего торговых дней: {total_days:,}")
        
        if self.failed_files:
            print(f"\n❌ ФАЙЛЫ С ОШИБКАМИ:")
            for failed in self.failed_files:
                print(f"   • {os.path.basename(failed['input_file'])}: {failed['error']}")
        
        # Создаем сводный отчет
        summary_path = self.create_summary_report()
        
        print(f"\n📁 Результаты сохранены в папке: {os.path.abspath(self.results_dir)}")
        print(f"🎯 Готово! Все файлы обработаны.")


def main():
    """Главная функция для запуска массовой обработки"""
    
    print("=" * 80)
    print("🔬 СИСТЕМА МАССОВОЙ ОБРАБОТКИ ФАЙЛОВ")
    print("   Анализ ликвидности EUR/USD по торговым сессиям")
    print("=" * 80)
    
    # Создаем экземпляр батч-анализатора
    batch_analyzer = BatchLiquidityAnalyzer()
    
    # Запускаем массовую обработку
    batch_analyzer.run_batch_analysis()
    
    print(f"\n💡 Для обработки новых файлов:")
    print(f"   1. Поместите CSV/XLSX файлы в папку: {os.path.abspath('files')}")
    print(f"   2. Запустите: python batch_analyzer.py")
    print(f"   3. Результаты будут в папке: {os.path.abspath('results')}")


if __name__ == "__main__":
    main()
