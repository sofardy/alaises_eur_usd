#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Массовый анализ ликвидности EUR/USD для множественных файлов
Автор: GitHub Copilot
Версия: 1.0
"""

import os
import glob
import pandas as pd
from datetime import datetime
from liquidity_analyzer import LiquidityAnalyzer
import warnings

warnings.filterwarnings('ignore')


class BatchLiquidityAnalyzer:
    """Класс для массового анализа множественных CSV файлов"""
    
    def __init__(self, files_dir="files", results_dir="results"):
        self.files_dir = files_dir
        self.results_dir = results_dir
        self.analyzer = LiquidityAnalyzer()
        
        # Создаем папки если не существуют
        os.makedirs(self.files_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
    
    def find_csv_files(self):
        """Найти все CSV файлы в папке files"""
        csv_pattern = os.path.join(self.files_dir, "*.csv")
        csv_files = glob.glob(csv_pattern)
        
        # Также ищем XLSX файлы
        xlsx_pattern = os.path.join(self.files_dir, "*.xlsx")
        xlsx_files = glob.glob(xlsx_pattern)
        
        all_files = csv_files + xlsx_files
        return sorted(all_files)
    
    def extract_currency_pair(self, filename):
        """Извлечь валютную пару из имени файла"""
        basename = os.path.basename(filename).upper()
        
        # Ищем стандартные валютные пары
        pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD']
        for pair in pairs:
            if pair in basename:
                return pair
        
        # Если не найдено, возвращаем часть имени файла
        return basename.split('_')[2] if '_' in basename else 'UNKNOWN'
    
    def extract_period(self, filename):
        """Извлечь период из имени файла"""
        basename = os.path.basename(filename)
        
        # Ищем дату в формате YYYYMM
        import re
        date_match = re.search(r'(\d{6})', basename)
        if date_match:
            return date_match.group(1)
        
        # Альтернативный поиск
        date_match = re.search(r'(\d{4}\d{2})', basename)
        if date_match:
            return date_match.group(1)
        
        return datetime.now().strftime('%Y%m')
    
    def process_single_file(self, file_path):
        """Обработать один файл"""
        print(f"\n📁 Обработка файла: {os.path.basename(file_path)}")
        print("-" * 50)
        
        try:
            # Загружаем данные
            df = self.analyzer.load_data(file_path)
            
            if df is None or df.empty:
                print(f"❌ Ошибка: файл {file_path} пустой или не читается")
                return None
            
            # Анализируем
            results = self.analyzer.analyze_period(df)
            
            if results.empty:
                print(f"❌ Ошибка: не удалось проанализировать {file_path}")
                return None
            
            # Генерируем имя выходного файла
            currency_pair = self.extract_currency_pair(file_path)
            period = self.extract_period(file_path)
            
            output_filename = f"liquidity_analysis_{currency_pair}_{period}.xlsx"
            output_path = os.path.join(self.results_dir, output_filename)
            
            # Сохраняем результаты
            self.analyzer.save_results(results, output_path)
            
            print(f"✅ Результаты сохранены: {output_filename}")
            
            return {
                'file': os.path.basename(file_path),
                'currency_pair': currency_pair,
                'period': period,
                'total_days': len(results),
                'output_file': output_filename,
                'status': 'success'
            }
            
        except Exception as e:
            print(f"❌ Ошибка при обработке {file_path}: {str(e)}")
            return {
                'file': os.path.basename(file_path),
                'status': 'error',
                'error': str(e)
            }
    
    def process_all_files(self):
        """Обработать все файлы в папке files"""
        print("🚀 МАССОВЫЙ АНАЛИЗ ЛИКВИДНОСТИ")
        print("=" * 50)
        
        # Находим все файлы
        files = self.find_csv_files()
        
        if not files:
            print(f"❌ В папке '{self.files_dir}' не найдено CSV/XLSX файлов!")
            print(f"📁 Поместите файлы данных в папку '{self.files_dir}' и запустите снова.")
            return
        
        print(f"📊 Найдено файлов для обработки: {len(files)}")
        for i, file_path in enumerate(files, 1):
            print(f"  {i}. {os.path.basename(file_path)}")
        
        # Обрабатываем каждый файл
        results_summary = []
        start_time = datetime.now()
        
        for i, file_path in enumerate(files, 1):
            print(f"\n🔄 Обработка {i}/{len(files)}")
            result = self.process_single_file(file_path)
            if result:
                results_summary.append(result)
        
        # Создаем общий отчет
        self.create_summary_report(results_summary, start_time)
        
        print(f"\n✅ ОБРАБОТКА ЗАВЕРШЕНА!")
        print(f"📁 Результаты сохранены в папке: {self.results_dir}")
    
    def create_summary_report(self, results_summary, start_time):
        """Создать общий отчет по всем обработанным файлам"""
        end_time = datetime.now()
        processing_time = end_time - start_time
        
        summary_data = []
        successful_files = 0
        failed_files = 0
        
        for result in results_summary:
            if result['status'] == 'success':
                successful_files += 1
                summary_data.append({
                    'Файл': result['file'],
                    'Валютная пара': result['currency_pair'],
                    'Период': result['period'],
                    'Дней проанализировано': result['total_days'],
                    'Выходной файл': result['output_file'],
                    'Статус': 'Успешно'
                })
            else:
                failed_files += 1
                summary_data.append({
                    'Файл': result['file'],
                    'Валютная пара': '-',
                    'Период': '-',
                    'Дней проанализировано': 0,
                    'Выходной файл': '-',
                    'Статус': f"Ошибка: {result.get('error', 'Неизвестная ошибка')}"
                })
        
        # Создаем DataFrame с отчетом
        summary_df = pd.DataFrame(summary_data)
        
        # Добавляем общую статистику
        stats_data = [
            {'Метрика': 'Всего файлов', 'Значение': len(results_summary)},
            {'Метрика': 'Успешно обработано', 'Значение': successful_files},
            {'Метрика': 'Ошибок', 'Значение': failed_files},
            {'Метрика': 'Время обработки', 'Значение': str(processing_time).split('.')[0]},
            {'Метрика': 'Начало обработки', 'Значение': start_time.strftime('%Y-%m-%d %H:%M:%S')},
            {'Метрика': 'Окончание обработки', 'Значение': end_time.strftime('%Y-%m-%d %H:%M:%S')}
        ]
        stats_df = pd.DataFrame(stats_data)
        
        # Сохраняем общий отчет
        summary_file = os.path.join(self.results_dir, f"batch_analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        
        with pd.ExcelWriter(summary_file, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='Обработанные файлы', index=False)
            stats_df.to_excel(writer, sheet_name='Общая статистика', index=False)
        
        print(f"\n📊 ОБЩИЙ ОТЧЕТ:")
        print("-" * 30)
        print(f"Всего файлов: {len(results_summary)}")
        print(f"Успешно: {successful_files}")
        print(f"Ошибок: {failed_files}")
        print(f"Время обработки: {processing_time}")
        print(f"Отчет сохранен: {os.path.basename(summary_file)}")


def main():
    """Главная функция"""
    batch_analyzer = BatchLiquidityAnalyzer()
    batch_analyzer.process_all_files()


if __name__ == "__main__":
    main()
