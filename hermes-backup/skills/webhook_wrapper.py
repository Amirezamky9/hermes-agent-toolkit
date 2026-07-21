#!/home/hermeswebui/.venv/bin/python3
"""
n8n Workflow Webhook Wrapper — Dual Mode
=========================================
دو حالت مجزا برای دو وب‌هوک مختلف:

حالت ۱ — Search: جستجوی ورک‌فلوهای مشابه با query + category
  python3 webhook_wrapper.py search --query "<text>" --category "<category>"
  → POST به https://n8n.mym8m.cloud/webhook/9fbc7330-3744-4105-b5a8-974c6959938e
  → خروجی: آرایه JSON از {id, title, goal, flowLogic, nodeCount}

حالت ۲ — Fetch: دریافت JSON کامل یک ورک‌فلو با UUID دیتابیس
  python3 webhook_wrapper.py fetch <UUID>
  python3 webhook_wrapper.py <UUID>   (حالت پیش‌فرض برای backward compatibility)
  → POST به https://n8n.mym8m.cloud/webhook-test/workflowid-to-jsonfile
  → خروجی: JSON کامل ورک‌فلو با نودها، کانکشن‌ها و credentialها

Exit codes:
  0 = success (JSON to stdout)
  1 = invalid UUID / missing arguments
  2 = HTTP error
  3 = timeout / connection error
  4 = empty response
"""

import sys
import json
import re
import urllib.request
import urllib.error
import socket

# ── Webhook URLs ──────────────────────────────────────────────────────────
SEARCH_WEBHOOK_URL = "https://n8n.mym8m.cloud/webhook/9fbc7330-3744-4105-b5a8-974c6959938e"
FETCH_WEBHOOK_URL = "https://n8n.mym8m.cloud/webhook/2e7d73f9-b090-41d7-baf6-dd6e9621b13d"

UUID_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE
)
TIMEOUT = 30
MAX_RETRIES = 2


# ── Valid 17 categories ──────────────────────────────────────────────────
VALID_CATEGORIES = [
    "Multimodal AI",
    "AI Summarization",
    "AI",
    "AI Chatbot",
    "AI RAG",
    "Content Creation",
    "Market Research",
    "Marketing",
    "Social Media",
    "Document Extraction",
    "Lead Generation",
    "Engineering",
    "Automation",
    "Sales & CRM",
    "IT & DevOps",
    "Business Operations",
    "Other",
]


def validate_uuid(uuid_str: str) -> bool:
    """Validate UUID v4 format."""
    return bool(UUID_PATTERN.match(uuid_str.strip()))


def post_to_webhook(url: str, payload_dict: dict) -> dict:
    """
    Generic webhook POST. Returns structured result dict.
    Handles HTTP errors, timeouts, empty responses, and retries.
    """
    payload = json.dumps(payload_dict).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST"
    )

    last_error = None
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                raw = resp.read().decode('utf-8').strip()
                if not raw:
                    return {
                        "error": True,
                        "code": 4,
                        "message": f"پاسخ خالی از سرور (HTTP {resp.status})."
                    }
                try:
                    data = json.loads(raw)
                    return {
                        "error": False,
                        "code": 0,
                        "data": data,
                    }
                except json.JSONDecodeError:
                    return {
                        "error": True,
                        "code": 4,
                        "message": f"پاسخ معتبر JSON نیست. خروجی:\n{raw[:500]}"
                    }

        except urllib.error.HTTPError as e:
            last_error = f"HTTP {e.code}: {e.reason}"
            if attempt > MAX_RETRIES:
                body = e.read().decode('utf-8', errors='replace')[:300]
                return {
                    "error": True,
                    "code": 2,
                    "message": f"خطای HTTP {e.code} — {body or e.reason}"
                }
        except urllib.error.URLError as e:
            last_error = str(e.reason)
            if attempt > MAX_RETRIES:
                return {
                    "error": True,
                    "code": 3,
                    "message": f"خطای اتصال — {e.reason}"
                }
        except socket.timeout:
            last_error = "timeout"
            if attempt > MAX_RETRIES:
                return {
                    "error": True,
                    "code": 3,
                    "message": f"تایم‌اوت بعد از {TIMEOUT} ثانیه."
                }

        import time
        time.sleep(1)

    return {
        "error": True,
        "code": 3,
        "message": f"ناموفق بعد از {MAX_RETRIES + 1} بار تلاش. آخرین خطا: {last_error}"
    }


