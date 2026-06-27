# information-hiding-stable-boundaries

_Theme G: fitting-in-and-scope_

## repository returns ORM model, leaking *_cents schema to HTTP layer  ·  `python`  ·  synthetic

**Before**
```python
class OrderModel(Base):              # SQLAlchemy table mapping
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    total_cents = Column(Integer)
    internal_version = Column(Integer)

def get_order(order_id: int) -> OrderModel:
    return session.get(OrderModel, order_id)   # raw ORM row goes up the stack

# routes.py now depends on the column layout:
#   o = get_order(id)
#   return {"id": o.id, "total": o.total_cents / 100}
```

**After**
```python
@dataclass(frozen=True)
class Order:
    id: int
    total: Decimal

def get_order(order_id: int) -> Order:
    row = session.get(OrderModel, order_id)
    return Order(id=row.id, total=Decimal(row.total_cents) / 100)

# routes.py depends only on Order.total; the cents storage choice
# and internal_version stay hidden inside the repository.
```

**Why:** Shows mapping the ORM row into a domain Order at the repository boundary so the storage unit (cents) and internal columns don't leak to the HTTP layer. When-NOT: inside the data-access module you may pass OrderModel around freely; don't add this dataclass+mapping where there is no real boundary to protect.

---

## service returns raw DB row, leaking password_hash and snake_case columns  ·  `typescript`  ·  synthetic

**Before**
```typescript
// userService.ts — hands the raw DB row straight to the API layer
export async function getUser(id: string) {
  return db.query.users.findFirst({ where: eq(users.id, id) });
  // row: { id, email, password_hash, stripe_customer_id, created_at }
}

// route.ts
app.get("/users/:id", async (req, res) => {
  res.json(await getUser(req.params.id)); // leaks password_hash + schema to the wire
});
```

**After**
```typescript
export interface User {
  id: string;
  email: string;
  createdAt: Date;
}

export async function getUser(id: string): Promise<User | null> {
  const row = await db.query.users.findFirst({ where: eq(users.id, id) });
  if (!row) return null;
  return { id: row.id, email: row.email, createdAt: row.created_at };
}
```

**Why:** Returning a domain User hides the table layout and keeps secrets (password_hash) and storage-shaped names off the boundary, so a column rename doesn't ripple into routes. When-NOT: helpers living inside userService.ts can share the row type directly; don't mint a DTO per function where the row never crosses a module boundary.

---

## repository returns sql.NullString driver types across its boundary  ·  `go`  ·  synthetic

**Before**
```go
// Leaks database/sql driver types out of the repository.
type UserRow struct {
    ID        int64
    Email     string
    AvatarURL sql.NullString
    DeletedAt sql.NullTime
}

func (r *Repo) GetUser(ctx context.Context, id int64) (UserRow, error) {
    var u UserRow
    err := r.db.QueryRowContext(ctx,
        `SELECT id, email, avatar_url, deleted_at FROM users WHERE id=$1`, id).
        Scan(&u.ID, &u.Email, &u.AvatarURL, &u.DeletedAt)
    return u, err // every caller must understand sql.NullString
}
```

**After**
```go
type User struct {
    ID        int64
    Email     string
    AvatarURL string // "" when absent
}

func (r *Repo) GetUser(ctx context.Context, id int64) (User, error) {
    var (
        u      User
        avatar sql.NullString
    )
    err := r.db.QueryRowContext(ctx,
        `SELECT id, email, avatar_url FROM users WHERE id=$1`, id).
        Scan(&u.ID, &u.Email, &avatar)
    u.AvatarURL = avatar.String
    return u, err
}
```

**Why:** The domain User exposes plain Go types and keeps database/sql driver types (sql.NullString/NullTime) and soft-delete columns inside the repo, so callers aren't coupled to the storage layer. When-NOT: an unexported scan helper used only within the data-access package can keep the NullString form; the mapping earns its place only at the exported boundary.

---

## Refactoring.Guru: Encapsulate Field  ·  `typescript`  ·  ✅ sourced
Source: https://refactoring.guru/encapsulate-field

**Before**
```typescript
class Person {
  name: string;
}
```

**After**
```typescript
class Person {
  private _name: string;

  get name() {
    return this._name;
  }
  setName(arg: string): void {
    this._name = arg;
  }
}
```

**Why:** Demonstrates hiding internal representation behind a stable boundary: a public mutable field becomes a `private _name` accessed only through a getter/setter, so callers depend on the accessor contract rather than the raw field, letting you add validation or change storage without breaking them. When-NOT: for plain immutable data carriers / DTOs where there is no invariant to protect, wrapping every field in accessors adds ceremony without buying real encapsulation.

_Verified: Fetched https://refactoring.guru/encapsulate-field. The TypeScript tab shows exactly the claimed Before and After. Before: `class Person { name: string; }`. After: `class Person { private _name: string; get name() { return this._name; } setName(arg: string): void { this._name = arg; } }`. This matches the candidate's before/after byte-for-byte and satisfies the verify_hint (private _name field, get name() returning this._name, and setName(arg: string): void). Other language tabs (Java, C#) on the page differ in style but the TypeScript example is genuinely present as described._

---
