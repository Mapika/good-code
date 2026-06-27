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

## Refactoring.Guru: Replace Nested Conditional with Guard Clauses  ·  `python`  ·  ✅ sourced
Source: https://refactoring.guru/replace-nested-conditional-with-guard-clauses

**Before**
```python
def getPayAmount(self):
    if self.isDead:
        result = deadAmount()
    else:
        if self.isSeparated:
            result = separatedAmount()
        else:
            if self.isRetired:
                result = retiredAmount()
            else:
                result = normalPayAmount()
    return result
```

**After**
```python
def getPayAmount(self):
    if self.isDead:
        return deadAmount()
    if self.isSeparated:
        return separatedAmount()
    if self.isRetired:
        return retiredAmount()
    return normalPayAmount()
```

**Why:** Demonstrates clarity over a clever/deeply-nested control structure: the 'arrow' of nested if/else with a mutated `result` temp is flattened into flat early-return guard clauses, so each special case reads linearly. When-NOT: guard clauses suit early exits for special/edge cases; if both branches are equally important normal paths (not exceptional), an if/else better signals their equal weight, so don't force every conditional into guards.

_Verified: Fetched https://refactoring.guru/replace-nested-conditional-with-guard-clauses. The page offers code in 5 languages (Java, C#, PHP, Python, TypeScript). The Python tab shows the Before block as a `getPayAmount(self)` method with nested if/else assigning `result` (deadAmount/separatedAmount/retiredAmount/normalPayAmount) and a final `return result` — matching the candidate's `before` verbatim. The After block flattens it into guard clauses: `if self.isDead: return deadAmount()`, `if self.isSeparated: return separatedAmount()`, `if self.isRetired: return retiredAmount()`, ending with `return normalPayAmount()` — matching the candidate's `after` verbatim. Both before/after and the described pattern are genuinely present on the page's Python tab._

---
