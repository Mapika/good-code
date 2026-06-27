# exhaustive-variant-handling

_Theme D: errors-and-validation_

## notification dispatch: silent else fall-through vs exhaustive switch  ·  `typescript`  ·  synthetic

**Before**
```typescript
type Notification =
  | { kind: 'email'; to: string }
  | { kind: 'sms'; phone: string }
  | { kind: 'push'; deviceId: string }

function render(n: Notification): string {
  if (n.kind === 'email') return `Email to ${n.to}`
  else if (n.kind === 'sms') return `SMS to ${n.phone}`
  else return `Push to ${n.deviceId}` // a future 'webhook' kind silently renders as a push
}
```

**After**
```typescript
function render(n: Notification): string {
  switch (n.kind) {
    case 'email': return `Email to ${n.to}`
    case 'sms':   return `SMS to ${n.phone}`
    case 'push':  return `Push to ${n.deviceId}`
    default: {
      const _exhaustive: never = n // compile error the moment a new kind is added
      throw new Error(`unhandled notification: ${JSON.stringify(_exhaustive)}`)
    }
  }
}
```

**Why:** Shows the TS-specific `never` trick turning 'I forgot a case' into a compile error instead of a silent wrong result. When-NOT: this is right because the channel set is closed and edited in one place; if channels were a third-party plugin registry where callers add handlers without touching render(), a registry/polymorphic dispatch would be the correct tool, not a switch.

---

## transaction settlement: defaulting else vs match + assert_never  ·  `python`  ·  synthetic

**Before**
```python
def settle(txn: Txn) -> Decimal:
    if txn.kind == "charge":
        return txn.amount
    elif txn.kind == "refund":
        return -txn.amount
    else:
        return Decimal(0)  # a new "chargeback" kind is silently settled as 0
```

**After**
```python
from typing import assert_never  # txn.kind: Literal['charge','refund','chargeback']

def settle(txn: Txn) -> Decimal:
    match txn.kind:
        case "charge":
            return txn.amount
        case "refund":
            return -txn.amount
        case "chargeback":
            return -txn.amount - txn.fee
        case _:
            assert_never(txn.kind)  # mypy/pyright error if any kind is unhandled
```

**Why:** Demonstrates that Python gets static exhaustiveness too via a Literal discriminant + typing.assert_never, replacing a catch-all else that swallows new kinds. When-NOT: appropriate because transaction kinds are a fixed, finite enum; if kinds were dynamically registered handlers (an open plugin set), a dispatch dict / Protocol-based polymorphism would be the right design instead of a closed match.

---

## pricing tiers: premature interface hierarchy vs enum switch  ·  `go`  ·  synthetic

**Before**
```go
// Premature polymorphism for two fixed, never-extended cases.
type Pricer interface{ Price(cents int64) int64 }
type Standard struct{}
func (Standard) Price(c int64) int64 { return c }
type Premium struct{}
func (Premium) Price(c int64) int64 { return c + c/10 }

func pricerFor(tier string) Pricer {
    if tier == "premium" { return Premium{} }
    return Standard{} // unknown tier silently priced as Standard
}
```

**After**
```go
type Tier int
const (
    Standard Tier = iota
    Premium
)

func price(t Tier, cents int64) (int64, error) {
    switch t {
    case Standard: return cents, nil
    case Premium:  return cents + cents/10, nil
    default:       return 0, fmt.Errorf("unhandled tier: %d", t)
    }
}
```

**Why:** Covers the other anti-pattern in 'replaces': a class/interface hierarchy + factory for two fixed cases is heavier and slower than a switch over an enum. The explicit default returning an error (paired with the `exhaustive` linter) is Go's stand-in for `never`, instead of silently defaulting. When-NOT: if pricing strategies were genuinely open and added by other packages without editing this function, the Pricer interface would be the correct, intentional use of polymorphism.

---
