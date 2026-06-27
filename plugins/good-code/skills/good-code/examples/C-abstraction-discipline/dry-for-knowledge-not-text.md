# dry-for-knowledge-not-text

_Theme C: abstraction-discipline_

## sales-tax rule cloned across checkout and quote endpoints drifts  ·  `python`  ·  synthetic

**Before**
```python
# routes/checkout.py
def create_order(cart):
    subtotal = sum(i.price * i.qty for i in cart.items)
    total = subtotal + subtotal * Decimal("0.08")        # CA sales tax
    return Order(total=total.quantize(Decimal("0.01")))

# routes/quote.py  -- copy bumped to 8.25% here only; checkout still charges 8%
def preview_quote(cart):
    subtotal = sum(i.price * i.qty for i in cart.items)
    total = subtotal + subtotal * Decimal("0.0825")
    return Quote(total=total.quantize(Decimal("0.01")))
```

**After**
```python
SALES_TAX_RATE = Decimal("0.0825")  # CA, see FIN-204

def order_total(cart) -> Decimal:
    subtotal = sum(i.price * i.qty for i in cart.items)
    return (subtotal * (1 + SALES_TAX_RATE)).quantize(Decimal("0.01"))

def create_order(cart):
    return Order(total=order_total(cart))

def preview_quote(cart):
    return Quote(total=order_total(cart))
```

**Why:** The tax rate is one business rule that must change in lockstep across charging and quoting; the cloned copy drifted so customers were quoted 8.25% but charged 8% — the exact 'bug fixed in one copy survives in the other' failure. Guard against the opposite pole: unify the shared rule, not the two subtotal loops if they merely looked alike while summing unrelated quantities.

---

## HMAC canonical signing string duplicated, signer and verifier drift apart  ·  `typescript`  ·  synthetic

**Before**
```typescript
// sign.ts
function signRequest(req: ApiRequest, secret: string): string {
  const base = `${req.method}\n${req.path}\n${req.timestamp}`;
  return hmac(secret, base);
}

// verify.ts  -- someone appended body to the canonical string here only
function verifyRequest(req: ApiRequest, secret: string, sig: string): boolean {
  const base = `${req.method}\n${req.path}\n${req.timestamp}\n${req.body}`;
  return hmac(secret, base) === sig;
}
```

**After**
```typescript
// one canonical signing string both sides must agree on
function canonicalString(req: ApiRequest): string {
  return [req.method, req.path, req.timestamp, req.body].join("\n");
}

export function signRequest(req: ApiRequest, secret: string): string {
  return hmac(secret, canonicalString(req));
}

export function verifyRequest(req: ApiRequest, secret: string, sig: string): boolean {
  return hmac(secret, canonicalString(req)) === sig;
}
```

**Why:** The canonical signing format is a wire contract the two sides must compute byte-for-byte identically; duplicating it let verify add `body` while sign did not, silently rejecting every valid request. This is knowledge that must change in lockstep — the right place to DRY. It would be wrong to instead merge two serializers that coincidentally join a few fields but encode different messages.

---

## two coincidentally-similar validators merged behind a generic helper  ·  `go`  ·  synthetic

**Before**
```go
// Merged because both were "3-20 alphanumeric" today — but they are
// independent rules that will diverge (coupons will allow '-', usernames
// get a reserved-word check). Every future change now risks both callers.
func validateField(s string, min, max int) error {
    if len(s) < min || len(s) > max {
        return fmt.Errorf("length must be %d-%d", min, max)
    }
    return mustBeAlphanumeric(s)
}
// callers: validateField(username, 3, 20); validateField(coupon, 3, 20)
```

**After**
```go
func validateUsername(s string) error {
    if len(s) < 3 || len(s) > 20 {
        return errors.New("username must be 3-20 chars")
    }
    return mustBeAlphanumeric(s) // share only the genuinely-common check
}

func validateCoupon(s string) error {
    if len(s) < 3 || len(s) > 20 {
        return errors.New("coupon must be 3-20 chars")
    }
    return mustBeAlphanumeric(s)
}
```

**Why:** Demonstrates the when-not pole: the two rules only resemble each other today, so merging them behind a flag/param helper couples callers that will diverge (a little copying beats a little coupling). It still unifies the one piece of real shared knowledge — the alphanumeric check — showing DRY targets knowledge, not text. If instead both fields shared one canonical 'slug' format, that single rule SHOULD be unified.

---
