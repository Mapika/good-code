# prefer-clear-over-clever

_Theme F: naming-and-clarity_

## shipping cost crammed into one nested-ternary expression  ·  `python`  ·  synthetic

**Before**
```python
def shipping_cost(weight_kg, country, express):
    return (0 if weight_kg == 0 else
            (5 if country == "US" else 12) * (2 if express else 1)
            + (3 if weight_kg > 10 else 0))
```

**After**
```python
def shipping_cost(weight_kg: float, country: str, express: bool) -> int:
    if weight_kg == 0:
        return 0
    base = 5 if country == "US" else 12
    rate = base * 2 if express else base
    heavy_surcharge = 3 if weight_kg > 10 else 0
    return rate + heavy_surcharge
```

**Why:** Shows binding each pricing decision to a named local so the rule is reviewable line by line, the point of clear-over-clever. Note the after KEEPS the simple two-way ternaries (base = 5 if ... else 12); the when_not is that a well-understood one-liner shouldn't be inflated into if/else ceremony, only the dense compound expression is unpacked.

---

## authorization check as a nested ternary  ·  `typescript`  ·  synthetic

**Before**
```typescript
function canEdit(u: User, doc: Doc): boolean {
  return u.role === "admin"
    ? true
    : u.role === "editor"
    ? doc.ownerId === u.id
      ? true
      : doc.shared
    : false
}
```

**After**
```typescript
function canEdit(u: User, doc: Doc): boolean {
  if (u.role === "admin") return true
  if (u.role !== "editor") return false
  return doc.ownerId === u.id || doc.shared
}
```

**Why:** Demonstrates that a genuinely NESTED ternary (a ? : (b ? : c) : ) carries real cognitive load and reads far better as ordered guard clauses plus a plain boolean. The when_not guard: a flat single ternary like score > 0 ? "pass" : "fail" is already clear and should be left alone, this is not a blanket ban on ?:.

---

## pagination slice with inline min() calls  ·  `go`  ·  synthetic

**Before**
```go
func page(items []Item, pageNum, size int) []Item {
    return items[min(pageNum*size, len(items)):min(pageNum*size+size, len(items))]
}
```

**After**
```go
func page(items []Item, pageNum, size int) []Item {
    start := min(pageNum*size, len(items))
    end := min(start+size, len(items))
    return items[start:end]
}
```

**Why:** Shows that off-by-one-prone slice bounds are easy to verify when start and end are named locals, instead of two clever min() calls buried in the slice expression. The when_not: a plain items[a:b] needs no such expansion, the fix targets only the bound arithmetic that a reader otherwise has to recompute mentally.

---