# ── Mode 1: Search ────────────────────────────────────────────────────────
def cmd_search(args: list) -> dict:
    """
    Search workflows by query text + category.
    
    Usage: webhook_wrapper.py search --query "<text>" --category "<category>"
    
    --category is optional; if omitted, no category filter is sent.
    If provided, it must be one of the 17 valid categories.
    """
    query = ""
    category = ""

    # Parse --query and --category from remaining args
    i = 0
    while i < len(args):
        if args[i] == "--query" and i + 1 < len(args):
            query = args[i + 1].strip()
            i += 2
        elif args[i] == "--category" and i + 1 < len(args):
            category = args[i + 1].strip()
            i += 2
        else:
            i += 1

    if not query:
        return {
            "error": True,
            "code": 1,
            "message": "کاربرد: python3 webhook_wrapper.py search --query \"<text>\" [--category \"<category>\"]\n"
                       "--query الزامی است. --category اختیاری است (از ۱۷ دسته معتبر)."
        }

    if category and category not in VALID_CATEGORIES:
        return {
            "error": True,
            "code": 1,
            "message": f"دسته '{category}' نامعتبر است.\n"
                       f"دسته‌های معتبر (۱۷ عدد):\n" +
                       "\n".join(f"  {i+1}. {c}" for i, c in enumerate(VALID_CATEGORIES))
        }

    payload = {"query": query}
    if category:
        payload["category"] = category

    result = post_to_webhook(SEARCH_WEBHOOK_URL, payload)

    # Wrap empty result as informative message
    if not result.get("error") and result.get("data") is not None:
        data = result["data"]
        # data should be a list; if empty list, enrich with code 4
        if isinstance(data, list) and len(data) == 0:
            return {
                "error": False,
                "code": 4,
                "data": [],
                "message": f"نتیجه‌ای برای query='{query}'" +
                           (f" و category='{category}'" if category else "") +
                           " یافت نشد."
            }
        # data is a list with items or non-list — pass through
        return {
            "error": False,
            "code": result.get("code", 0),
            "data": data,
            "query": query,
            "category": category or None,
        }

    return result


# ── Mode 2: Fetch by UUID ────────────────────────────────────────────────
def cmd_fetch(uuid_str: str) -> dict:
    """
    Fetch full workflow JSON by database UUID.
    
    Usage: webhook_wrapper.py fetch <UUID>
           webhook_wrapper.py <UUID>   (backward compatible)
    
    UUID از فیلد id خروجی search میاد (database UUID).
    POST به webhook با body: {"workflowid": "<UUID>"}
    """
    uuid_str = uuid_str.strip()

    if not validate_uuid(uuid_str):
        return {
            "error": True,
            "code": 1,
            "message": f"UUID نامعتبر: '{uuid_str}'. "
                       f"فرمت باید xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx باشد."
        }

    payload = {"workflowid": uuid_str}
    result = post_to_webhook(FETCH_WEBHOOK_URL, payload)

    # Enrich with uuid for reference
    if not result.get("error"):
        result["uuid"] = uuid_str

    return result


# ── Main ──────────────────────────────────────────────────────────────────
def print_usage():
    print(json.dumps({
        "error": True,
        "code": 1,
        "message": (
            "کاربرد:\n"
            "  1) جستجو (Search):  python3 webhook_wrapper.py search --query \"<text>\" [--category \"<category>\"]\n"
            "  2) دریافت JSON (Fetch): python3 webhook_wrapper.py fetch <UUID>\n"
            "  3) دریافت JSON (کوتاه):  python3 webhook_wrapper.py <UUID>\n"
            "\n"
            "حالت ۱ — جستجوی ورک‌فلوهای مشابه با query + category (از ۱۷ دسته)\n"
            "  خروجی: آرایه JSON [{id, title, goal, flowLogic, nodeCount}, ...]\n"
            "\n"
            "حالت ۲ — دریافت JSON کامل یک ورک‌فلو با UUID دیتابیس\n"
            "  خروجی: JSON کامل ورک‌فلو با نودها، کانکشن‌ها، credentialها\n"
            "\n"
            "مثال:\n"
            "  python3 webhook_wrapper.py search --query \"telegram coffee shop\" --category \"AI Chatbot\"\n"
            "  python3 webhook_wrapper.py fetch 550e8400-e29b-41d4-a716-446655440000\n"
            "  python3 webhook_wrapper.py 550e8400-e29b-41d4-a716-446655440000"
        ),
        "usage": "python3 webhook_wrapper.py [search|fetch] [args...]",
        "valid_categories": VALID_CATEGORIES,
    }))


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    first_arg = sys.argv[1].lower()

    # ── Mode 1: search ────────────────────────────────────────────────
    if first_arg == "search":
        result = cmd_search(sys.argv[2:])
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if not result.get("error") else result.get("code", 1))

    # ── Mode 2: fetch (explicit or implicit) ──────────────────────────
    if first_arg == "fetch":
        if len(sys.argv) < 3:
            print(json.dumps({
                "error": True,
                "code": 1,
                "message": "کاربرد: python3 webhook_wrapper.py fetch <UUID>"
            }))
            sys.exit(1)
        uuid_str = sys.argv[2]
    else:
        # Backward compatible: bare UUID
        uuid_str = first_arg

    result = cmd_fetch(uuid_str)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if not result.get("error") else result.get("code", 1))


if __name__ == "__main__":
    main()
