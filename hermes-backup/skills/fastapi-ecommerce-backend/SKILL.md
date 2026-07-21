---
name: fastapi-ecommerce-backend
description: Complete FastAPI + SQLAlchemy e-commerce backend — full CRUD, auth, product catalog, cart, orders, reviews, subscriptions.
---

# FastAPI E-Commerce Backend

## When to use

When building a complete e-commerce REST API with FastAPI + SQLAlchemy + SQLite (or any SQL backend). Covers coffee/consumable-specific attributes.

## Architecture

```
backend/
├── __init__.py
├── main.py          # FastAPI app + CORS + router includes
├── database.py      # SQLAlchemy models + engine + get_db()
├── auth.py          # JWT + bcrypt + get_current_user/admin
├── models.py        # Pydantic v2 schemas
└── routes/
    ├── __init__.py
    ├── auth_routes.py
    ├── product_routes.py
    ├── cart_routes.py
    ├── order_routes.py
    ├── review_routes.py
    └── subscription_routes.py
```

## Key patterns

### Import convention
Use **absolute** imports (`from database import ...`, `from routes import ...`) — not relative (`from .database`). Uvicorn runs `main:app` as a top-level module, not a package, so relative imports fail.

### SQLAlchemy models — coffee-specific
- Store prices in **cents** (integers, not floats) — `price_cents`, `total_cents`
- Coffee fields: `roast_level`, `origin`, `tasting_notes`, `brew_method`, `weight_oz`
- Use `String` for UUID primary keys — `generate_uuid()` helper:
  ```python
  def generate_uuid():
      return str(uuid.uuid4())
  ```

### Pydantic v2
- Use `model_config = {"from_attributes": True}` for ORM → schema
- `model_validate()` instead of `from_orm()`
- `field_validator` for enums (frequency, status)

### JWT auth
- `python-jose` + `passlib[bcrypt]` for hashing
- `get_current_user` decodes JWT `sub`, looks up user
- `get_current_admin` checks `role == "admin"`

### Search/filter pattern
```python
q = db.query(Product).filter(Product.is_active == True)
if search:
    q = q.filter(Product.name.ilike(f'%{search}%'))
# ... more filters
total = q.count()
q = q.offset((page-1)*page_size).limit(page_size)
```

## Pitfalls
- **Relative imports break** — `uvicorn main:app` treats file as top-level module, not package. Use `from database import ...` not `from .database import ...`
- **SQLite UUID** — no native UUID type; use `String` with `str(uuid.uuid4())`
- **SQLite check_same_thread** — must pass `connect_args={"check_same_thread": False}` for multi-threaded FastAPI
- **Default datetime** — use `lambda: datetime.now(timezone.utc)` (not `datetime.utcnow()` which is deprecated)
- **Order numbers** — generate unique via loop: `while db.query(Order).filter(...).first():`

## Verification
```bash
cd backend && uvicorn main:app --port 8000
curl http://localhost:8000/
curl http://localhost:8000/docs
```