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
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# Импорт библиотек для работы с часовыми поясами
try:
    import pytz
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False
    try:
        import zoneinfo
        HAS_ZONEINFO = True
    except ImportError:
        HAS_ZONEINFO = False


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
            if HAS_PYTZ:
                kyiv_tz = pytz.timezone('Europe/Kyiv')
                df['Datetime'] = df['Datetime'].dt.tz_convert(kyiv_tz)
                print("✅ Конвертация времени: UTC → Europe/Kyiv (pytz)")
            elif HAS_ZONEINFO:
                from zoneinfo import ZoneInfo
                kyiv_tz = ZoneInfo('Europe/Kyiv')
                df['Datetime'] = df['Datetime'].dt.tz_convert(kyiv_tz)
                print("✅ Конвертация времени: UTC → Europe/Kyiv (zoneinfo)")
            else:
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


def main():
    """Основна функція для запуску аналізу"""
    print("🚀 Тест конвертации часовых поясов UTC → Europe/Kyiv")
    print("=" * 60)
    
    # Створення аналізатора
    analyzer = LiquidityAnalyzer()
    
    # Тест загрузки данных
    df = analyzer.load_data('files/3_.csv')
    
    if df is not None:
        print(f"\n📊 Данные загружены успешно!")
        print(f"🌍 Часовой пояс: {df['Datetime'].dt.tz}")
        print(f"📅 Первая запись: {df['Datetime'].iloc[0]}")
        print(f"📅 Последняя запись: {df['Datetime'].iloc[-1]}")
        
        # Проверяем разные месяцы для DST
        sample_dates = df['Datetime'].dt.date.unique()[:5]
        print(f"\n🔍 Образцы дат после конвертации:")
        for date in sample_dates:
            date_data = df[df['Datetime'].dt.date == date]
            if not date_data.empty:
                first_time = date_data['Datetime'].iloc[0]
                print(f"   {date}: {first_time} (UTC offset: {first_time.utcoffset()})")
    else:
        print("❌ Ошибка загрузки данных")


if __name__ == "__main__":
    main()
