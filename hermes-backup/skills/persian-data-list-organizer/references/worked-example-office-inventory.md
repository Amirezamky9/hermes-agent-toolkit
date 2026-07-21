# Worked Example — Office Inventory List

Raw user input (Telegram):
```
16 تا تابلو 
4 عدد مانیتور 
دو عدد کیس 
 یک عدد پرینتر 
یک عدد یخچال 
یک عدد مایکروفر
5عدد خودکار ابی 
3عدد قرمز 
1عدد فلش 
2عدد پاکن 
4عدد مداد
4عدد باتری 
4عدد باتری نیم قلم 
2بسته منگنه
2عدد غلط گیر
2عدد تخته پاک کن 
1عدد خطکش
1عدد قیچی
1عدد کاتر
1سرویس غذاخوری
2دست قاشق و چنگال 
2دست لیوان نوشیدنی شیش عددی
2دست لیوان چایی خوری شیش عددی
1کارتون کارت تبلیغ
2بسته دستمال 
1بسته کیسه زباله
1بسته چایی کیسه ای
1بسته ورقه اچار نصفه
3بستع پاکت نامه
1عدد سررسید
2بسته پاکت نامه بزرگ 
11بسته کیف مدارک
1عدد مودم عمانتل
1عدد تلفن
4عدد سبد تحریر
2عدد تابلو سفال لوگو مسترتیوب
4 عدد سه راهی
3عدد هدفون
3عدد کیبورد و موس تسکو
1عدد مودم cpe
2 عدد ساعت
16عدد تابلو 
1عدد چایی ساز 
1عدد منگنه
3عدد وبکم
1عدد تی
1عدد جارو خاک انداز 
4عدد پرچم کوچک 
3عدد پرچم بزرگ
```

## Corrections the user gave after first draft:
1. "مارک دون بهم ریخته" → Stop using Markdown tables, switch to Excel file
2. "تابلو تکراری بود" → Merge the two "16 تابلو" entries (it was one item listed twice)
3. "ساعت دو عدد بود" → Confirm/explicitly note the 2 watches
4. Add: سویچ شبکه D-Link (1), موس پد (3), سطل آشغال (2)
5. "قندان" not in list → Add 2 قندان to Kitchen category

## Final Excel Output Structure

| Column | Content | Example |
|--------|---------|---------|
| ردیف | Auto-numbered | 1, 2, 3... |
| دسته‌بندی | Category with emoji | 🖥️ الکترونیک و IT |
| کالا | Item name | مانیتور |
| تعداد | Quantity | 4 |

### Categories used:
- 🖥️ الکترونیک و IT (13 items)
- 📋 تابلو و پرچم (4 items)
- ✏️ لوازم تحریر (13 items)
- 🔋 باتری (2 items)
- 🍳 آشپزخانه و پذیرایی (10 items)
- 📦 بسته‌بندی و اداری (6 items)
- 🧹 نظافت (5 items)
- 🔌 متفرقه (1 item)

**Total: 52 items** after all corrections.
