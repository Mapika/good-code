# deep-modules-no-passthrough

_Theme B: function-and-module-shape_

## passthrough variable threaded through a constructor  ·  `typescript`  ·  ✅ sourced
Source: https://github.com/puppeteer/puppeteer/pull/5826/files#diff-Target.ts

**Before**
```typescript
import { TaskQueue } from './TaskQueue';

export class Target {
  _screenshotTaskQueue: TaskQueue;
  constructor(
    targetInfo: TargetInfo,
    browserContext: BrowserContext,
    sessionFactory: () => Promise<CDPSession>,
    ignoreHTTPSErrors: boolean,
    defaultViewport: Viewport | null,
    screenshotTaskQueue: TaskQueue,   // Target never uses it; only forwards it
  ) {
    this._screenshotTaskQueue = screenshotTaskQueue;
  }
  // ...page creation forwards it on:
  // Page.create(client, this, this._ignoreHTTPSErrors,
  //             this._defaultViewport, this._screenshotTaskQueue);
}
```

**After**
```typescript
export class Target {
  constructor(
    targetInfo: TargetInfo,
    browserContext: BrowserContext,
    sessionFactory: () => Promise<CDPSession>,
    ignoreHTTPSErrors: boolean,
    defaultViewport: Viewport | null,
  ) {}
  // Page now owns its own screenshot queue, so Target no longer
  // accepts, stores, or forwards it:
  // Page.create(client, this, this._ignoreHTTPSErrors, this._defaultViewport);
}
```

**Why:** Real puppeteer refactor deleting a pass-through variable: Target accepted, stored, and forwarded screenshotTaskQueue purely to hand it to Page, hiding nothing while widening every signature on the path. When-NOT: if Target actually used the queue (e.g. to serialize screenshots across its pages) the parameter would earn its place — only delete a dependency a layer genuinely consumes, not one it transforms or owns.

_Verified: Fetched puppeteer PR #5826 patch (via 5826.patch and patch-diff raw .diff). The src/Target.ts diff shows: import { TaskQueue } from './TaskQueue'; removed; the _screenshotTaskQueue: TaskQueue field declaration removed; the screenshotTaskQueue: TaskQueue constructor parameter removed; the this._screenshotTaskQueue = screenshotTaskQueue assignment removed; and the this._screenshotTaskQueue argument dropped from the Page.create(...) call (Page.create now ends at this._defaultViewport). src/TaskQueue.ts is deleted ('delete mode 100644 src/TaskQueue.ts', -34 lines). The task queue moved into src/Page.ts as an inline ScreenshotTaskQueue, so Target indeed only forwarded it and never used it. before/after snippets accurately represent the actual change._

---

## ceremonial service wrapping a repository 1:1  ·  `python`  ·  synthetic

**Before**
```python
class InvoiceService:
    def __init__(self, repo: InvoiceRepository):
        self._repo = repo

    def get_invoice(self, invoice_id: str) -> Invoice:
        return self._repo.get_invoice(invoice_id)

    def list_invoices(self, customer_id: str) -> list[Invoice]:
        return self._repo.list_invoices(customer_id)

    def delete_invoice(self, invoice_id: str) -> None:
        return self._repo.delete_invoice(invoice_id)
```

**After**
```python
# Plain reads/deletes call the repository directly — no wrapper earns its keep.
# Keep a service method only where it adds real behavior:
class InvoiceService:
    def __init__(self, repo: InvoiceRepository, audit: AuditLog):
        self._repo = repo
        self._audit = audit

    def void_invoice(self, invoice_id: str, reason: str) -> Invoice:
        with self._repo.transaction():
            invoice = self._repo.get_invoice(invoice_id)
            invoice.mark_void(reason)
            self._repo.save(invoice)
            self._audit.record("invoice.void", invoice_id, reason)
        return invoice
```

**Why:** Demonstrates collapsing a shallow service whose interface mirrors the repo method-for-method and hides no complexity (classitis / middle-man); callers should use the repo directly for trivial forwards. When-NOT: the kept `void_invoice` shows the layer is justified the moment it does real work — wrapping the mutation in a transaction, applying a domain state change, and writing an audit record. Thinness, not layer count, is the test; do not delete a layer that adds authz/transactions/mapping.

---

## single-impl interface 'for mocking' plus forwarding service  ·  `go`  ·  synthetic

**Before**
```go
// Interface defined on the implementer side purely "for mocking",
// with one production implementation and a service that just forwards.
type UserStore interface {
    GetUser(ctx context.Context, id string) (*User, error)
}

type UserService struct{ store UserStore }

func (s *UserService) GetUser(ctx context.Context, id string) (*User, error) {
    return s.store.GetUser(ctx, id) // adds nothing
}
```

**After**
```go
// No speculative interface, no forwarding layer: handlers use the concrete
// repo, whose method is itself deep (tiny signature hiding the SQL).
type UserRepo struct{ db *sql.DB }

func (r *UserRepo) GetUser(ctx context.Context, id string) (*User, error) {
    var u User
    err := r.db.QueryRowContext(ctx,
        "SELECT id, email FROM users WHERE id = $1", id).Scan(&u.ID, &u.Email)
    if err != nil {
        return nil, fmt.Errorf("get user %s: %w", id, err)
    }
    return &u, nil
}
```

**Why:** Targets the Go classitis the rule names: a single-method interface introduced before any second implementation plus a service struct that only re-exports the repo's signature. When-NOT: this is not a ban on interfaces — when a real second backend or a genuine test seam appears, define a narrow `Getter` interface at the consumer that needs it (accept-interfaces, return concrete), which transforms the dependency rather than merely forwarding it.

---
