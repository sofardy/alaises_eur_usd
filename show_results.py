#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрація результатів аналізу ліквідності EUR/USD
"""

import pandas as pd
import numpy as np
from datetime import datetime

def show_results():
    """Показати основні результати аналізу"""
    
    print("🎯 ДЕМОНСТРАЦІЯ РЕЗУЛЬТАТІВ АНАЛІЗУ ЛІКВІДНОСТІ EUR/USD")
    print("=" * 60)
    
    try:
        # Завантажуємо результати
        df = pd.read_excel('liquidity_analysis_results.xlsx', sheet_name='Analysis_Results')
        stats_df = pd.read_excel('liquidity_analysis_results.xlsx', sheet_name='Statistics')
        
        print(f"📅 Період аналізу: {df['date'].min()} - {df['date'].max()}")
        print(f"📊 Оброблено торгових днів: {len(df)}")
        print()
        
        # Основна статистика
        print("📈 ОСНОВНА СТАТИСТИКА:")
        print("-" * 30)
        for _, row in stats_df.iterrows():
            print(f"{row['Metric']:<25}: {row['Value']:>3} ({row['Percentage']:>6.1f}%)")
        print()
        
        # Найкращі та найгірші дні
        print("🏆 ТОП-5 ДНІВ ЗА РОЗШИРЕННЯМ:")
        print("-" * 40)
        top_days = df.nlargest(5, 'extension_pips')[['date', 'day_of_week', 'sweep_type', 'extension_pips', 'extension_percent']]
        for _, row in top_days.iterrows():
            print(f"{row['date']} ({row['day_of_week']:<9}): {row['extension_pips']:>6.1f} пунктів ({row['extension_percent']:>6.1f}%) - {row['sweep_type']}")
        print()
        
        # Аналіз по днях тижня
        print("📅 АНАЛІЗ ПО ДНЯХ ТИЖНЯ:")
        print("-" * 30)
        day_analysis = df.groupby('day_of_week').agg({
            'extension_pips': 'mean',
            'extension_percent': 'mean',
            'sweep_type': lambda x: (x == 'Continue').sum(),
            'london_direction': lambda x: (x == 'Long').sum()
        }).round(2)
        
        for day, row in day_analysis.iterrows():
            print(f"{day:<10}: Розширення {row['extension_pips']:>6.1f} пунктів, Continue: {int(row['sweep_type'])}, Long: {int(row['london_direction'])}")
        print()
        
        # Sweep Type аналіз
        print("🎯 АНАЛІЗ ТИПІВ SWEEP:")
        print("-" * 25)
        sweep_analysis = df.groupby('sweep_type').agg({
            'extension_pips': ['mean', 'std'],
            'rebalance': lambda x: (x == 'Yes').sum()
        }).round(2)
        
        for sweep_type in sweep_analysis.index:
            mean_ext = sweep_analysis.loc[sweep_type, ('extension_pips', 'mean')]
            std_ext = sweep_analysis.loc[sweep_type, ('extension_pips', 'std')]
            rebalance_count = int(sweep_analysis.loc[sweep_type, ('rebalance', '<lambda>')])
            print(f"{sweep_type:<17}: {mean_ext:>6.1f}±{std_ext:>5.1f} пунктів, Rebalance: {rebalance_count}")
        print()
        
        # NY vs London аналіз
        print("🌍 LONDON vs NEW YORK:")
        print("-" * 25)
        ny_support = (df['ny_status'] == 'Support').sum()
        ny_reverse = (df['ny_status'] == 'Reverse').sum()
        print(f"NY Support London: {ny_support} ({ny_support/len(df)*100:.1f}%)")
        print(f"NY Reverse London: {ny_reverse} ({ny_reverse/len(df)*100:.1f}%)")
        print()
        
        # Додаткові метрики
        print("📊 ДОДАТКОВІ МЕТРИКИ:")
        print("-" * 20)
        print(f"Середнє Asia Range: {(df['asia_high'] - df['asia_low']).mean()/0.00010:.1f} пунктів")
        print(f"Rebalance Rate: {(df['rebalance'] == 'Yes').sum()}/{len(df)} ({(df['rebalance'] == 'Yes').sum()/len(df)*100:.1f}%)")
        print(f"Середній Reverse: {df['reverse_pips'].mean():.1f} пунктів")
        print()
        
        # Приклад конкретного дня
        print("🔍 ПРИКЛАД ДЕТАЛЬНОГО АНАЛІЗУ (найкращий день):")
        print("-" * 50)
        best_day = df.loc[df['extension_pips'].idxmax()]
        print(f"Дата: {best_day['date']} ({best_day['day_of_week']})")
        print(f"Asia High: {best_day['asia_high']:.5f}")
        print(f"Asia Low: {best_day['asia_low']:.5f}")
        print(f"Asia Mid: {best_day['asia_mid']:.5f}")
        print(f"London Sweep: High={best_day['london_sweep_high']}, Low={best_day['london_sweep_low']}")
        print(f"Sweep Type: {best_day['sweep_type']}")
        print(f"London Direction: {best_day['london_direction']}")
        print(f"Extension: {best_day['extension_pips']:.1f} пунктів ({best_day['extension_percent']:.1f}%)")
        print(f"Rebalance: {best_day['rebalance']}")
        print(f"NY Direction: {best_day['ny_direction']}")
        print(f"NY Status: {best_day['ny_status']}")
        
    except FileNotFoundError:
        print("❌ Файл з результатами не знайдено!")
        print("Спочатку запустіть аналіз: python liquidity_analyzer.py")

if __name__ == "__main__":
    show_results()
