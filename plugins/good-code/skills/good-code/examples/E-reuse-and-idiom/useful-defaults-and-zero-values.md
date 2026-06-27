# useful-defaults-and-zero-values

_Theme E: reuse-and-idiom_

## value mutex makes the zero value usable; drop the constructor  ·  `go`  ·  synthetic

**Before**
```go
type Counter struct {
    mu    *sync.Mutex
    count int
}

func NewCounter() *Counter {
    return &Counter{mu: &sync.Mutex{}}
}

func (c *Counter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}
// callers must remember: c := NewCounter()
```

**After**
```go
type Counter struct {
    mu    sync.Mutex // zero value is an unlocked mutex; no constructor needed
    count int
}

// usable directly: var c Counter; c.Inc()
func (c *Counter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}
```

**Why:** Shows the Go idiom of embedding sync.Mutex by value so the struct's zero value is ready and the NewCounter ceremony disappears. when_not: this only works because mutex and int zero values are valid; a struct holding a map still needs explicit init (a nil map panics on write), so don't blanket-delete constructors for fields whose zero value is unusable.

---

## default_factory empties remove None-guards in total()  ·  `python`  ·  synthetic

**Before**
```python
class Cart:
    def __init__(self, items=None, discounts=None):
        if items is None:
            items = []
        self.items = items
        self.discounts = discounts  # may be None

    def total(self):
        subtotal = sum(i.price for i in self.items)
        if self.discounts is None:
            return subtotal
        return subtotal - sum(self.discounts)
```

**After**
```python
@dataclass
class Cart:
    items: list[Item] = field(default_factory=list)
    discounts: list[Decimal] = field(default_factory=list)

    def total(self) -> Decimal:
        subtotal = sum((i.price for i in self.items), Decimal(0))
        return subtotal - sum(self.discounts, Decimal(0))
```

**Why:** Demonstrates empty-but-usable collections via field(default_factory=list) so the common path needs no None sentinel and total() drops its is-None branch. when_not: this is safe only because 'no discounts' is semantically identical to an empty list; for a field where unset must differ from a real zero (an optional applied_coupon, or an as-yet-unpriced item) keep Optional/None rather than collapsing the distinction.

---

## return empty array instead of null so callers skip the guard  ·  `typescript`  ·  synthetic

**Before**
```typescript
function getTags(post: Post): string[] | null {
  if (!post.tags || post.tags.length === 0) {
    return null;
  }
  return post.tags;
}

// every caller must guard:
const tags = getTags(post);
if (tags !== null) {
  for (const tag of tags) index(tag);
}
```

**After**
```typescript
function getTags(post: Post): string[] {
  return post.tags ?? []; // empty-but-usable; callers never null-check
}

// caller just iterates:
for (const tag of getTags(post)) index(tag);
```

**Why:** Shows returning a useful zero value (an empty array) so the iterate-tags common case needs no null branch at any call site. when_not: collapse to [] only when 'no tags field present' and 'explicitly empty tags' should be treated the same; if a caller genuinely must distinguish absent vs empty (e.g. PATCH semantics, or 'never fetched' vs 'fetched, none'), keep the nullable return.

---
