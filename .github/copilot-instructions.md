# 📄 **Технічне Завдання: Аналіз ліквідності EUR/USD по торгових сесіях**

---

## 1️⃣ Вхідні дані

- Формат файлів: CSV або XLSX.
- Формат даних (наприклад з HistData):
  - `Date` — у форматі `YYYY.MM.DD`.
  - `Time` — у форматі `HH:MM`.
  - `Open`, `High`, `Low`, `Close` — BID-ціни.
  - `Volume` — ігнорується.
- Таймфрейм: **M1** (1-хвилинні свічки).
- Часова зона у файлі: **UTC+0 (GMT)**.

---

## 2️⃣ Попередня обробка даних

### 2.1 Об’єднання дати і часу:

- Створити колонку `Datetime`:

```python
df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%Y.%m.%d %H:%M')

```

### 2.2 Переведення у UTC+3:

```python
df['Datetime'] = df['Datetime'] + pd.Timedelta(hours=3)

```

### 2.3 Залишити колонки:

- `Datetime`, `Open`, `High`, `Low`, `Close`.

---

## 3️⃣ Розмітка сесій (літній час, UTC+3)

| Сесія     | Час           |
| --------- | ------------- |
| Азія      | 02:00 – 10:00 |
| Франкфурт | 09:00 – 10:00 |
| Лондон    | 10:00 – 15:00 |

---

## 4️⃣ Алгоритм розрахунку

### 4.1 Розрахунок Asia High / Low / Mid

- Asia High: максимум з 02:00 до 10:00.
- Asia Low: мінімум з 02:00 до 10:00.
- Asia Mid = (Asia High + Asia Low) / 2.

### 4.2 Розрахунок PDH / PDL

- PDH — хай попереднього дня (00:00 – 23:59 UTC+3).
- PDL — лоу попереднього дня.

---

## 5️⃣ Визначення Sweep

### 5.1 Франкфурт Sweep:

- Чи було пробито Asia High/Low у Франкфурті (09:00 – 10:00).
- Sweep вважається, якщо:
  - High ≥ Asia High + 0.00010
  - або Low ≤ Asia Low - 0.00010

### Часове вікно Франкфурта:

- 09:00 – 10:00 UTC+3

### Розрахунок рівнів для перевірки:

- Asia High / Asia Low завжди розраховуються за повний період Азії: `02:00 – 10:00 UTC+3`.

### Умова фіксації sweep Франкфурта:

- У період 09:00 – 10:00 перевіряється, чи було пробито Asia High або Asia Low:

```python
if high_in_frankfurt >= (asia_high + 0.00010):
    sweep_frankfurt_high = True
if low_in_frankfurt <= (asia_low - 0.00010):
    sweep_frankfurt_low = True

```

- Sweep фіксується навіть якщо пробиття сталося до закриття азійської сесії (оскільки Франкфурт частково накладається на Азію).

---

✅ Таким чином:

- Межі сесій ми не зміщуємо.
- Sweep Франкфурта завжди перевіряється у своєму вузькому вікні 09:00–10:00.

---

Все. Це доповнення повністю закриває цю точку.

🚀 Якщо хочеш — можемо тепер перейти до фінальної чистової версії коду (стартовий каркас Python). Хочеш? — напиши: **"Давай кодовий каркас"** — я зроблю тобі готову основу для розробника.

### 5.2 Лондон Sweep:

- Чи було пробито Asia High/Low у Лондоні (10:00 – 15:00).
- Умови аналогічні:
  - High ≥ Asia High + 0.00010
  - або Low ≤ Asia Low - 0.00010

---

## 6️⃣ Визначення основного напрямку руху (Long / Short)

- Розрахунок ведеться з моменту sweep (час пробиття хай/лоу Азії) до 15:00.
- Обчислюється амплітуда:

```python
Up_move = High після sweep - Sweep Price
Down_move = Sweep Price - Low після sweep

```

- Якщо `Up_move > Down_move` → Long.
- Якщо `Down_move > Up_move` → Short.

---

## 7️⃣ Визначення Sweep Type

- На основі sweep та основного руху:

| Sweep     | Основний рух | Sweep Type        |
| --------- | ------------ | ----------------- |
| Asia High | Long         | Continue          |
| Asia High | Short        | Sweep and Reverse |
| Asia Low  | Short        | Continue          |
| Asia Low  | Long         | Sweep and Reverse |

- Якщо у Лондоні не було sweep → `No Sweep` (окремо фіксуємо).

---

## 8️⃣ Визначення Rebalance

- Перевірка виконується тільки після того, як визначено Sweep and Reverse.
- Умова:

1️⃣ Після sweep ціна розвертається у протилежний бік. 2️⃣ Ціна дотикнулась до 0.5 Asia (Asia Mid ±3 пункти). 3️⃣ Після дотику — продовжила рух у бік sweep (тобто пішла проти основного руху).

- Якщо умова виконана → `Rebalance = Yes`.
- Якщо ціна не дотикнулась до 0.5 або після дотику продовжила основний рух → `Rebalance = No`.

---

## 9️⃣ Визначення Sweep PDH/PDL

- Після Лондон sweep Asia High/Low додатково перевіряємо:

| Умова                | Дія             |
| -------------------- | --------------- |
| High ≥ PDH + 0.00010 | Sweep PDH = Yes |
| Low ≤ PDL - 0.00010  | Sweep PDL = Yes |

---

## 10️⃣ Розрахунок розширень

- Розраховується розширення ціни після sweep:
  - в пунктах (0.00010 = 1 пункт),
  - у відсотках від Asia Range,
  - час до максимуму/мінімуму в рамках Лондону.

---

## 11️⃣ Підсумкові вихідні колонки:

- Дата
- День тижня
- Asia High / Low / Mid
- Frankfurt Sweep (H/L) + час
- London Sweep Asia (H/L) + час
- London Sweep Frankfurt (H/L) + час
- Sweep Type (Continue / Sweep and Reverse / No Sweep)
- Основний рух (Long / Short)
- Rebalance (Yes / No)
- Розширення в пунктах та у %
- Час до максимуму/мінімуму після sweep
- Reverse після sweep в пунктах та %
- Retest Asia Sweep Level (Yes / No)
- Asia Mid Retest (Yes / No)
- PDH / PDL
- Sweep PDH / Sweep PDL + час

---

## 12️⃣ Технічні вимоги:

- Мова: Python 3.x
- Бібліотеки: pandas, numpy, datetime, openpyxl.
- Чітко розділені функції під кожний етап.

---

# 🔑 Примітка:

- Всі часові розрахунки проводяться у UTC+3.
- Sweep фіксуємо тільки в рамках Лондону (10:00–15:00 UTC+3).
- Мінімальне пробиття — 1 пункт (0.00010).
- Asia Mid перевіряється з допуском ±3 пункти (0.00030).

---

---

---

## 🔢 10.1 Розрахунок розширення після sweep

### 1️⃣ Розрахунок діапазону Азії:

```python
asia_range = asia_high - asia_low

```

---

### 2️⃣ Розширення в пунктах:

### Якщо sweep був по Asia High:

```python
rozshyrennia_punktiv = (max_london_high - sweep_price) / 0.00010

```

### Якщо sweep був по Asia Low:

```python
rozshyrennia_punktiv = (sweep_price - min_london_low) / 0.00010

```

- (Один пункт = 0.00010)

---

### 3️⃣ Розширення у відсотках від Asia Range:

### Загальна формула:

```python
rozshyrennia_v_procentakh = (rozshyrennia / asia_range) * 100

```

Де:

```python
rozshyrennia = abs(max_london_high - sweep_price) або abs(sweep_price - min_london_low)

```

(залежно від напрямку sweep).

---

## 🔧 Додатково:

- Якщо asia_range = 0 → уникати ділення на нуль (захист від помилок).
- Працювати з точністю до 5 знаків після коми.

---

# 📊 **Результуюча таблиця по Лондону (структура рядка даних на 1 день)**

| Поле                          | Опис                                                      |
| ----------------------------- | --------------------------------------------------------- |
| Дата                          | Дата дня                                                  |
| День тижня                    | Наприклад: Monday, Tuesday                                |
| Asia High                     | Максимум Азії (02:00 – 10:00)                             |
| Asia Low                      | Мінімум Азії (02:00 – 10:00)                              |
| Asia Mid                      | (Asia High + Asia Low) / 2                                |
| Frankfurt Sweep High          | Yes/No                                                    |
| Frankfurt Sweep Low           | Yes/No                                                    |
| London Sweep High             | Yes/No                                                    |
| London Sweep Low              | Yes/No                                                    |
| Sweep Type                    | Continue / Sweep and Reverse / No Sweep                   |
| Основний рух Лондону          | Long / Short                                              |
| Rebalance                     | Yes / No                                                  |
| Розширення Лондону (пунктів)  | В пунктах після sweep                                     |
| Розширення Лондону (%)        | Відсоток від Asia Range                                   |
| Час до максимуму (Лондону)    | Час коли був сформований максимум Лондону після sweep     |
| Час до мінімуму (Лондону)     | Час коли був сформований мінімум Лондону після sweep      |
| Reverse після sweep (пунктів) | Скільки пройшла ціна у протилежному напрямку після sweep  |
| Reverse після sweep (%)       | Те саме у відсотках від Asia Range                        |
| Retest Asia Sweep Level       | Yes/No (дотик ±3 пунктів після sweep до рівня sweep Азії) |
| Asia Mid Retest               | Yes/No (дотик ±3 пунктів до 0.5 Asia після sweep)         |
| PDH                           | Хай попереднього дня                                      |
| PDL                           | Лоу попереднього дня                                      |
| Sweep PDH                     | Yes/No                                                    |
| Sweep PDL                     | Yes/No                                                    |

