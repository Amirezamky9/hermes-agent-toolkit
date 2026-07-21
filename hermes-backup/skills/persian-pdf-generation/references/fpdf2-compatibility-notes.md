# fpdf2 Version Compatibility Notes (2026)

## The `uni` parameter was removed in fpdf2 v2.5.1

```python
# ❌ ERROR in fpdf2 2.5.1+
self.add_font("Vazir", "", FONT_REGULAR, uni=True)

# ✅ CORRECT for 2.5.1+
self.add_font("Vazir", "", FONT_REGULAR)
```

If you see `DeprecationWarning: "uni" parameter is deprecated`, remove `uni=True` from all `add_font()` calls. The parameter was silently dropped and passing it now has no effect, but future versions (v2.6+) will raise an error.

## Style characters: Only "B" and "I" are valid

```python
# ❌ ERROR — fpdf2 accepts only "B" and "I" as style modifiers
self.add_font("Vazir", "M", FONT_MEDIUM)  # "M" for Medium
self.add_font("Vazir", "L", FONT_LIGHT)   # "L" for Light

# ✅ CORRECT — only register "" (regular) and "B" (bold)
self.add_font("Vazir", "", FONT_REGULAR)
self.add_font("Vazir", "B", FONT_BOLD)
```

If you need Medium/Light weights, use the closest available style (bold for medium, regular for light) — there's no way to register custom style characters in fpdf2.
