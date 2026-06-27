# types-at-boundaries-no-escape-hatches

_Theme F: naming-and-clarity_

## API handler: `as` cast + parallel interface that drifts  ·  `typescript`  ·  synthetic

**Before**
```typescript
// hand-maintained type, separate from any validation -> silently drifts
interface CreateUser {
  email: string
  age: number
}

router.post("/users", async (req, res) => {
  const input = req.body as CreateUser   // cast asserts a shape nothing checks
  const user = await db.users.create(input)
  res.json(user)
})
```

**After**
```typescript
const CreateUser = z.object({
  email: z.string().email(),
  age: z.number().int().min(0),
})
type CreateUser = z.infer<typeof CreateUser>   // single source of truth

router.post("/users", async (req, res) => {
  const input = CreateUser.parse(req.body)     // validated at boundary -> typed
  const user = await db.users.create(input)
  res.json(user)
})
```

**Why:** Shows deriving the type from the schema (no parallel interface to drift) and replacing `as` (which asserts a shape the runtime never verifies) with boundary parsing. When-NOT: don't re-parse already-trusted values on every internal hop, and keep passing the concrete typed `input` inward rather than re-validating it.

---

## Webhook handler: cast(dict[str, Any]) + over-annotated locals  ·  `python`  ·  synthetic

**Before**
```python
def handle_payment(body: bytes) -> dict[str, Any]:
    data = cast(dict[str, Any], json.loads(body))  # cast asserts shape, checks nothing
    user_id: str = data["user_id"]                 # over-annotated local; KeyError at runtime
    amount: int = int(data["amount_cents"])
    return {"charged": charge(user_id, amount)}
```

**After**
```python
class Payment(BaseModel):
    user_id: str
    amount_cents: int

def handle_payment(body: bytes) -> ChargeResult:
    payment = Payment.model_validate_json(body)   # parse at boundary -> typed
    return charge(payment.user_id, payment.amount_cents)
```

**Why:** Replaces an unchecked `cast` (an escape hatch that lies to the checker) with real boundary validation, and lets inference carry the obvious `payment` local instead of annotating it. When-NOT: don't add a Pydantic model for data your own code already produced and trusts, and keep the public signature annotated (the boundary) even as you drop ceremony on locals.

---

## Config loader: non-null `!` silencing string | undefined  ·  `typescript`  ·  synthetic

**Before**
```typescript
function loadConfig(): Config {
  const url = process.env.DATABASE_URL!        // ! hides string | undefined
  const port = Number(process.env.PORT!)       // NaN if unset, no error
  return { url, port }
}
```

**After**
```typescript
function loadConfig(): Config {
  const url = process.env.DATABASE_URL
  if (!url) throw new Error("DATABASE_URL is required")  // check at the edge
  const port = Number(process.env.PORT ?? "8080")
  return { url, port }
}
```

**Why:** Demonstrates replacing the non-null `!` escape hatch with a real runtime check at the config boundary, where the value genuinely can be absent. When-NOT: at a provably-safe library edge a cast is acceptable if paired with an assertion and a justifying comment; the point is env vars are not that edge, so check them.

---
