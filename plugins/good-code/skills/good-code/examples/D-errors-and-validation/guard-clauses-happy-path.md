# guard-clauses-happy-path

_Theme D: errors-and-validation_

## HTTP handler nests on success instead of returning on error  ·  `go`  ·  synthetic

**Before**
```go
func handleGetUser(w http.ResponseWriter, r *http.Request) {
    id := r.URL.Query().Get("id")
    if id != "" {
        user, err := store.Find(id)
        if err == nil {
            if user.Active {
                json.NewEncoder(w).Encode(user)
            } else {
                http.Error(w, "inactive", http.StatusForbidden)
            }
        } else {
            http.Error(w, "not found", http.StatusNotFound)
        }
    } else {
        http.Error(w, "missing id", http.StatusBadRequest)
    }
}
```

**After**
```go
func handleGetUser(w http.ResponseWriter, r *http.Request) {
    id := r.URL.Query().Get("id")
    if id == "" {
        http.Error(w, "missing id", http.StatusBadRequest)
        return
    }
    user, err := store.Find(id)
    if err != nil {
        http.Error(w, "not found", http.StatusNotFound)
        return
    }
    if !user.Active {
        http.Error(w, "inactive", http.StatusForbidden)
        return
    }
    json.NewEncoder(w).Encode(user)
}
```

**Why:** Demonstrates Go's 'indent error flow' idiom: return on each failed precondition so the success path is un-nested at the bottom, the opposite of nesting the happy case inside `if err == nil`. When-NOT: guards are for invalid/exceptional cases only; don't reach for early returns where two outcomes are equal-weight domain branches that read better as a symmetric if/else.

---

## null-and-exists pyramid with else-after-throw  ·  `typescript`  ·  synthetic

**Before**
```typescript
function getShippingCost(order: Order | null): number {
  if (order) {
    if (order.items.length > 0) {
      if (order.address) {
        return rateFor(order.address, order.items);
      } else {
        throw new Error("no shipping address");
      }
    } else {
      throw new Error("order has no items");
    }
  } else {
    throw new Error("no order");
  }
}
```

**After**
```typescript
function getShippingCost(order: Order | null): number {
  if (!order) throw new Error("no order");
  if (order.items.length === 0) throw new Error("order has no items");
  if (!order.address) throw new Error("no shipping address");
  return rateFor(order.address, order.items);
}
```

**Why:** Collapses a null-and-exists pyramid into flat guards and drops each `else` after a terminating `throw`, leaving one readable happy-path return. When-NOT: this works because every guard is an invalid/exceptional case; a legitimately two-way domain choice of equal weight should stay a single symmetric if/else rather than be split into scattered throws/returns.

---

## pagination parsing nested in if/else with else-after-raise  ·  `python`  ·  synthetic

**Before**
```python
def parse_pagination(params: dict) -> tuple[int, int]:
    if "limit" in params:
        limit = int(params["limit"])
        if limit <= 0:
            raise ValueError("limit must be positive")
        else:
            if limit > 100:
                raise ValueError("limit too large")
            else:
                offset = int(params.get("offset", 0))
                return limit, offset
    else:
        return 50, 0
```

**After**
```python
def parse_pagination(params: dict) -> tuple[int, int]:
    if "limit" not in params:
        return 50, 0
    limit = int(params["limit"])
    if limit <= 0:
        raise ValueError("limit must be positive")
    if limit > 100:
        raise ValueError("limit too large")
    offset = int(params.get("offset", 0))
    return limit, offset
```

**Why:** Handles the default case and validation failures first with early returns/raises and removes the LLM 'else after a terminating branch' tell, so the real parsing reads un-indented at the bottom. When-NOT: don't over-apply this to genuine equally-weighted branching; the default-vs-explicit split here is a true precondition, not two co-equal domain paths that a symmetric if/else would express better.

---

## Replace Nested Conditional with Guard Clauses (Refactoring.Guru)  ·  `python`  ·  ✅ sourced
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

**Why:** Demonstrates flattening deeply nested if/else into a flat list of guard clauses with early returns, so each special case exits immediately and the 'normal' path (normalPayAmount) reads at the bottom without indentation. When NOT to apply: if every branch shares cleanup/finalization or a resource must be released on exit, scattering returns can drop that cleanup, so prefer a single exit (or try/finally) instead.

_Verified: Fetched https://refactoring.guru/replace-nested-conditional-with-guard-clauses. The Python example is present and matches the candidate byte-for-byte. BEFORE: `def getPayAmount(self):` with nested if/else assigning `result = deadAmount()`, `separatedAmount()`, `retiredAmount()`, `normalPayAmount()` then `return result`. AFTER: sequential guard clauses `if self.isDead: return deadAmount()`, `if self.isSeparated: return separatedAmount()`, `if self.isRetired: return retiredAmount()`, ending in `return normalPayAmount()`. Both the nested-with-result before and the sequential-early-return after exactly match the candidate's before/after fields._

---
