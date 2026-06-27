# minimal-public-surface

_Theme C: abstraction-discipline_

## API route exports a single-use DTO mapper  ·  `typescript`  ·  synthetic

**Before**
```typescript
// routes/users.ts
export const toUserDTO = (row: UserRow) => ({
  id: row.id,
  name: row.full_name,
  joinedAt: row.created_at.toISOString(),
})

export async function getUser(req: Request, res: Response) {
  const row = await db.users.findById(req.params.id)
  res.json(toUserDTO(row)) // toUserDTO is only ever used in this file
}
```

**After**
```typescript
// routes/users.ts
function toUserDTO(row: UserRow) {
  return {
    id: row.id,
    name: row.full_name,
    joinedAt: row.created_at.toISOString(),
  }
}

export async function getUser(req: Request, res: Response) {
  const row = await db.users.findById(req.params.id)
  res.json(toUserDTO(row)) // local helper; export only when a second module imports it
}
```

**Why:** Shows keeping a single-use mapper file-local instead of exporting it speculatively, plus the TS form: top-level `function` over an exported arrow const (better stack traces/hoisting). When-NOT: getUser stays exported because the router genuinely imports it - that is the module's real contract, so do not hide it.

---

## Data-access package exports an internal row scanner  ·  `go`  ·  synthetic

**Before**
```go
package store

// ScanOrder is only called inside this package.
func ScanOrder(r *sql.Row) (Order, error) {
	var o Order
	return o, r.Scan(&o.ID, &o.TotalCents)
}

func GetOrder(db *sql.DB, id string) (Order, error) {
	return ScanOrder(db.QueryRow(
		"select id, total_cents from orders where id = $1", id))
}
```

**After**
```go
package store

func scanOrder(r *sql.Row) (Order, error) {
	var o Order
	return o, r.Scan(&o.ID, &o.TotalCents)
}

// GetOrder is the package's entry point; callers import only this.
func GetOrder(db *sql.DB, id string) (Order, error) {
	return scanOrder(db.QueryRow(
		"select id, total_cents from orders where id = $1", id))
}
```

**Why:** Uses Go's capitalization-based visibility: the row scanner is unexported (lower-case) since nothing outside the package uses it, narrowing the package surface to GetOrder. When-NOT: GetOrder remains exported as the deliberate package contract - do not unexport symbols other packages legitimately consume just to chase minimalism.

---

## ETL config module leaks its parsing helper into the public API  ·  `python`  ·  synthetic

**Before**
```python
# etl/config.py
def parse_duration(raw: str) -> int:   # used only below
    return int(raw.rstrip("s"))

def load_config(path: str) -> Config:
    data = json.loads(Path(path).read_text())
    return Config(timeout=parse_duration(data["timeout"]))
```

**After**
```python
# etl/config.py
__all__ = ["load_config"]

def _parse_duration(raw: str) -> int:  # underscore: not part of the module's API
    return int(raw.rstrip("s"))

def load_config(path: str) -> Config:
    data = json.loads(Path(path).read_text())
    return Config(timeout=_parse_duration(data["timeout"]))
```

**Why:** Uses Python's conventions (leading underscore + `__all__`) to keep a single-use helper out of the module's public surface, signalling callers should not depend on it. When-NOT: load_config stays public (no underscore, listed in __all__) because it is the documented contract other modules import - do not underscore-hide symbols that are genuinely consumed elsewhere.

---
