# pure-seams-explicit-dependencies

_Theme B: function-and-module-shape_

## totals threaded through self-state instead of returned  ·  `python`  ·  synthetic

**Before**
```python
class PriceCalculator:
    def total(self, items):
        self.items = items          # stash args as instance state
        self.subtotal = 0
        self._sum()                 # mutates self.subtotal
        self._discount()            # reads/mutates self.subtotal
        return self.subtotal

    def _sum(self):
        for i in self.items:
            self.subtotal += i.price * i.qty

    def _discount(self):
        if self.subtotal > 100:
            self.subtotal *= 0.9
```

**After**
```python
def order_total(items: list[Item]) -> float:
    subtotal = sum(i.price * i.qty for i in items)
    return subtotal * 0.9 if subtotal > 100 else subtotal
```

**Why:** Shows the PrimeGenerator tell: helpers take no args and communicate only through self, so they aren't reentrant or independently testable; the fix makes the seam pure (value in, value out). when-NOT: don't read this as 'never hold state' — an object whose state is its purpose (a streaming aggregator, an open buffer) legitimately keeps it.

---

## per-request data stashed on a singleton service  ·  `typescript`  ·  synthetic

**Before**
```typescript
class OrderService {
  private cart!: CartItem[]
  private userId!: string

  handle(req: OrderRequest): number {
    this.cart = req.cart            // hide params as instance state
    this.userId = req.userId
    return this.computeTotal()      // no args; reads hidden this.cart
  }

  private computeTotal(): number {
    // singleton: concurrent requests overwrite this.cart -> wrong totals
    return this.cart.reduce((sum, i) => sum + i.price * i.qty, 0)
  }
}
```

**After**
```typescript
function computeTotal(cart: CartItem[]): number {
  return cart.reduce((sum, i) => sum + i.price * i.qty, 0)
}

class OrderService {
  handle(req: OrderRequest): number {
    return computeTotal(req.cart)   // dependency explicit; no shared state
  }
}
```

**Why:** Demonstrates that shortening signatures by parking request data on a shared singleton is a real concurrency bug, not just a style nit; the explicit parameter is safe and testable. when-NOT: a per-connection/per-session object (a WebSocket session, an open DB transaction) carrying state is fine — the target is ambient shared-mutable singletons.

---

## package-global counter mutated by a free function  ·  `go`  ·  synthetic

**Before**
```go
// package-level mutable state shared by every caller
var lastID int64

func NextID() int64 {
    lastID++        // data race under concurrent requests
    return lastID
}
```

**After**
```go
type IDSequence struct {
    n atomic.Int64
}

// Next is safe for concurrent use; state is owned, not ambient.
func (s *IDSequence) Next() int64 {
    return s.n.Add(1)
}
```

**Why:** Shows ambient package-global mutation (hidden dependency + data race + untestable) turned into an owned, injectable dependency. when-NOT: the fix is itself stateful — the enemy was the hidden package-level singleton, not statefulness; a struct with a coherent lifecycle is the correct home for that state.

---

## Dependency Injection — Greet accepting io.Writer (Learn Go with Tests)  ·  `go`  ·  ✅ sourced
Source: https://quii.gitbook.io/learn-go-with-tests/go-fundamentals/dependency-injection

**Before**
```go
func Greet(name string) {
	fmt.Printf("Hello, %s", name)
}
```

**After**
```go
func Greet(writer io.Writer, name string) {
	fmt.Fprintf(writer, "Hello, %s", name)
}
```

**Why:** Before, Greet hard-wires its output to stdout via fmt.Printf, a hidden dependency on os.Stdout that gives tests no seam to observe behavior. After, the output destination is an explicit io.Writer parameter, so the collaborator is injected: production passes os.Stdout, tests pass a bytes.Buffer to assert on. The function becomes a pure transformation over its explicit inputs/output sink. When NOT to do it: do not parameterize stable, side-effect-free dependencies (e.g. pure stdlib math or trivial helpers) — inject only the side-effecting or substitutable collaborators that actually need a test seam, or you just add noise.

_Verified: Fetched https://quii.gitbook.io/learn-go-with-tests/go-fundamentals/dependency-injection. The page's dependency injection chapter refactors the Greet function exactly as claimed. Original/before: `func Greet(name string) { fmt.Printf("Hello, %s", name) }`. Refactored/after: `func Greet(writer io.Writer, name string) { fmt.Fprintf(writer, "Hello, %s", name) }`. This matches the candidate's before and after fields verbatim, and the section demonstrates the pure-seams/explicit-dependencies pattern by injecting an io.Writer as the first parameter instead of hardcoding stdout via fmt.Printf. Verified for Go._

---
