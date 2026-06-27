# size-follows-cohesion

_Theme B: function-and-module-shape_

## CSV import row split into single-use trampolines  ·  `python`  ·  synthetic

**Before**
```python
def import_user(row):
    user = _build_user(row)
    _persist(user)
    return _summary(user)

def _build_user(row):
    return User(name=row[0], email=row[1])

def _persist(user):
    db.session.add(user)
    db.session.commit()

def _summary(user):
    return f"imported {user.email}"
```

**After**
```python
def import_user(row):
    user = User(name=row[0], email=row[1])
    db.session.add(user)
    db.session.commit()
    return f"imported {user.email}"
```

**Why:** Shows length following cohesion: three one-line helpers each called exactly once chop a linear flow into trampolines that add navigation cost while naming no reusable abstraction; inlining yields one coherent 5-line unit. When-NOT guard: this is not license to cram unrelated concerns together — if _persist grew retry/transaction logic or gained a second caller, or the body started mixing auth + parsing + emailing, separation would again be warranted.

---

## Health handler fragmented into trivial helpers  ·  `go`  ·  synthetic

**Before**
```go
func handleHealth(w http.ResponseWriter, r *http.Request) {
    status := buildStatus()
    writeStatus(w, status)
}

func buildStatus() map[string]string {
    return map[string]string{"status": "ok"}
}

func writeStatus(w http.ResponseWriter, status map[string]string) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(status)
}
```

**After**
```go
func handleHealth(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
}
```

**Why:** Idiomatic-Go form of tiny-function disease: each helper is single-use and hides nothing, so the interface cost exceeds the body; inlining lets the handler read as one cohesive unit. When-NOT guard: the tell is single-use AND trivial — keep a writeJSON helper the moment several handlers reuse it, or when a helper encapsulates real logic (validation, error mapping); this is not an excuse to merge genuinely distinct concerns into one func.

---

## Order endpoint mixing pricing, DB, payment, and HTTP  ·  `typescript`  ·  synthetic

**Before**
```typescript
async function createOrder(req: Request, res: Response) {
  const items = req.body.items;
  let subtotal = 0;
  for (const it of items) subtotal += it.price * it.qty;
  const tax = subtotal * 0.2;
  const total = subtotal + tax;
  const row = await db.query(
    "INSERT INTO orders(total) VALUES($1) RETURNING id", [total]);
  await stripe.charges.create({
    amount: Math.round(total * 100), source: req.body.token });
  res.json({ id: row.rows[0].id, total });
}
```

**After**
```typescript
async function createOrder(req: Request, res: Response) {
  const total = priceOrder(req.body.items);
  const id = await saveOrder(total);          // thin DB I/O wrapper
  await chargeCard(req.body.token, total);    // thin payment I/O wrapper
  res.json({ id, total });
}

function priceOrder(items: Item[]): number {
  const subtotal = items.reduce((s, it) => s + it.price * it.qty, 0);
  return subtotal + subtotal * TAX_RATE;
}
```

**Why:** The opposite pole: the before is a god-function blending domain pricing, DB I/O, payment I/O, and HTTP at three altitudes, so the split is driven by mixed concerns/cohesion — not by counting lines. priceOrder is a genuine independent abstraction (pure, testable, reusable). When-NOT guard: do not over-correct into trampolines — a cohesive 40-line handler doing one thing should NOT be chopped to hit a size limit, and the extracted piece must earn its name rather than just forwarding one obvious line.

---

## Replace Method with Method Object — Order.price -> PriceCalculator  ·  `typescript`  ·  ✅ sourced
Source: https://refactoring.guru/replace-method-with-method-object

**Before**
```typescript
class Order {
  // ...
  price(): number {
    let primaryBasePrice;
    let secondaryBasePrice;
    let tertiaryBasePrice;
    // Perform long computation.
  }
}
```

**After**
```typescript
class Order {
  // ...
  price(): number {
    return new PriceCalculator(this).compute();
  }
}

class PriceCalculator {
  private _primaryBasePrice: number;
  private _secondaryBasePrice: number;
  private _tertiaryBasePrice: number;

  constructor(order: Order) {
    // Copy relevant information from the
    // order object.
  }

  compute(): number {
    // Perform long computation.
  }
}
```

**Why:** The long price() method is one cohesive computation whose many tightly-coupled local variables make it grow; its size is a signal that the calculation deserves its own cohesive unit rather than being chopped by an arbitrary line limit or left tangled inside Order. After, the calculation lives in a PriceCalculator class sized exactly to that one responsibility — the boundary follows cohesion. When NOT to do it: do not promote a short method, or one whose locals do not tangle, into its own class — that adds a class with no cohesion gain and is needless ceremony.

_Verified: Fetched https://refactoring.guru/replace-method-with-method-object and the TypeScript example matches the candidate exactly. The 'before' shows class Order with price(): number declaring `let primaryBasePrice; let secondaryBasePrice; let tertiaryBasePrice;` followed by the `// Perform long computation.` placeholder. The 'after' shows Order.price() returning `new PriceCalculator(this).compute();`, plus a new PriceCalculator class with private _primaryBasePrice/_secondaryBasePrice/_tertiaryBasePrice fields, a constructor(order: Order) with a '// Copy relevant information from the order object.' comment, and compute(): number containing '// Perform long computation.'. Both the before and after snippets in the candidate JSON reproduce this verbatim. Verify hint confirmed._

---
