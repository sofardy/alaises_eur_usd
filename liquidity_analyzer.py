#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Аналіз ліквідності EUR/USD по торгових сесіях
Автор: GitHub Copilot
Версія: 1.0
"""

import pandas as pd
import numpy as np
import os
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
            # Определяем тип файла
            if file_path.endswith('.xlsx'):
                # Читаємо XLSX файл
                df = pd.read_excel(file_path, header=None, names=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
            else:
                # Читаємо CSV файл
                df = pd.read_csv(file_path, header=None, names=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
            
            if df.empty:
                print(f"❌ Файл пустой: {file_path}")
                return None
            
            # Об'єднання дати і часу
            df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%Y.%m.%d %H:%M')
            
            # Переведення у UTC+3
            df['Datetime'] = df['Datetime'] + pd.Timedelta(hours=3)
            
            # Залишаємо тільки потрібні колонки
            df = df[['Datetime', 'Open', 'High', 'Low', 'Close']].copy()
            
            # Сортуємо по даті
            df = df.sort_values('Datetime').reset_index(drop=True)
            
            print(f"Завантажено {len(df)} записів")
            print(f"Період: з {df['Datetime'].min()} до {df['Datetime'].max()}")
            
            return df
            
        except Exception as e:
            print(f"❌ Ошибка при загрузке файла {file_path}: {str(e)}")
            return None
    
    def get_session_data(self, df, date, start_hour, end_hour):
        """Отримати дані для конкретної сесії"""
        session_start = pd.Timestamp(date) + pd.Timedelta(hours=start_hour)
        session_end = pd.Timestamp(date) + pd.Timedelta(hours=end_hour)
        
        # Якщо сесія переходить на наступний день
        if end_hour < start_hour:
            session_end += pd.Timedelta(days=1)
            
        mask = (df['Datetime'] >= session_start) & (df['Datetime'] < session_end)
        return df[mask].copy()
    
    def calculate_asia_levels(self, df, date):
        """Розрахунок Asia High/Low/Mid для конкретної дати"""
        asia_data = self.get_session_data(df, date, 2, 10)  # 02:00 - 10:00
        
        if asia_data.empty:
            return None, None, None
            
        asia_high = asia_data['High'].max()
        asia_low = asia_data['Low'].min()
        asia_mid = (asia_high + asia_low) / 2
        
        return asia_high, asia_low, asia_mid
    
    def calculate_pdh_pdl(self, df, date):
        """Розрахунок PDH/PDL (попередній день)"""
        prev_date = pd.Timestamp(date) - pd.Timedelta(days=1)
        prev_day_data = self.get_session_data(df, prev_date, 0, 24)  # Весь попередній день
        
        if prev_day_data.empty:
            return None, None
            
        pdh = prev_day_data['High'].max()
        pdl = prev_day_data['Low'].min()
        
        return pdh, pdl
    
    def check_frankfurt_sweep(self, df, date, asia_high, asia_low):
        """Перевірка Frankfurt Sweep (09:00-10:00)"""
        frankfurt_data = self.get_session_data(df, date, 9, 10)
        
        if frankfurt_data.empty or asia_high is None or asia_low is None:
            return False, False, None, None
            
        frankfurt_high = frankfurt_data['High'].max()
        frankfurt_low = frankfurt_data['Low'].min()
        
        sweep_high = frankfurt_high >= (asia_high + self.pip_size)
        sweep_low = frankfurt_low <= (asia_low - self.pip_size)
        
        # Знаходимо час sweep
        sweep_high_time = None
        sweep_low_time = None
        
        if sweep_high:
            high_idx = frankfurt_data[frankfurt_data['High'] == frankfurt_high].index[0]
            sweep_high_time = df.loc[high_idx, 'Datetime']
            
        if sweep_low:
            low_idx = frankfurt_data[frankfurt_data['Low'] == frankfurt_low].index[0]
            sweep_low_time = df.loc[low_idx, 'Datetime']
        
        return sweep_high, sweep_low, sweep_high_time, sweep_low_time
    
    def check_london_sweep(self, df, date, asia_high, asia_low):
        """Перевірка London Sweep (10:00-15:00)"""
        london_data = self.get_session_data(df, date, 10, 15)
        
        if london_data.empty or asia_high is None or asia_low is None:
            return False, False, None, None, None, None
            
        london_high = london_data['High'].max()
        london_low = london_data['Low'].min()
        
        sweep_high = london_high >= (asia_high + self.pip_size)
        sweep_low = london_low <= (asia_low - self.pip_size)
        
        # Знаходимо час і ціну sweep
        sweep_price = None
        sweep_time = None
        sweep_high_time = None
        sweep_low_time = None
        
        if sweep_high:
            high_idx = london_data[london_data['High'] == london_high].index[0]
            sweep_high_time = df.loc[high_idx, 'Datetime']
                
        if sweep_low:
            low_idx = london_data[london_data['Low'] == london_low].index[0]
            sweep_low_time = df.loc[low_idx, 'Datetime']
            
        # Визначаємо який sweep відбувся першим та встановлюємо відповідну ціну
        if sweep_high and sweep_low:
            if sweep_high_time <= sweep_low_time:
                sweep_price = asia_high
                sweep_time = sweep_high_time
            else:
                sweep_price = asia_low
                sweep_time = sweep_low_time
        elif sweep_high:
            sweep_price = asia_high
            sweep_time = sweep_high_time
        elif sweep_low:
            sweep_price = asia_low
            sweep_time = sweep_low_time
        
        return sweep_high, sweep_low, sweep_price, sweep_time, sweep_high_time, sweep_low_time
    
    def determine_london_direction(self, df, date, sweep_time, sweep_price):
        """Визначення основного напрямку руху в Лондоні"""
        
        # Якщо є sweep - аналізуємо після sweep
        if sweep_time is not None and sweep_price is not None:
            london_end = sweep_time.replace(hour=15, minute=0, second=0, microsecond=0)
            after_sweep_data = df[(df['Datetime'] > sweep_time) & (df['Datetime'] <= london_end)]
            
            if not after_sweep_data.empty:
                max_high = after_sweep_data['High'].max()
                min_low = after_sweep_data['Low'].min()
                
                up_move = max_high - sweep_price
                down_move = sweep_price - min_low
                
                return 'Long' if up_move > down_move else 'Short'
        
        # Якщо немає sweep - аналізуємо всю Лондонську сесію
        london_data = self.get_session_data(df, date, 10, 15)  # 10:00 - 15:00
        
        if london_data.empty:
            return None
            
        london_open = london_data.iloc[0]['Open']  # Відкриття Лондону о 10:00
        london_high = london_data['High'].max()
        london_low = london_data['Low'].min()
        
        up_move = london_high - london_open
        down_move = london_open - london_low
        
        return 'Long' if up_move > down_move else 'Short'
    
    def determine_sweep_type(self, sweep_high, sweep_low, london_direction, asia_high, asia_low, sweep_price):
        """Визначення типу sweep"""
        if not sweep_high and not sweep_low:
            return 'No Sweep'
            
        # Якщо є sweep, але не можемо визначити напрямок - все одно аналізуємо
        if london_direction is None:
            return 'No Sweep'
            
        # Визначаємо який sweep відбувся
        if sweep_high and (not sweep_low or sweep_price == asia_high):
            # Sweep Asia High
            if london_direction == 'Long':
                return 'Continue'
            else:
                return 'Sweep and Reverse'
        elif sweep_low and (not sweep_high or sweep_price == asia_low):
            # Sweep Asia Low
            if london_direction == 'Short':
                return 'Continue'
            else:
                return 'Sweep and Reverse'
                
        return 'No Sweep'
    
    def check_rebalance(self, df, sweep_time, sweep_type, asia_mid, london_direction):
        """Перевірка Rebalance"""
        if sweep_type != 'Sweep and Reverse' or sweep_time is None:
            return 'No'
            
        # Дані після sweep до 15:00
        london_end = sweep_time.replace(hour=15, minute=0, second=0, microsecond=0)
        after_sweep_data = df[(df['Datetime'] > sweep_time) & (df['Datetime'] <= london_end)]
        
        if after_sweep_data.empty:
            return 'No'
            
        # Перевіряємо дотик до Asia Mid ±3 пункти
        touched_mid = False
        mid_touch_time = None
        
        for idx, row in after_sweep_data.iterrows():
            if abs(row['High'] - asia_mid) <= self.tolerance or abs(row['Low'] - asia_mid) <= self.tolerance:
                touched_mid = True
                mid_touch_time = row['Datetime']
                break
                
        if not touched_mid:
            return 'No'
            
        # Перевіряємо чи після дотику ціна пішла проти основного руху
        after_mid_data = after_sweep_data[after_sweep_data['Datetime'] > mid_touch_time]
        
        if after_mid_data.empty:
            return 'No'
            
        # Логіка перевірки продовження руху проти основного напрямку
        if london_direction == 'Long':
            # Основний рух вгору, але після rebalance має йти вниз
            min_after_mid = after_mid_data['Low'].min()
            return 'Yes' if min_after_mid < (asia_mid - self.pip_size) else 'No'
        else:
            # Основний рух вниз, але після rebalance має йти вгору
            max_after_mid = after_mid_data['High'].max()
            return 'Yes' if max_after_mid > (asia_mid + self.pip_size) else 'No'
    
    def calculate_extensions(self, df, date, sweep_time, sweep_price, sweep_high, sweep_low, asia_range):
        """Розрахунок розширень після sweep або від початку Лондону"""
        if asia_range == 0:
            return 0, 0, None, None, 0, 0
            
        # Якщо є sweep - рахуємо від sweep
        if sweep_time is not None and sweep_price is not None:
            # Дані після sweep до 15:00
            london_end = sweep_time.replace(hour=15, minute=0, second=0, microsecond=0)
            after_sweep_data = df[(df['Datetime'] > sweep_time) & (df['Datetime'] <= london_end)]
            
            if after_sweep_data.empty:
                return 0, 0, None, None, 0, 0
                
            max_high = after_sweep_data['High'].max()
            min_low = after_sweep_data['Low'].min()
            
            # Час досягнення максимуму і мінімуму
            max_time = after_sweep_data[after_sweep_data['High'] == max_high]['Datetime'].iloc[0]
            min_time = after_sweep_data[after_sweep_data['Low'] == min_low]['Datetime'].iloc[0]
            
            # Розширення в пунктах від sweep price
            if sweep_high:
                extension_pips = (max_high - sweep_price) / self.pip_size
                reverse_pips = (sweep_price - min_low) / self.pip_size
            else:
                extension_pips = (sweep_price - min_low) / self.pip_size
                reverse_pips = (max_high - sweep_price) / self.pip_size
                
        else:
            # Якщо немає sweep - рахуємо від початку Лондону (10:00)
            london_data = self.get_session_data(df, date, 10, 15)  # 10:00 - 15:00
            
            if london_data.empty:
                return 0, 0, None, None, 0, 0
                
            london_open = london_data.iloc[0]['Open']  # Ціна на 10:00
            max_high = london_data['High'].max()
            min_low = london_data['Low'].min()
            
            # Час досягнення максимуму і мінімуму
            max_time = london_data[london_data['High'] == max_high]['Datetime'].iloc[0]
            min_time = london_data[london_data['Low'] == min_low]['Datetime'].iloc[0]
            
            # Розширення в пунктах від London Open (10:00)
            up_move = max_high - london_open
            down_move = london_open - min_low
            
            if up_move > down_move:
                # Основний рух вгору
                extension_pips = up_move / self.pip_size
                reverse_pips = down_move / self.pip_size
            else:
                # Основний рух вниз
                extension_pips = down_move / self.pip_size
                reverse_pips = up_move / self.pip_size
            
        # Розширення у відсотках від Asia Range
        extension_percent = (extension_pips * self.pip_size / asia_range) * 100
        reverse_percent = (reverse_pips * self.pip_size / asia_range) * 100
        
        return extension_pips, extension_percent, max_time, min_time, reverse_pips, reverse_percent
    
    def check_retests(self, df, sweep_time, sweep_price, asia_mid):
        """Перевірка retests"""
        if sweep_time is None:
            return 'No', 'No'
            
        # Дані після sweep до 15:00
        london_end = sweep_time.replace(hour=15, minute=0, second=0, microsecond=0)
        after_sweep_data = df[(df['Datetime'] > sweep_time) & (df['Datetime'] <= london_end)]
        
        if after_sweep_data.empty:
            return 'No', 'No'
            
        # Retest Asia Sweep Level
        retest_sweep = 'No'
        for idx, row in after_sweep_data.iterrows():
            if abs(row['High'] - sweep_price) <= self.tolerance or abs(row['Low'] - sweep_price) <= self.tolerance:
                retest_sweep = 'Yes'
                break
                
        # Asia Mid Retest
        retest_mid = 'No'
        for idx, row in after_sweep_data.iterrows():
            if abs(row['High'] - asia_mid) <= self.tolerance or abs(row['Low'] - asia_mid) <= self.tolerance:
                retest_mid = 'Yes'
                break
                
        return retest_sweep, retest_mid
    
    def check_pdh_pdl_sweep(self, df, date, pdh, pdl):
        """Перевірка Sweep PDH/PDL"""
        london_data = self.get_session_data(df, date, 10, 15)
        
        if london_data.empty or pdh is None or pdl is None:
            return 'No', 'No', None, None
            
        london_high = london_data['High'].max()
        london_low = london_data['Low'].min()
        
        sweep_pdh = 'Yes' if london_high >= (pdh + self.pip_size) else 'No'
        sweep_pdl = 'Yes' if london_low <= (pdl - self.pip_size) else 'No'
        
        # Час sweep
        pdh_time = None
        pdl_time = None
        
        if sweep_pdh == 'Yes':
            high_idx = london_data[london_data['High'] == london_high].index[0]
            pdh_time = df.loc[high_idx, 'Datetime']
            
        if sweep_pdl == 'Yes':
            low_idx = london_data[london_data['Low'] == london_low].index[0]
            pdl_time = df.loc[low_idx, 'Datetime']
        
        return sweep_pdh, sweep_pdl, pdh_time, pdl_time
    
    def analyze_new_york_session(self, df, date, asia_high, asia_low, london_direction):
        """Аналіз Нью-Йоркської сесії"""
        ny_data = self.get_session_data(df, date, 15, 19)  # 15:00 - 19:00
        
        if ny_data.empty:
            return {
                'ny_direction': None,
                'ny_status': None,
                'ny_up_extension_pips': 0,
                'ny_up_extension_percent': 0,
                'ny_down_extension_pips': 0,
                'ny_down_extension_percent': 0,
                'ny_max_high_time': None,
                'ny_min_low_time': None
            }
            
        # NY Open - перша свічка о 15:00
        ny_open = ny_data.iloc[0]['Open']
        ny_high = ny_data['High'].max()
        ny_low = ny_data['Low'].min()
        
        # Визначення напрямку NY
        up_move = ny_high - ny_open
        down_move = ny_open - ny_low
        ny_direction = 'Long' if up_move > down_move else 'Short'
        
        # Визначення статусу
        if london_direction is None:
            ny_status = None
        elif london_direction == ny_direction:
            ny_status = 'Support'
        else:
            ny_status = 'Reverse'
            
        # Розширення в пунктах
        ny_up_extension_pips = up_move / self.pip_size
        ny_down_extension_pips = down_move / self.pip_size
        
        # Розширення у відсотках від Asia Range
        asia_range = asia_high - asia_low if (asia_high and asia_low) else 0
        ny_up_extension_percent = (up_move / asia_range * 100) if asia_range > 0 else 0
        ny_down_extension_percent = (down_move / asia_range * 100) if asia_range > 0 else 0
        
        # Час досягнення максимуму і мінімуму
        ny_max_high_time = ny_data[ny_data['High'] == ny_high]['Datetime'].iloc[0]
        ny_min_low_time = ny_data[ny_data['Low'] == ny_low]['Datetime'].iloc[0]
        
        return {
            'ny_direction': ny_direction,
            'ny_status': ny_status,
            'ny_up_extension_pips': round(ny_up_extension_pips, 5),
            'ny_up_extension_percent': round(ny_up_extension_percent, 5),
            'ny_down_extension_pips': round(ny_down_extension_pips, 5),
            'ny_down_extension_percent': round(ny_down_extension_percent, 5),
            'ny_max_high_time': ny_max_high_time.strftime('%H:%M') if ny_max_high_time is not None else None,
            'ny_min_low_time': ny_min_low_time.strftime('%H:%M') if ny_min_low_time is not None else None
        }
    
    def analyze_day(self, df, date):
        """Аналіз одного дня"""
        date_str = date.strftime('%Y-%m-%d')
        day_name = date.strftime('%A')
        
        # Розрахунок Asia рівнів
        asia_high, asia_low, asia_mid = self.calculate_asia_levels(df, date)
        
        if asia_high is None:
            return None  # Немає даних для цього дня
            
        asia_range = asia_high - asia_low
        
        # Розрахунок PDH/PDL
        pdh, pdl = self.calculate_pdh_pdl(df, date)
        
        # Frankfurt Sweep
        frankfurt_sweep_high, frankfurt_sweep_low, frankfurt_high_time, frankfurt_low_time = \
            self.check_frankfurt_sweep(df, date, asia_high, asia_low)
        
        # London Sweep
        london_sweep_high, london_sweep_low, sweep_price, sweep_time, london_high_time, london_low_time = \
            self.check_london_sweep(df, date, asia_high, asia_low)
        
        # Основний рух Лондону
        london_direction = self.determine_london_direction(df, date, sweep_time, sweep_price)
        
        # Тип sweep
        sweep_type = self.determine_sweep_type(
            london_sweep_high, london_sweep_low, london_direction, 
            asia_high, asia_low, sweep_price
        )
        
        # Rebalance
        rebalance = self.check_rebalance(df, sweep_time, sweep_type, asia_mid, london_direction)
        
        # Розширення
        extension_pips, extension_percent, max_time, min_time, reverse_pips, reverse_percent = \
            self.calculate_extensions(
                df, date, sweep_time, sweep_price, london_sweep_high, london_sweep_low, asia_range
            )
        
        # Retests
        retest_sweep, retest_mid = self.check_retests(df, sweep_time, sweep_price, asia_mid)
        
        # PDH/PDL Sweep
        sweep_pdh, sweep_pdl, pdh_time, pdl_time = self.check_pdh_pdl_sweep(df, date, pdh, pdl)
        
        # Аналіз Нью-Йорку
        ny_analysis = self.analyze_new_york_session(df, date, asia_high, asia_low, london_direction)
        
        return {
            'date': date_str,
            'day_of_week': day_name,
            'asia_high': round(asia_high, 5),
            'asia_low': round(asia_low, 5),
            'asia_mid': round(asia_mid, 5),
            'frankfurt_sweep_high': 'Yes' if frankfurt_sweep_high else 'No',
            'frankfurt_sweep_low': 'Yes' if frankfurt_sweep_low else 'No',
            'frankfurt_high_time': frankfurt_high_time.strftime('%H:%M') if frankfurt_high_time else None,
            'frankfurt_low_time': frankfurt_low_time.strftime('%H:%M') if frankfurt_low_time else None,
            'london_sweep_high': 'Yes' if london_sweep_high else 'No',
            'london_sweep_low': 'Yes' if london_sweep_low else 'No',
            'london_sweep_asia_high_time': london_high_time.strftime('%H:%M') if london_high_time and london_sweep_high else None,
            'london_sweep_asia_low_time': london_low_time.strftime('%H:%M') if london_low_time and london_sweep_low else None,
            'london_high_time': london_high_time.strftime('%H:%M') if london_high_time else None,
            'london_low_time': london_low_time.strftime('%H:%M') if london_low_time else None,
            'sweep_type': sweep_type,
            'london_direction': london_direction,
            'rebalance': rebalance,
            'extension_pips': round(extension_pips, 1),
            'extension_percent': round(extension_percent, 2),
            'max_time': max_time.strftime('%H:%M') if max_time else None,
            'min_time': min_time.strftime('%H:%M') if min_time else None,
            'reverse_pips': round(reverse_pips, 1),
            'reverse_percent': round(reverse_percent, 2),
            'retest_sweep_level': retest_sweep,
            'asia_mid_retest': retest_mid,
            'pdh': round(pdh, 5) if pdh else None,
            'pdl': round(pdl, 5) if pdl else None,
            'sweep_pdh': sweep_pdh,
            'sweep_pdl': sweep_pdl,
            'pdh_time': pdh_time.strftime('%H:%M') if pdh_time else None,
            'pdl_time': pdl_time.strftime('%H:%M') if pdl_time else None,
            **ny_analysis
        }
    
    def analyze_period(self, df):
        """Аналіз всього періоду"""
        print("Починаю аналіз...")
        
        # Отримуємо унікальні дати
        df['Date'] = df['Datetime'].dt.date
        unique_dates = sorted(df['Date'].unique())
        
        results = []
        
        for i, date in enumerate(unique_dates):
            print(f"Обробка {date} ({i+1}/{len(unique_dates)})")
            
            day_result = self.analyze_day(df, pd.Timestamp(date))
            if day_result:
                results.append(day_result)
        
        return pd.DataFrame(results)
    
    def analyze_data(self, df):
        """Алиас для analyze_period (для совместимости с BatchLiquidityAnalyzer)"""
        return self.analyze_period(df)
    
    def save_results(self, results_df, output_file):
        """Збереження результатів у Excel"""
        print(f"Зберігаю результати у файл: {output_file}")
        
        # Створюємо Excel writer
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Основні результати
            results_df.to_excel(writer, sheet_name='Analysis_Results', index=False)
            
            # Статистика
            stats_df = self.calculate_statistics(results_df)
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)
        
        print(f"Результати збережено у файл: {output_file}")
    
    def calculate_statistics(self, results_df):
        """Розрахунок статистики"""
        stats = []
        
        # Загальна статистика
        total_days = len(results_df)
        
        # Frankfurt sweeps
        frankfurt_high_count = (results_df['frankfurt_sweep_high'] == 'Yes').sum()
        frankfurt_low_count = (results_df['frankfurt_sweep_low'] == 'Yes').sum()
        
        # London sweeps
        london_high_count = (results_df['london_sweep_high'] == 'Yes').sum()
        london_low_count = (results_df['london_sweep_low'] == 'Yes').sum()
        
        # Sweep types
        continue_count = (results_df['sweep_type'] == 'Continue').sum()
        reverse_count = (results_df['sweep_type'] == 'Sweep and Reverse').sum()
        no_sweep_count = (results_df['sweep_type'] == 'No Sweep').sum()
        
        # Rebalance
        rebalance_yes = (results_df['rebalance'] == 'Yes').sum()
        
        # Directions
        long_count = (results_df['london_direction'] == 'Long').sum()
        short_count = (results_df['london_direction'] == 'Short').sum()
        
        stats.extend([
            {'Metric': 'Загальна кількість днів', 'Value': total_days, 'Percentage': 100.0},
            {'Metric': 'Frankfurt Sweep High', 'Value': frankfurt_high_count, 'Percentage': round(frankfurt_high_count/total_days*100, 2)},
            {'Metric': 'Frankfurt Sweep Low', 'Value': frankfurt_low_count, 'Percentage': round(frankfurt_low_count/total_days*100, 2)},
            {'Metric': 'London Sweep High', 'Value': london_high_count, 'Percentage': round(london_high_count/total_days*100, 2)},
            {'Metric': 'London Sweep Low', 'Value': london_low_count, 'Percentage': round(london_low_count/total_days*100, 2)},
            {'Metric': 'Continue', 'Value': continue_count, 'Percentage': round(continue_count/total_days*100, 2)},
            {'Metric': 'Sweep and Reverse', 'Value': reverse_count, 'Percentage': round(reverse_count/total_days*100, 2)},
            {'Metric': 'No Sweep', 'Value': no_sweep_count, 'Percentage': round(no_sweep_count/total_days*100, 2)},
            {'Metric': 'Rebalance Yes', 'Value': rebalance_yes, 'Percentage': round(rebalance_yes/total_days*100, 2)},
            {'Metric': 'London Long', 'Value': long_count, 'Percentage': round(long_count/total_days*100, 2)},
            {'Metric': 'London Short', 'Value': short_count, 'Percentage': round(short_count/total_days*100, 2)},
        ])
        
        return pd.DataFrame(stats)


def main():
    """Головна функція"""
    print("🚀 Аналіз ліквідності EUR/USD по торгових сесіях")
    print("=" * 50)
    
    # Ініціалізація аналізатора
    analyzer = LiquidityAnalyzer()
    
    # Завантаження даних - проверяем сначала в папке files
    input_file = None
    if os.path.exists("files/DAT_MT_EURUSD_M1_202505.csv"):
        input_file = "files/DAT_MT_EURUSD_M1_202505.csv"
    elif os.path.exists("DAT_MT_EURUSD_M1_202505.csv"):
        input_file = "DAT_MT_EURUSD_M1_202505.csv"
    else:
        print("❌ Файл данных не найден!")
        print("💡 Используйте batch_analyzer.py для массовой обработки файлов в папке 'files'")
        return
    
    df = analyzer.load_data(input_file)
    
    if df is None:
        print("❌ Не удалось загрузить данные")
        return
    
    # Аналіз
    results = analyzer.analyze_period(df)
    
    # Збереження результатів
    output_file = "liquidity_analysis_results.xlsx"
    analyzer.save_results(results, output_file)
    
    # Виведення короткої статистики
    print("\n📊 Коротка статистика:")
    print(f"Оброблено днів: {len(results)}")
    print(f"Frankfurt Sweep High: {(results['frankfurt_sweep_high'] == 'Yes').sum()}")
    print(f"Frankfurt Sweep Low: {(results['frankfurt_sweep_low'] == 'Yes').sum()}")
    print(f"London Sweep High: {(results['london_sweep_high'] == 'Yes').sum()}")
    print(f"London Sweep Low: {(results['london_sweep_low'] == 'Yes').sum()}")
    print(f"Continue: {(results['sweep_type'] == 'Continue').sum()}")
    print(f"Sweep and Reverse: {(results['sweep_type'] == 'Sweep and Reverse').sum()}")
    print(f"No Sweep: {(results['sweep_type'] == 'No Sweep').sum()}")
    
    print(f"\n✅ Аналіз завершено! Результати збережено у файл: {output_file}")
    print("💡 Для массовой обработки используйте: python batch_analyzer.py")


if __name__ == "__main__":
    main()
