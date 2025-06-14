#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Аналіз ліквідності EUR/USD по торгових сесіях
Автор: GitHub Copilot  
Версія: 2.0 - з конвертацією UTC → Europe/Kyiv (з урахуванням DST)
"""

import pandas as pd
import numpy as np
import os
import pytz
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')


class LiquidityAnalyzer:
    """Клас для аналізу ліквідності EUR/USD по торгових сесіях"""
    
    def __init__(self):
        self.pip_size = 0.00010  # Розмір пункту для EUR/USD
        self.tolerance = 0.00030  # Допуск для Asia Mid (±3 пункти)
        
    def load_data(self, file_path):
        """Завантаження та попередня обробка даних"""
        print(f"Завантажую дані з файлу: {file_path}")
        
        try:
            # Определяем, есть ли заголовки в файле
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip().lower()
            has_header = ('date' in first_line and 'time' in first_line)

            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                if has_header:
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_csv(file_path, header=None, names=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'])

            if df.empty:
                print(f"❌ Файл пустой: {file_path}")
                return None

            # Об'єднання дати і часу з підтримкою різних форматів
            parse_success = False
            for date_fmt in ['%Y.%m.%d %H:%M', '%Y-%m-%d %H:%M', '%Y.%m.%d %H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                try:
                    # Создаем datetime как UTC
                    df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format=date_fmt, utc=True)
                    parse_success = True
                    print(f"✅ Формат даты распознан: {date_fmt}")
                    break
                except:
                    continue

            if not parse_success:
                print("❌ Не удалось распознать формат даты")
                return None

            # Конвертація з UTC в Europe/Kyiv з урахуванням DST
            try:
                kyiv_tz = pytz.timezone('Europe/Kyiv')
                df['Datetime'] = df['Datetime'].dt.tz_convert(kyiv_tz)
                print("✅ Конвертация времени: UTC → Europe/Kyiv (pytz)")
            except:
                df['Datetime'] = df['Datetime'] + pd.Timedelta(hours=3)
                print("⚠️ Конвертация времени: UTC+3 (без учета DST)")

            # Залишити необхідні колонки
            df = df[['Datetime', 'Open', 'High', 'Low', 'Close']].copy()
            df = df.drop_duplicates(subset=['Datetime']).dropna()
            df = df.sort_values('Datetime').reset_index(drop=True)
            
            print(f"✅ Завантажено {len(df)} записів")
            print(f"   Період: {df['Datetime'].min()} - {df['Datetime'].max()}")
            
            return df
            
        except Exception as e:
            print(f"❌ Помилка завантаження файлу: {e}")
            return None
    
    def get_session_data(self, df, date, start_hour, end_hour):
        """Отримання даних за сесію"""
        if not isinstance(date, pd.Timestamp):
            date = pd.Timestamp(date)
        
        if df['Datetime'].dt.tz is not None:
            if date.tz is None:
                date = date.tz_localize(df['Datetime'].dt.tz)
        
        start_time = date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        end_time = date.replace(hour=end_hour, minute=0, second=0, microsecond=0)
        
        mask = (df['Datetime'] >= start_time) & (df['Datetime'] < end_time)
        return df[mask].copy()
    
    def calculate_asia_levels(self, df, date):
        """Розрахунок рівнів Азії (02:00 - 10:00)"""
        asia_data = self.get_session_data(df, date, 2, 10)
        
        if asia_data.empty:
            return None, None, None
            
        asia_high = asia_data['High'].max()
        asia_low = asia_data['Low'].min()
        asia_mid = (asia_high + asia_low) / 2
        
        return asia_high, asia_low, asia_mid
    
    def calculate_pdh_pdl(self, df, date):
        """Розрахунок PDH/PDL (попередний день)"""
        if isinstance(date, pd.Timestamp):
            prev_date = date - pd.Timedelta(days=1)
        else:
            prev_date = pd.Timestamp(date) - pd.Timedelta(days=1)
            
        prev_day_data = self.get_session_data(df, prev_date, 0, 24)
        
        if prev_day_data.empty:
            return None, None
            
        pdh = prev_day_data['High'].max()
        pdl = prev_day_data['Low'].min()
        
        return pdh, pdl
    
    def check_frankfurt_sweep(self, df, date, asia_high, asia_low):
        """Перевірка sweep Франкфурта (09:00 - 10:00)"""
        frankfurt_data = self.get_session_data(df, date, 9, 10)
        
        if frankfurt_data.empty:
            return False, False, None, None
            
        frankfurt_high = frankfurt_data['High'].max()
        frankfurt_low = frankfurt_data['Low'].min()
        
        sweep_high = frankfurt_high >= (asia_high + self.pip_size)
        sweep_low = frankfurt_low <= (asia_low - self.pip_size)
        
        sweep_high_time = None
        sweep_low_time = None
        
        if sweep_high:
            sweep_high_time = frankfurt_data[frankfurt_data['High'] == frankfurt_high]['Datetime'].iloc[0]
        if sweep_low:
            sweep_low_time = frankfurt_data[frankfurt_data['Low'] == frankfurt_low]['Datetime'].iloc[0]
            
        return sweep_high, sweep_low, sweep_high_time, sweep_low_time
    
    def check_london_sweep(self, df, date, asia_high, asia_low):
        """Перевірка sweep Лондона (10:00 - 15:00)"""
        london_data = self.get_session_data(df, date, 10, 15)
        
        if london_data.empty:
            return False, False, None, None
            
        london_high = london_data['High'].max()
        london_low = london_data['Low'].min()
        
        sweep_high = london_high >= (asia_high + self.pip_size)
        sweep_low = london_low <= (asia_low - self.pip_size)
        
        sweep_high_time = None
        sweep_low_time = None
        
        if sweep_high:
            sweep_high_time = london_data[london_data['High'] == london_high]['Datetime'].iloc[0]
        if sweep_low:
            sweep_low_time = london_data[london_data['Low'] == london_low]['Datetime'].iloc[0]
            
        return sweep_high, sweep_low, sweep_high_time, sweep_low_time
    
    def calculate_main_direction(self, df, date, sweep_time, sweep_price):
        """Визначення основного напрямку руху після sweep"""
        if sweep_time is None:
            return None
            
        end_time = date.replace(hour=15, minute=0, second=0, microsecond=0)
        
        if sweep_time.tz is not None and end_time.tz is None:
            end_time = end_time.tz_localize(sweep_time.tz)
        elif sweep_time.tz is None and end_time.tz is not None:
            sweep_time = sweep_time.tz_localize(end_time.tz)
        
        after_sweep_data = df[(df['Datetime'] > sweep_time) & (df['Datetime'] <= end_time)]
        
        if after_sweep_data.empty:
            return None
            
        high_after_sweep = after_sweep_data['High'].max()
        low_after_sweep = after_sweep_data['Low'].min()
        
        up_move = high_after_sweep - sweep_price
        down_move = sweep_price - low_after_sweep
        
        return 'Long' if up_move > down_move else 'Short'
    
    def determine_sweep_type(self, sweep_high, sweep_low, main_direction):
        """Визначення типу sweep"""
        if not sweep_high and not sweep_low:
            return 'No Sweep'
        
        if sweep_high and main_direction == 'Long':
            return 'Continue'
        elif sweep_high and main_direction == 'Short':
            return 'Sweep and Reverse'
        elif sweep_low and main_direction == 'Short':
            return 'Continue'
        elif sweep_low and main_direction == 'Long':
            return 'Sweep and Reverse'
        
        return 'Unknown'
    
    def analyze_day(self, df, date):
        """Аналіз одного дня"""
        if isinstance(date, str):
            date = pd.Timestamp(date)
        
        if df['Datetime'].dt.tz is not None and date.tz is None:
            date = date.tz_localize(df['Datetime'].dt.tz)
        
        # Базові розрахунки
        asia_high, asia_low, asia_mid = self.calculate_asia_levels(df, date)
        if asia_high is None:
            return None
            
        pdh, pdl = self.calculate_pdh_pdl(df, date)
        
        # Sweep аналіз
        frankfurt_sweep_high, frankfurt_sweep_low, frankfurt_sweep_high_time, frankfurt_sweep_low_time = \
            self.check_frankfurt_sweep(df, date, asia_high, asia_low)
            
        london_sweep_high, london_sweep_low, london_sweep_high_time, london_sweep_low_time = \
            self.check_london_sweep(df, date, asia_high, asia_low)
        
        # Визначення основного sweep та його параметрів
        sweep_time = None
        sweep_price = None
        
        if london_sweep_high:
            sweep_time = london_sweep_high_time
            sweep_price = asia_high
        elif london_sweep_low:
            sweep_time = london_sweep_low_time
            sweep_price = asia_low
        
        # Основний напрямок
        main_direction = self.calculate_main_direction(df, date, sweep_time, sweep_price)
        
        # Тип sweep
        sweep_type = self.determine_sweep_type(london_sweep_high, london_sweep_low, main_direction)
        
        # Формування результату
        result = {
            'Date': date.strftime('%Y-%m-%d'),
            'Day_of_Week': date.strftime('%A'),
            'Asia_High': round(asia_high, 5),
            'Asia_Low': round(asia_low, 5),
            'Asia_Mid': round(asia_mid, 5),
            'Frankfurt_Sweep_High': 'Yes' if frankfurt_sweep_high else 'No',
            'Frankfurt_Sweep_Low': 'Yes' if frankfurt_sweep_low else 'No',
            'Frankfurt_Sweep_High_Time': frankfurt_sweep_high_time.strftime('%H:%M') if frankfurt_sweep_high_time else '',
            'Frankfurt_Sweep_Low_Time': frankfurt_sweep_low_time.strftime('%H:%M') if frankfurt_sweep_low_time else '',
            'London_Sweep_High': 'Yes' if london_sweep_high else 'No',
            'London_Sweep_Low': 'Yes' if london_sweep_low else 'No',
            'London_Sweep_High_Time': london_sweep_high_time.strftime('%H:%M') if london_sweep_high_time else '',
            'London_Sweep_Low_Time': london_sweep_low_time.strftime('%H:%M') if london_sweep_low_time else '',
            'Sweep_Type': sweep_type,
            'Main_Direction': main_direction if main_direction else 'No Direction',
            'PDH': round(pdh, 5) if pdh else '',
            'PDL': round(pdl, 5) if pdl else ''
        }
        
        return result
    
    def analyze_file(self, file_path, output_path=None):
        """Аналіз файлу з даними"""
        # Завантаження даних
        df = self.load_data(file_path)
        if df is None:
            return None
        
        # Отримання унікальних дат
        dates = df['Datetime'].dt.date.unique()
        print(f"Знайдено {len(dates)} унікальних дат для аналізу")
        
        # Аналіз кожного дня
        results = []
        for date in dates:
            try:
                result = self.analyze_day(df, pd.Timestamp(date))
                if result:
                    results.append(result)
                    print(f"✅ Проаналізовано: {date}")
                else:
                    print(f"⚠️ Пропущено: {date} (недостатньо даних)")
            except Exception as e:
                print(f"❌ Помилка аналізу {date}: {e}")
                continue
        
        if not results:
            print("❌ Немає результатів для збереження")
            return None
        
        # Створення DataFrame з результатами
        results_df = pd.DataFrame(results)
        
        # Збереження результатів
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_path = f"results/liquidity_analysis_{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Створення каталогу results, якщо його немає
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Збереження в Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            results_df.to_excel(writer, sheet_name='Liquidity_Analysis', index=False)
        
        print(f"\n✅ Результати збережено: {output_path}")
        print(f"📊 Проаналізовано {len(results)} днів")
        
        return results_df


def main():
    """Основна функція для запуску аналізу"""
    import sys
    
    if len(sys.argv) < 2:
        print("Використання: python liquidity_analyzer_working.py <файл_з_даними.csv>")
        print("Приклад: python liquidity_analyzer_working.py files/3_.csv")
        return
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"❌ Файл не знайдено: {file_path}")
        return
    
    # Створення аналізатора
    analyzer = LiquidityAnalyzer()
    
    # Запуск аналізу
    print("🚀 Запуск аналізу ліквідності EUR/USD з конвертацією часовых поясов...")
    print("=" * 60)
    
    results = analyzer.analyze_file(file_path)
    
    if results is not None:
        print("=" * 60)
        print("🎉 Аналіз завершено успішно!")
    else:
        print("❌ Аналіз завершено з помилкою")


if __name__ == "__main__":
    main()
