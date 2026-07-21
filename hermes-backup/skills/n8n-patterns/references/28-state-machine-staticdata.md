# Cross-Execution State via `$getWorkflowStaticData` — Admin State Machine

> ذخیره state بین اجراهای مختلف ساب‌ورک‌فلو بدون PostgreSQL
> الگو: reject comment flow (admin دلیل رد رو وارد می‌کنه)

---

## مشکل

ساب‌ورک‌فلوها هر بار که فراخوانی میشن یه اجرای مستقل دارن. وقتی ادمین روی "رد" کلیک می‌کنه و بات دلیل می‌خواد، متن دلیل **یه اجرای جدید** میشه — نه ادامه اجرای قبلی.

```
مرحله ۱: admin_rj_42 → Fetch Order → Ask Comment → اجرا تمام
مرحله ۲: "کیفیت پایین" → اجرای جدید → Router نمیشناسه → fallback → خطا!
```

---

## رفع: `$getWorkflowStaticData('global')`

n8n یه store ساده داره که بین همه اجراهای یه ورک‌فلو **persist** می‌کنه — نه PostgreSQL، نه settings table، نه هیچ چیز خارجی.

```javascript
// ذخیره state
const sd = $getWorkflowStaticData('global');
sd.admin_state = { action: 'reject_comment', order_id: 42 };

// خواندن state
const state = sd.admin_state; // { action: 'reject_comment', order_id: 42 }

// پاک کردن state
delete sd.admin_state;
```

**نکته:** این store در هر اجرای ورک‌فلو قابل دسترسیه — چه sub-workflow باشه، چه standalone.

---

## الگوی کامل: Reject Comment Flow

### فلوی ذخیره state

```
🔀 Admin Router [output 10] → 🔍 Fetch Order for Reject
  → 💾 Store Reject State (Code node)
      sd.admin_state = { action: 'reject_comment', order_id: $json.id }
  → 📝 Ask Reject Comment (Telegram)
  → اجرا تمام
```

### فلوی پردازش state

```
⚡ Normalize Input → 🔍 Check Admin State (Code node)
  → اگه route == "admin_reject_comment" → 📝 Process Reject Comment
  → 💾 Update Order (Postgres)
  → ✅ Confirm to Admin + ❌ Notify User
```

### نودهای کلیدی

**🔍 Check Admin State (Code node v2):**
```javascript
const sd = $getWorkflowStaticData('global');
const route = $json.route || '';
if (sd.admin_state && !route.startsWith('admin_')) {
  const state = sd.admin_state;
  if (state.action === 'reject_comment') {
    return [{ json: { route: 'admin_reject_comment', admin_state: state, comment: route } }];
  }
}
return [$input.first()];
```

**📝 Process Reject Comment (Code node v2):**
```javascript
const s = $json.admin_state;
const c = $json.comment;
delete $getWorkflowStaticData('global').admin_state;
return [{ json: { order_id: s.order_id, comment: c, admin_chat_id: ... } }];
```

**🔢 Route Index — اضافه کردن مسیر جدید:**
```javascript
// ... existing routes ...
if (route === 'admin_reject_comment') return [{ json: { routeIndex: 17, route: r, admin_state: $json.admin_state, comment: $json.comment }}];
return [{ json: { routeIndex: 16, route: r }}]; // fallback
```

---

## چرا PostgreSQL نه؟

| روش | مزیت | عیب |
|-----|------|-----|
| `$getWorkflowStaticData` | ✅ بدون وابستگی، ساده، سریع | ❌ فقط برای ورک‌فلو فعلی |
| PostgreSQL settings | ✅ cross-workflow | ❌ نیاز به DB query، credential management |
| DataTable | ✅ query قدرتمند | ❌ اضافه کردن جدول و credential |

**قانون:** برای state machine داخل یه ساب‌ورک‌فلو → همیشه `$getWorkflowStaticData`.

---

## قابلیت گسترش

این الگو برای هر flow چندمرحله‌ای کار می‌کنه:

- ✅ reject comment (admin دلیل رد)
- ✅ confirm approve (admin تأیید نهایی)
- ✅ tracking code (admin کد رهگیری وارد می‌کنه)
- ✅ broadcast confirm (admin پیام جمعی تأیید می‌کنه)

فقط `action` رو عوض کن و نودهای پردازش مربوطه رو اضافه کن.
