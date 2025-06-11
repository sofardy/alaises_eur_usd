#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфігурація аналізатора ліквідності EUR/USD
"""

class Config:
    """Конфігурація параметрів аналізу"""
    
    # Торгові сесії (UTC+3)
    SESSIONS = {
        'asia': {'start': 2, 'end': 10},      # 02:00 - 10:00
        'frankfurt': {'start': 9, 'end': 10}, # 09:00 - 10:00
        'london': {'start': 10, 'end': 15},   # 10:00 - 15:00
        'newyork': {'start': 15, 'end': 19}   # 15:00 - 19:00
    }
    
    # Константи для розрахунків
    PIP_SIZE = 0.00010         # Розмір пункту для EUR/USD
    TOLERANCE = 0.00030        # Допуск для Asia Mid (±3 пункти)
    PRECISION = 5              # Точність для цін
    
    # Назви файлів
    DEFAULT_INPUT_FILE = "DAT_MT_EURUSD_M1_202505.csv"
    DEFAULT_OUTPUT_FILE = "liquidity_analysis_results.xlsx"
    
    # Формати даних  
    DATE_FORMAT = '%Y.%m.%d'
    TIME_FORMAT = '%H:%M'
    DATETIME_FORMAT = '%Y.%m.%d %H:%M'
    
    # Колонки вхідних даних
    INPUT_COLUMNS = ['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    REQUIRED_COLUMNS = ['Datetime', 'Open', 'High', 'Low', 'Close']
    
    # UTC offset
    UTC_OFFSET = 3  # UTC+3
