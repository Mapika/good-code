# fix-code-instead-of-explaining-it

_Theme A: comments-and-docs_

## paraphrase comment on a settlement eligibility check  ·  `python`  ·  synthetic

**Before**
```python
def settle(order):
    # check paid is true, refunded is false, and 7 days elapsed since shipping
    if order.paid and not order.refunded and (now() - order.shipped_at).days > 7:
        release_funds(order)
```

**After**
```python
RETURN_WINDOW_DAYS = 7  # chargeback window per merchant agreement (FIN-204)

def settle(order):
    return_window_passed = (now() - order.shipped_at).days > RETURN_WINDOW_DAYS
    eligible_for_release = order.paid and not order.refunded and return_window_passed
    if eligible_for_release:
        release_funds(order)
```

**Why:** Turns a WHAT-paraphrase comment into named explaining variables plus a named constant, so the eligibility rule reads in domain terms with no comment needed. When-NOT guard: don't manufacture a single-use helper or hoist a truly self-evident one-off value just to kill a comment; and the genuine WHY behind the 7 days (why this window exists) is information the code can't carry, so it stays as a short why-comment/ticket link on the constant.

---

## magic page-size duplicated with a math paraphrase comment  ·  `typescript`  ·  synthetic

**Before**
```typescript
function listUsers(req: Request) {
  // skip (page-1)*50 rows, then return 50 per page
  const offset = (Number(req.query.page) - 1) * 50;
  return db.users.findMany({ skip: offset, take: 50 });
}
```

**After**
```typescript
const PAGE_SIZE = 50;

function listUsers(req: Request) {
  const page = Number(req.query.page);
  const offset = (page - 1) * PAGE_SIZE;
  return db.users.findMany({ skip: offset, take: PAGE_SIZE });
}
```

**Why:** Replaces a comment that just narrates the offset arithmetic with a named constant, which also removes the duplicated literal 50 so the meaning is self-documenting. When-NOT guard: naming is warranted here because the value recurs and the comment only restated mechanics; a single, obvious, one-off literal would not need a constant, and a genuinely tricky pagination edge (off-by-one cursor logic) would still earn a short clarifying comment.

---

## cryptic nanosecond timeout literal with a what-comment  ·  `go`  ·  synthetic

**Before**
```go
func newUpstreamClient() *http.Client {
    // 90 second timeout for the slow batch upstream
    return &http.Client{Timeout: 90 * 1000 * 1000 * 1000}
}
```

**After**
```go
// Batch upstream can take ~1m under load; allow margin (see RUNBOOK-12).
const upstreamTimeout = 90 * time.Second

func newUpstreamClient() *http.Client {
    return &http.Client{Timeout: upstreamTimeout}
}
```

**Why:** Fixes the code instead of explaining it: the opaque 90*1000*1000*1000 nanosecond literal becomes self-documenting via time.Second and a named constant, so the WHAT-comment disappears. When-NOT guard: the retained comment is now a WHY (why 90s), which no name can capture, so it is correctly kept short rather than deleted in pursuit of zero comments.

---
