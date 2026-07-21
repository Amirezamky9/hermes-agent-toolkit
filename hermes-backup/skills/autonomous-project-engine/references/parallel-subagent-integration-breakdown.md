# Parallel Subagent Integration Breakdown

## Session: BREW Coffee Marketplace (2026-07-14)

Three parallel subagents built backend, frontend, and seed/tests simultaneously.
Result: Backend had 8 integration failures from cross-file inconsistency.

## The 7 Specific Bugs Found

### 1. PK Type Mismatch
```
database.py (backend subagent):       id = Column(String, primary_key=True, default=generate_uuid)
seed.py (seed subagent):              id = Column(Integer, primary_key=True)
models.py (backend subagent):         id: str
routes/auth_routes.py:                User(id=generate_uuid(), ...)
```
**Fix**: Changed all to `Integer, primary_key=True, autoincrement=True`.

### 2. JWT sub Type (python-jose constraint)
```
auth_routes.py:           create_access_token(data={"sub": user.id})       # user.id is int
python-jose requirement:  sub must be a string
```
**Fix**: `create_access_token(data={"sub": str(user.id)})` in both register and login.  
Also need `int(payload.get("sub"))` in get_current_user to compare with DB int id.

### 3. Missing ORM Relationships
```
database.py (no relationships defined):
    class CartItem(Base):
        product_id = Column(Integer, ForeignKey("products.id"))

cart_routes.py expects:          cart_item.product.name       # AttributeError!
```
**Fix**: Added `product = relationship("Product")` to CartItem (and all other models).

### 4. Field Name: delivery_day vs day_of_week
```
subscription_routes.py:           delivery_day=payload.delivery_day
database.py:                       day_of_week = Column(Integer, default=1)
```
**Fix**: Changed route to `day_of_week=payload.day_of_week`.

### 5. Field Name: body vs comment, is_approved missing
```
review_routes.py creates:   Review(body="...")                # TypeError!
review_routes.py filters:   Review.is_approved == True        # AttributeError!
database.py column:          comment = Column(Text)
```
**Fix**: Changed model field from body to comment; removed is_approved filter.

### 6. Extra Fields: phone, role, last_login_at
```
auth_routes.py creates:      User(phone=..., role=..., last_login_at=...)
database.py User model:      (no phone, no role, no last_login_at columns)
```
**Fix**: Removed the fields from auth_routes user creation.

### 7. Pydantic str vs DB int
```
models.py ProductResponse:    category_id: Optional[str] = None
database.py Product:          category_id = Column(Integer, ForeignKey("categories.id"))
```
**Fix**: Changed to `category_id: Optional[int] = None`. Same fix needed for id fields across all Pydantic models.

## Root Cause

Each subagent received the shared architecture document but **did not use a shared database.py as the source of truth**. The architecture doc described tables conceptually ("Products have categories, prices, origins...") but did not provide exact column definitions. Each subagent then invented column names independently.

The parallel subagent programming model **amplifies** this problem — without a shared `database.py` that all subagents import from, inconsistencies are inevitable.

## Solution Pattern

1. **Write database.py FIRST**, before dispatching subagents
2. Give every subagent the exact column listing (not just table descriptions)
3. Generate Pydantic models from database.py automatically (or accept manual sync)
4. After batch completion, always run a smoke test on ALL endpoints before declaring success
5. The ContextManager in v3.6 should track the frozen schema and pass it to all agents
