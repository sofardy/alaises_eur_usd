#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утиліти для валідації та обробки даних
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
from config import Config

class DataValidator:
    """Клас для валідації вхідних даних"""
    
    def __init__(self):
        self.config = Config()
    
    def validate_csv_file(self, file_path):
        """Валідація CSV файлу"""
        try:
            # Перевіряємо чи існує файл
            df = pd.read_csv(file_path, nrows=5)  # Читаємо тільки перші 5 рядків
            
            print(f"✅ Файл знайдено: {file_path}")
            print(f"📊 Колонки: {list(df.columns)}")
            
            # Перевіряємо кількість колонок
            if len(df.columns) < 6:
                print("⚠️  Увага: Менше 6 колонок. Очікується: Date, Time, Open, High, Low, Close, Volume")
                return False
            
            # Перевіряємо формат дати та часу в перших рядках
            if len(df) > 0:
                first_row = df.iloc[0]
                print(f"📅 Приклад дати: {first_row.iloc[0]}")
                print(f"⏰ Приклад часу: {first_row.iloc[1]}")
                print(f"💰 Приклад цін: O={first_row.iloc[2]}, H={first_row.iloc[3]}, L={first_row.iloc[4]}, C={first_row.iloc[5]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Помилка при читанні файлу: {e}")
            return False
    
    def validate_data_quality(self, df):
        """Валідація якості даних"""
        issues = []
        
        # Перевіряємо на пропущені значення
        missing_values = df.isnull().sum()
        if missing_values.sum() > 0:
            issues.append(f"Пропущені значення: {missing_values.to_dict()}")
        
        # Перевіряємо логічність цін (High >= Low, Open/Close між High/Low)
        invalid_ohlc = ((df['High'] < df['Low']) | 
                       (df['Open'] > df['High']) | (df['Open'] < df['Low']) |
                       (df['Close'] > df['High']) | (df['Close'] < df['Low'])).sum()
        
        if invalid_ohlc > 0:
            issues.append(f"Некоректні OHLC дані: {invalid_ohlc} рядків")
        
        # Перевіряємо на дублікати часу
        duplicates = df['Datetime'].duplicated().sum()
        if duplicates > 0:
            issues.append(f"Дублікати часу: {duplicates} рядків")
        
        # Перевіряємо на розриви в часі (більше 1 хвилини)
        time_diff = df['Datetime'].diff()
        large_gaps = (time_diff > pd.Timedelta(minutes=5)).sum()
        if large_gaps > 0:
            issues.append(f"Великі розриви в даних (>5 хв): {large_gaps}")
        
        if issues:
            print("⚠️  Знайдені проблеми з якістю даних:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ Якість даних хороша")
            return True
    
    def get_data_statistics(self, df):
        """Отримати статистику даних"""
        stats = {
            'total_records': len(df),
            'date_range': f"{df['Datetime'].min()} - {df['Datetime'].max()}",
            'trading_days': df['Datetime'].dt.date.nunique(),
            'avg_spread': ((df['High'] - df['Low']) / self.config.PIP_SIZE).mean(),
            'price_range': f"{df[['Open', 'High', 'Low', 'Close']].min().min():.5f} - {df[['Open', 'High', 'Low', 'Close']].max().max():.5f}"
        }
        
        print("📊 Статистика даних:")
        print(f"   Всього записів: {stats['total_records']:,}")
        print(f"   Період: {stats['date_range']}")
        print(f"   Торгових днів: {stats['trading_days']}")
        print(f"   Середній спред: {stats['avg_spread']:.1f} пунктів")
        print(f"   Діапазон цін: {stats['price_range']}")
        
        return stats

def validate_input_file(file_path):
    """Головна функція валідації"""
    print("🔍 ВАЛІДАЦІЯ ВХІДНИХ ДАНИХ")
    print("=" * 30)
    
    validator = DataValidator()
    
    # Валідація файлу
    if not validator.validate_csv_file(file_path):
        return False
    
    # Завантаження та валідація даних
    try:
        df = pd.read_csv(file_path, header=None, names=Config.INPUT_COLUMNS)
        df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format=Config.DATETIME_FORMAT)
        df['Datetime'] = df['Datetime'] + pd.Timedelta(hours=Config.UTC_OFFSET)
        df = df[Config.REQUIRED_COLUMNS].copy()
        
        # Валідація якості
        quality_ok = validator.validate_data_quality(df)
        
        # Статистика
        validator.get_data_statistics(df)
        
        return quality_ok
        
    except Exception as e:
        print(f"❌ Помилка при обробці даних: {e}")
        return False

if __name__ == "__main__":
    validate_input_file(Config.DEFAULT_INPUT_FILE)
