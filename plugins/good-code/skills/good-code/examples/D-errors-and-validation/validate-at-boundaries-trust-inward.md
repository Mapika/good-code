# validate-at-boundaries-trust-inward

_Theme D: errors-and-validation_

## order handler re-checks shapes the parser already proved  ·  `typescript`  ·  synthetic

**Before**
```typescript
function applyDiscount(order: any): number {
  if (!order || typeof order.total !== "number" || order.total < 0) {
    throw new Error("invalid order");
  }
  if (!Array.isArray(order.items)) return order.total;
  return order.total * (order.items.length > 5 ? 0.9 : 1);
}

app.post("/orders", (req, res) => {
  const order = req.body;
  if (!order || typeof order.total !== "number") {
    return res.status(400).json({ error: "bad order" });
  }
  res.json({ total: applyDiscount(order) });
});
```

**After**
```typescript
const OrderInput = z.object({
  total: z.number().nonnegative(),
  items: z.array(z.object({ sku: z.string() })),
});
type OrderInput = z.infer<typeof OrderInput>;

function applyDiscount(order: OrderInput): number {
  return order.total * (order.items.length > 5 ? 0.9 : 1);
}

app.post("/orders", (req, res) => {
  const parsed = OrderInput.safeParse(req.body); // validate once at the edge
  if (!parsed.success) return res.status(400).json(parsed.error.flatten());
  res.json({ total: applyDiscount(parsed.data) });
});
```

**Why:** Shows untrusted body parsed once with Zod at the handler so applyDiscount takes the inferred type and never re-checks total/items shapes. Guards the opposite pole: the boundary check is not dropped, it is relocated into the schema; internal trust is earned by the type, not by convention.

---

## queue consumer re-validates a typed event in every helper  ·  `python`  ·  synthetic

**Before**
```python
def process_event(raw: dict) -> None:
    event = PaymentEvent(**raw)   # already typed
    settle(event)

def settle(event: PaymentEvent) -> None:
    if event is None:
        raise ValueError("no event")
    if not isinstance(event.amount_cents, int) or event.amount_cents <= 0:
        raise ValueError("bad amount")
    if not event.currency:
        raise ValueError("bad currency")
    ledger.credit(event.amount_cents, event.currency)
```

**After**
```python
class PaymentEvent(BaseModel):
    amount_cents: PositiveInt                       # range enforced at parse time
    currency: constr(min_length=3, max_length=3)

def consume(raw: dict) -> None:
    settle(PaymentEvent.model_validate(raw))        # validate once at the edge

def settle(event: PaymentEvent) -> None:
    ledger.credit(event.amount_cents, event.currency)   # trust the typed value
```

**Why:** Moves the amount/currency invariants onto the model so the consumer edge validates once and settle trusts the value instead of repeating None/isinstance/range guards. Guards the when-not: validation is kept (in the model), not deleted, and a truly impossible internal state could still justify an assert rather than this defensive bloat.

---

## every helper nil-checks a struct decoded at the handler  ·  `go`  ·  synthetic

**Before**
```go
func createUser(w http.ResponseWriter, r *http.Request) {
    var u User
    json.NewDecoder(r.Body).Decode(&u)
    save(&u)
}

func save(u *User) error {
    if u == nil {
        return errors.New("nil user")
    }
    if u.Email == "" {
        return errors.New("empty email")
    }
    if u.Age < 0 {
        return errors.New("negative age")
    }
    return db.Insert(u)
}
```

**After**
```go
func createUser(w http.ResponseWriter, r *http.Request) {
    var u User
    if err := json.NewDecoder(r.Body).Decode(&u); err != nil {
        http.Error(w, "invalid body", http.StatusBadRequest)
        return
    }
    if err := u.Validate(); err != nil { // validate once at the boundary
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }
    if err := save(u); err != nil {
        http.Error(w, "internal error", http.StatusInternalServerError)
    }
}

func save(u User) error {
    return db.Insert(u) // value, already validated: no nil/empty/range re-checks
}
```

**Why:** A single u.Validate() at the handler plus a value (non-pointer) receiver removes the scattered nil/empty/range guards in save. Guards the opposite pole: the decode-error handling and the boundary Validate are kept; only the redundant inward re-checks the type and prior validation already guarantee are removed.

---
