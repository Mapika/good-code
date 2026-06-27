# match-surrounding-style

_Theme G: fitting-in-and-scope_

## new repo function ignores the module's session/domain-error idiom  ·  `python`  ·  synthetic

**Before**
```python
# neighbors: def get_user(session, id) -> User: ... raise NotFoundError(...); logger = logging.getLogger(__name__)
def get_order(order_id):
    conn = psycopg2.connect(DSN)            # neighbors take an injected session
    cur = conn.cursor()
    cur.execute("select * from orders where id=%s", (order_id,))
    row = cur.fetchone()
    if not row:
        print(f"order {order_id} not found")  # neighbors log + raise NotFoundError
        return None
    return {"id": row[0], "total": row[1]}      # neighbors return domain objects
```

**After**
```python
def get_order(session, order_id) -> Order:
    row = session.execute(
        select(Order).where(Order.id == order_id)
    ).scalar_one_or_none()
    if row is None:
        raise NotFoundError(f"order {order_id}")
    return row
```

**Why:** Mirrors the module's established idioms (injected session, ORM query, domain-object return, NotFoundError instead of print+None) so the added function is indistinguishable from its neighbors. When-not: matching is about local idioms, not terseness; if the surrounding pattern were genuinely unsafe you'd fix it deliberately across the scope, not copy it or silently add a third dialect.

---

## data-access fn imports promise-chain + snake_case into an async/AppError module  ·  `typescript`  ·  synthetic

**Before**
```typescript
// neighbors: export async function findUser(id: string): Promise<User> { ...; throw new AppError(`user ${id} not found`) }
export const get_invoice = (invoice_id: string) => {
  return db.select().from(invoices).where(eq(invoices.id, invoice_id))
    .then(rows => rows[0])
    .catch(err => { console.error(err); return null })  // neighbors await + throw AppError
}
```

**After**
```typescript
export async function getInvoice(invoiceId: string): Promise<Invoice> {
  const [row] = await db.select().from(invoices).where(eq(invoices.id, invoiceId))
  if (!row) throw new AppError(`invoice ${invoiceId} not found`)
  return row
}
```

**Why:** Conforms to the file's conventions: camelCase, async/await over .then/.catch chains, throwing AppError over swallow-and-return-null, and a typed Promise return matching siblings. When-not: blending in is not license to copy a harmful local pattern (e.g. if neighbors really did swallow errors, you'd fix that deliberately) and not an excuse to drop needed error handling for brevity.

---

## new Store method panics instead of returning wrapped errors like its neighbors  ·  `go`  ·  synthetic

**Before**
```go
// neighbors: func (s *Store) GetUser(ctx context.Context, id string) (*User, error) {
//   ... if err != nil { return nil, fmt.Errorf("get user %s: %w", id, err) } }
func (store *Store) GetOrder(orderId string) *Order {
    row := store.db.QueryRow("select id, total from orders where id = ?", orderId)
    var o Order
    if err := row.Scan(&o.ID, &o.Total); err != nil {
        panic("could not scan order: " + err.Error())  // neighbors return wrapped errors
    }
    return &o
}
```

**After**
```go
func (s *Store) GetOrder(ctx context.Context, id string) (*Order, error) {
    row := s.db.QueryRowContext(ctx, "select id, total from orders where id = ?", id)
    var o Order
    if err := row.Scan(&o.ID, &o.Total); err != nil {
        return nil, fmt.Errorf("get order %s: %w", id, err)
    }
    return &o, nil
}
```

**Why:** Adopts the package's idioms: short receiver s, ctx-first signature with QueryRowContext, idiomatic id, and error-as-value with %w wrapping instead of a foreign panic/exception idiom. When-not: this is mirroring a sound local convention, not minimalism; if every method in the package were (wrongly) panicking, you'd correct it deliberately rather than add yet another error style.

---
