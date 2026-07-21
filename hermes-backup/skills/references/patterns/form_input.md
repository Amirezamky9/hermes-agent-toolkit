# Pattern: Form Input

## تشخیص سریع — چه بپرسی تا بفهمی Form هست؟
- [ ] کاربر گفت "فرم / ثبت‌نام / نظرسنجی / questionnaire"؟
- [ ] "کاربر یه سری اطلاعات وارد کنه و بره مرحله بعد"؟

## سوالات هدفمند (قبل از جستجو)
| بپرس | تا بفهمی |
|------|---------|
| چند مرحله‌ایه؟ (تک صفحه یا چند مرحله‌ای) | Complexity |
| چه فیلدهایی داره؟ (متن / عدد / آپلود فایل / dropdown) | Form structure |
| شرط داره؟ (اگه فلان گزینه رو انتخاب کرد بره صفحه دیگه) | نیاز به IF/Switch |
| دیتا کجا ذخیره بشه؟ | Storage credential |
| بعد از ثبت‌نام چیکار کنه؟ (ایمیل تأیید / اعلان) | Notification نیاز داره؟ |

## کلمات کلیدی برای جستجوی مشابه
`n8n form`, `form submission`, `registration workflow with storage`

## Credentialهایی که باید چک کنی
Google Sheets / Airtable / Postgres (اگه storage خارجی نیازه)