---

---

✅ **Після цього блоку йде продовження цієї таблиці по Нью-Йорку**, яку ми нижче зробили

---

# 🔥 Тобто твоя фінальна таблиця в ідеалі буде мати дві частини:

1️⃣ Основний блок по Лондону (як вище). 2️⃣ Блок по Нью-Йорку (який ми тільки що створили).

---

# 📂 Якщо хочеш — я можу тобі зробити одразу:

✅ **Порожній Excel-шаблон під фінальну таблицю**, де будуть обидва блоки:

- Лондонський.
- Нью-Йоркський.

І ти вже зможеш бачити остаточну структуру майбутнього датасету.

---

👉 Якщо потрібно — просто скажи:

**"Давай фінальний Excel-шаблон"**

🚀 І я зроблю тобі чистий макет.

# **Нью-Йорк Блок**

---

## 1️⃣ Часова зона Нью-Йорк сесії:

- Нью-Йорк сесія: **15:00 – 19:00 UTC+3**

---

## 2️⃣ Вхідні рівні (які вже є з Лондонського блоку):

- Asia High, Asia Low, Asia Mid — розраховані по 02:00–10:00.
- Основний рух Лондону (London Direction) — Long або Short.

---

## 3️⃣ Логіка розрахунку для Нью-Йорка:

---

### 3.1 Визначення основного напрямку Нью-Йорка (NY Direction)

- Обираємо першу свічку Нью-Йорку (відкрита о 15:00 UTC+3) — беремо ціну відкриття → `NY Open`.
- Розрахунок:

```python
Up_move = NY High - NY Open
Down_move = NY Open - NY Low

```

- Якщо `Up_move > Down_move` → **NY Direction = Long**
- Якщо `Down_move > Up_move` → **NY Direction = Short**
- Визначається в рамках 15:00 – 19:00 UTC+3.

---

### 3.2 Визначення статусу:

- Порівнюємо напрямок Нью-Йорку з напрямком Лондону.

| Лондон | Нью-Йорк | NY Status |
| ------ | -------- | --------- |
| Long   | Long     | Support   |
| Long   | Short    | Reverse   |
| Short  | Short    | Support   |
| Short  | Long     | Reverse   |

---

### 3.3 Розширення Нью-Йорку в обидві сторони

### NY Up Extension (пунктів):

```python
ny_up_extension_pips = (NY High - NY Open) / 0.00010

```

### NY Down Extension (пунктів):

```python
ny_down_extension_pips = (NY Open - NY Low) / 0.00010

```

---

### 3.4 Розширення Нью-Йорку у відсотках від Asia Range

### Розрахунок Asia Range:

```python
asia_range = Asia High - Asia Low

```

### NY Up Extension (%):

```python
ny_up_extension_percent = (NY High - NY Open) / asia_range * 100

```

### NY Down Extension (%):

```python
ny_down_extension_percent = (NY Open - NY Low) / asia_range * 100

```

- Якщо Asia Range = 0 → уникати ділення на нуль.

---

### 3.5 Час до максимуму і мінімуму в NY:

- Визначити час коли був сформований:
  - `NY Max High Time` — коли NY High був досягнутий.
  - `NY Min Low Time` — коли NY Low був досягнутий.
- У рамках 15:00 – 19:00 UTC+3.

---

## 4️⃣ Вихідні колонки для Нью-Йорк блоку:

\| NY Direction | NY Status | NY Up Extension (пунктів) | NY Up Extension (%) | NY Down Extension (пунктів) | NY Down Extension (%) | NY Max High Time | NY Min Low Time |

---

✅ Після додавання цього блоку у нас повністю закривається логіка по всіх основних сесіях.

---

# 🔬 Особлива примітка:

- Логіка розрахунку NY абсолютно ідентична логіці розрахунку Лондону — просто інші часові рамки.

---
