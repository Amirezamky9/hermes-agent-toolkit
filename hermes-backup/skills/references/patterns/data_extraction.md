# Pattern: Data Extraction

## تشخیص سریع — چه بپرسی تا بفهمی Data Extraction هست؟
- [ ] کاربر گفت "فایل / اکسل / PDF / CSV بخون"؟
- [ ] "استخراج کن / parse کن / از توی فایل اطلاعات بکش بیرون"؟

## سوالات هدفمند (قبل از جستجو)
| بپرس | تا بفهمی |
|------|---------|
| چه نوع فایلی؟ (PDF / CSV / Excel / HTML / متن) | Extract From File vs AI |
| فایل چجوری میرسه؟ (آپلود / ایمیل attachment / API) | Trigger نوع |
| چیزایی ک میخوای استخراج کنی ساختار ثابت داره؟ | نیاز به AI یا Code |
| حجم فایل چقدره؟ | Batch نیاز داره؟ |
| خروجی کجا بره؟ | Storage |

## کلمات کلیدی برای جستجوی مشابه
`n8n pdf extraction`, `parse csv`, `excel automation`, `invoice extractor`

## Credentialهایی که باید چک کنی
OpenAI (اگه AI Extraction) / Google Sheets (ذخیره)
