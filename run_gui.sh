#!/bin/bash

# Простой запуск GUI приложения для анализа ликвидности
# Для "простых смертных" - без терминалов и сложностей

echo "🚀 Запуск анализатора ликвидности EUR/USD..."

# Переходим в директорию скрипта
cd "$(dirname "$0")"

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден!"
    echo "📥 Попробуем установить Python через Homebrew..."
    
    # Проверяем Homebrew
    if ! command -v brew &> /dev/null; then
        echo "📦 Устанавливаем Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Добавляем Homebrew в PATH
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    
    # Устанавливаем Python
    echo "🐍 Устанавливаем Python..."
    brew install python@3.11
fi

# Находим лучший Python с tkinter
PYTHON_CMD=""
TKINTER_AVAILABLE=false

# Проверяем разные варианты Python
for python_path in "/opt/homebrew/bin/python3" "/opt/homebrew/bin/python3.11" "python3" "/usr/bin/python3" "/usr/local/bin/python3"; do
    if command -v "$python_path" &> /dev/null; then
        echo "🔍 Проверяем $python_path..."
        if $python_path -c "import tkinter" 2>/dev/null; then
            PYTHON_CMD="$python_path"
            TKINTER_AVAILABLE=true
            echo "✅ Найден Python с tkinter: $python_path"
            break
        else
            PYTHON_CMD="$python_path"
            echo "⚠️  Python найден, но без tkinter: $python_path"
        fi
    fi
done

# Если Python найден, но нет tkinter, устанавливаем его
if [ ! -z "$PYTHON_CMD" ] && [ "$TKINTER_AVAILABLE" = false ]; then
    echo "📦 Устанавливаем tkinter..."
    
    # Для macOS устанавливаем python-tk через Homebrew
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install python-tk
            # Обновляем PYTHON_CMD на версию с tkinter
            if command -v "/opt/homebrew/bin/python3" &> /dev/null; then
                PYTHON_CMD="/opt/homebrew/bin/python3"
                if $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
                    TKINTER_AVAILABLE=true
                    echo "✅ tkinter успешно установлен!"
                fi
            fi
        fi
    fi
fi

# Если все еще нет Python, прерываем
if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Не удалось найти Python!"
    echo "Установите Python с https://python.org"
    read -p "Нажмите Enter для закрытия..."
    exit 1
fi

# Создаем виртуальное окружение если нужно
if [ ! -d "venv" ]; then
    echo "📦 Первый запуск - создаем виртуальное окружение..."
    $PYTHON_CMD -m venv venv
fi

# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем зависимости если нужно
if ! python -c "import pandas, openpyxl" 2>/dev/null; then
    echo "📚 Устанавливаем необходимые библиотеки..."
    pip install --upgrade pip
    pip install pandas openpyxl
fi

# Создаем папки если не существуют
mkdir -p files results

# Проверяем tkinter и запускаем соответствующий интерфейс
if python -c "import tkinter" 2>/dev/null; then
    echo "✅ Запускаем графический интерфейс..."
    python gui_app.py
else
    echo "⚠️  GUI недоступен (нет tkinter)"
    echo "💡 Хотите установить tkinter для GUI? (y/n)"
    read -p "Ответ: " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔧 Устанавливаем tkinter..."
        
        # Проверяем Homebrew
        if command -v brew &> /dev/null; then
            echo "📦 Установка через Homebrew..."
            brew install python-tk
            
            # Пересоздаем venv с новым Python
            echo "🔄 Обновляем виртуальное окружение..."
            rm -rf venv
            /opt/homebrew/bin/python3 -m venv venv
            source venv/bin/activate
            pip install --upgrade pip
            pip install pandas openpyxl
            
            # Пробуем запустить GUI снова
            if python -c "import tkinter" 2>/dev/null; then
                echo "🎉 tkinter установлен! Запускаем GUI..."
                python gui_app.py
            else
                echo "❌ Не удалось установить tkinter"
                echo "🔄 Запускаем текстовое меню..."
                python menu.py
            fi
        else
            echo "❌ Homebrew не найден, запускаем текстовое меню..."
            python menu.py
        fi
    else
        echo "🔄 Запускаем текстовое меню..."
        python menu.py
    fi
fi
            pip install pandas openpyxl
            
            # Пробуем снова
            if python -c "import tkinter" 2>/dev/null; then
                echo "✅ tkinter установлен! Запускаем GUI..."
                python gui_app.py
            else
                echo "❌ Не удалось установить tkinter"
                echo "🔄 Запускаем текстовое меню..."
                python menu.py
            fi
        else
            echo "❌ Homebrew не найден"
            echo "💡 Установите Python с https://python.org (включает tkinter)"
            echo "🔄 Запускаем текстовое меню..."
            python menu.py
        fi
    else
        echo "🔄 Запускаем текстовое меню..."
        python menu.py
    fi
fi

echo "👋 Программа завершена"
