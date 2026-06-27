# solve-todays-problem-yagni

_Theme C: abstraction-discipline_

## data-access fn grows knobs no caller sets  ·  `python`  ·  synthetic

**Before**
```python
def fetch_recent_orders(
    customer_id: int,
    *,
    limit: int = 50,
    order_by: str = "created_at",
    descending: bool = True,
    include_archived: bool = False,
    as_dict: bool = False,
) -> list[Order]:
    q = "SELECT * FROM orders WHERE customer_id = %s"
    if not include_archived:
        q += " AND archived = false"
    q += f" ORDER BY {order_by} {'DESC' if descending else 'ASC'} LIMIT {limit}"
    rows = db.execute(q, [customer_id]).fetchall()
    return [dict(r) for r in rows] if as_dict else [Order.from_row(r) for r in rows]

# every call site is: fetch_recent_orders(cid)
```

**After**
```python
def fetch_recent_orders(customer_id: int) -> list[Order]:
    rows = db.execute(
        "SELECT * FROM orders WHERE customer_id = %s AND archived = false "
        "ORDER BY created_at DESC LIMIT 50",
        [customer_id],
    ).fetchall()
    return [Order.from_row(r) for r in rows]
```

**Why:** Shows the over-parameterized-signature anti-pattern where every caller passes the same defaults; the speculative order_by knob even opens a SQL-injection hole. When-NOT: the moment a second caller genuinely needs, say, a different limit, add that one parameter then -- don't pre-emptively delete legitimate flexibility a real caller already uses.

---

## enqueue options object with fields nobody passes  ·  `typescript`  ·  synthetic

**Before**
```typescript
interface EnqueueOptions {
  priority?: number
  delayMs?: number
  maxRetries?: number
  backoff?: "fixed" | "exponential"
  dedupeKey?: string
  onComplete?: (id: string) => void
}

async function enqueueEmail(
  to: string,
  body: string,
  opts: EnqueueOptions = {},
): Promise<string> {
  // every call site is enqueueEmail(to, body)
  return queue.add("email", { to, body }, opts)
}
```

**After**
```typescript
async function enqueueEmail(to: string, body: string): Promise<string> {
  return queue.add("email", { to, body })
}
```

**Why:** Demonstrates a speculative options bag invented from zero call sites that vary it -- every field is dead surface a reader must understand. When-NOT: this is not a license to drop options a published/library API documents for external callers, nor to inline a knob a second internal caller actually sets today.

---

## functional-options ceremony for a single NewCache() call  ·  `go`  ·  synthetic

**Before**
```go
type Option func(*Cache)

func WithTTL(d time.Duration) Option     { return func(c *Cache) { c.ttl = d } }
func WithMaxEntries(n int) Option        { return func(c *Cache) { c.max = n } }
func WithEvictionPolicy(p string) Option { return func(c *Cache) { c.policy = p } }

func NewCache(opts ...Option) *Cache {
	c := &Cache{ttl: 5 * time.Minute, max: 1000, policy: "lru"}
	for _, opt := range opts {
		opt(c)
	}
	return c
}

// only call site: NewCache()
```

**After**
```go
func NewCache() *Cache {
	return &Cache{ttl: 5 * time.Minute, max: 1000}
}
```

**Why:** Captures the Go variadic functional-options pattern scaffolded for one concrete, optionless caller -- three exported Option helpers and a loop that never runs. When-NOT: if NewCache were an exported constructor with real external users, or a second caller needed to vary TTL, the options pattern earns its keep; pick a sensible internal default until then.

---
