# Persian Technical Glossary

Expanded terminology bank for bilingual documentation translation. Covers terms from the crypto-ingestion session and general software engineering.

## Data / Ingestion

| English | Persian |
|---|---|
| Ingestion | دریافت داده |
| Pipeline | پایپلاین |
| Candlestick / Candle | شمع (کندل) |
| OHLCV (Open, High, Low, Close, Volume) | OHLCV (باز، بیشترین، کمترین، بسته، حجم) |
| Open | باز (قیمت باز شدن) |
| High | بیشترین (قیمت) |
| Low | کمترین (قیمت) |
| Close | بسته (قیمت بسته شدن) |
| Volume | حجم معاملات |
| Turnover | ارزش معاملات |
| Backfill | بک‌فیل (داده‌های گذشته) |
| Delta fetch | دریافت دلتا (فقط داده جدید) |
| Upsert | آپسرت (درج یا به‌روزرسانی) |
| Overlap guard | محافظ تداخل |
| Row / Record | ردیف / رکورد |
| Data source | منبع داده |
| Exchange | صرافی |
| Trading pair | جفت‌ارز |
| Timeframe / Interval | بازه زمانی / تایم‌فریم |
| Candle overlap | تداخل شمعی |
| Gap healing | رفع شکاف داده |

## Architecture

| English | Persian |
|---|---|
| Microservice | میکروسرویس |
| Service | سرویس |
| Architecture | معماری |
| Component | مؤلفه / کامپوننت |
| Module | ماژول |
| Entry point | نقطه ورود |
| Dependency | وابستگی |
| Lifespan | چرخه عمر |
| Startup | راه‌اندازی |
| Shutdown | خاموشی |
| Idle / idle state | بیکار / حالت بیکار |

## Database

| English | Persian |
|---|---|
| Schema | اسکیما |
| Table | جدول |
| Column | ستون |
| Primary key | کلید اصلی |
| Constraint | محدودیت |
| Connection pool | pool اتصال |
| Query | پرس‌وجو |
| DDL (Data Definition Language) | DDL (زبان تعریف داده) |
| DML (Data Manipulation Language) | DML (زبان دستکاری داده) |
| SELECT | SELECT |
| INSERT | INSERT |
| ON CONFLICT DO UPDATE | ON CONFLICT DO UPDATE |
| PostgreSQL | PostgreSQL |

## API / Web

| English | Persian |
|---|---|
| Endpoint | نقطه پایانی |
| Route | مسیر |
| Trigger | محرک / trigger |
| Webhook | webhook |
| Bearer token | توکن Bearer |
| Authentication | احراز هویت |
| Authorization | مجوزدهی |
| Health check | بررسی سلامت |
| Liveness probe | کاوش زنده بودن |
| Readiness probe | کاوش آمادگی |
| Request | درخواست |
| Response | پاسخ |
| Payload | بار محموله / payload |
| Header | هدر |
| Status code | کد وضعیت |
| Timeout | مدت انتظار / timeout |
| Rate limit | محدودیت نرخ |

## Deployment

| English | Persian |
|---|---|
| Deployment | استقرار |
| Repository | مخزن |
| Image | تصویر |
| Container | کانتینر |
| Orchestration | orchestration |
| Cluster | خوشه |
| Node | گره |
| Probe | کاوشگر |
| Secret | راز / secret |
| Environment variable | متغیر محیطی |
| Multi-stage build | بیلد چندمرحله‌ای |
| Healthcheck | بررسی سلامت |
| Unprivileged user | کاربر غیر ریشه (non-root) |

## Development / Operations

| English | Persian |
|---|---|
| Concurrency | هم‌روندی |
| Semaphore | سمافور |
| Retry | تلاش مجدد |
| Exponential backoff | backoff نمایی |
| Transient error | خطای گذرا |
| Exception | استثنا |
| Async / asynchronous | ناهم‌زمان / async |
| Pool | pool (مجموعه اتصالات) |
| Logger | لاگر |
| Handler | هندلر |
| Structured logging | لاگ ساختاریافته |
| JSON | JSON |
| Dockerfile | Dockerfile |
| Docker Compose | Docker Compose |
| Kubernetes | Kubernetes |

## Project / Repository

| English | Persian |
|---|---|
| Repository | مخزن |
| Public | عمومی |
| Private | خصوصی |
| Fork | fork |
| Branch | شاخه |
| Commit | commit |
| Push | push |
| Remote | remote |
| README | README |
| License | مجوز |
| Open source | متن‌باز |
| Contribution | مشارکت |
| Pull request | درخواست pull |
| Issue | issue |
| Discussion | بحث / discussion |

## Code quality

| English | Persian |
|---|---|
| Type annotation | نوع‌نویسی |
| Docstring | مستندات درون‌کدی |
| Code quality | کیفیت کد |
| Testing | تست / آزمون |
| Unit test | تست واحد |
| Integration test | تست یکپارچگی |
| Code review | بازبینی کد |
| Debugging | رفع اشکال / دیباگ |
| Lint | لینت / بررسی کد |
| Type hint | راهنمای نوع |

## File / directory conventions

When documenting Persian projects, use these conventions:

- **README.md** — English (primary)
- **README.fa.md** — Persian translation
- Mark the Persian file with a language indicator at the top: `# پروژه — زبان فارسی`
- Keep all code blocks in English regardless of surrounding prose language
- Use `dir="rtl"` only if HTML rendering — GitHub Markdown renders LTR natively, Persian text flows correctly in Markdown without RTL attributes
