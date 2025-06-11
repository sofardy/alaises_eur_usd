@echo off
chcp 65001 >nul
title Анализатор ликвидности EUR/USD

echo 🚀 Запуск анализатора ликвидности EUR/USD...
echo.

REM Переходим в директорию скрипта
cd /d "%~dp0"

REM Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo Установите Python с https://python.org
    pause
    exit /b 1
)

REM Создаем виртуальное окружение если нужно
if not exist "venv" (
    echo 📦 Первый запуск - создаем виртуальное окружение...
    python -m venv venv
)

REM Активируем виртуальное окружение
call venv\Scripts\activate.bat

REM Устанавливаем зависимости если нужно
python -c "import pandas, openpyxl" >nul 2>&1
if errorlevel 1 (
    echo 📚 Устанавливаем необходимые библиотеки...
    pip install --upgrade pip
    pip install pandas openpyxl
)

REM Создаем папки если не существуют
if not exist "files" mkdir files
if not exist "results" mkdir results

REM Запускаем GUI приложение
echo ✅ Запускаем графический интерфейс...
python gui_app.py

echo.
echo 👋 Программа завершена
pause
