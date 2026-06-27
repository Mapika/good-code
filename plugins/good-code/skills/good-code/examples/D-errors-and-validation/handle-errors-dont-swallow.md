# handle-errors-dont-swallow

_Theme D: errors-and-validation_

## data-access default hides DB failure  ·  `python`  ·  synthetic

**Before**
```python
def get_user(user_id: int) -> User | None:
    try:
        row = db.execute(
            "select * from users where id = %s", (user_id,)
        ).fetchone()
        return User.from_row(row)
    except Exception:
        return None   # 'not found' and 'db is down' look identical to callers
```

**After**
```python
def get_user(user_id: int) -> User | None:
    row = db.execute(
        "select * from users where id = %s", (user_id,)
    ).fetchone()
    if row is None:
        return None              # genuinely absent: a normal result, not an error
    return User.from_row(row)    # connection/query errors propagate to the handler
```

**Why:** Demonstrates removing a default-that-hides-failure: the benign 'no such row' case stays a normal None, while real infra errors propagate to one boundary handler instead of being swallowed. Guards the when_not: it does NOT add a try/except just to log-and-rethrow, and does NOT catch broad Exception to keep going.

---

## discarded error returns in config load  ·  `go`  ·  synthetic

**Before**
```go
func loadConfig(path string) Config {
    data, _ := os.ReadFile(path)   // ignores missing file / permission error
    var cfg Config
    json.Unmarshal(data, &cfg)     // ignores malformed JSON
    return cfg                     // silently returns a zero/partial config
}
```

**After**
```go
func loadConfig(path string) (Config, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return Config{}, fmt.Errorf("read config %s: %w", path, err)
    }
    var cfg Config
    if err := json.Unmarshal(data, &cfg); err != nil {
        return Config{}, fmt.Errorf("parse config %s: %w", path, err)
    }
    return cfg, nil
}
```

**Why:** Demonstrates not discarding error returns (the `_` idiom) and instead adding context with %w before propagating, so a bad config fails loudly at startup rather than booting with empty values. Guards the when_not: each error is wrapped exactly once and returned (no log-then-return double handling), with no blanket recover-to-continue.

---

## empty catch returns a misleading fallback  ·  `typescript`  ·  synthetic

**Before**
```typescript
async function getInventory(sku: string): Promise<number> {
  try {
    const res = await fetch(`${API}/inventory/${sku}`);
    return (await res.json()).count;
  } catch (e) {
    return 0;   // a network/5xx error looks identical to 'out of stock'
  }
}
```

**After**
```typescript
async function getInventory(sku: string): Promise<number> {
  const res = await fetch(`${API}/inventory/${sku}`);
  if (res.status === 404) return 0;   // genuinely unstocked: a real answer
  if (!res.ok) {
    throw new Error(`inventory lookup failed for ${sku}: ${res.status}`);
  }
  return (await res.json()).count;
}
```

**Why:** Demonstrates distinguishing a benign domain result (404 -> 0 stock) from an infra failure (throw), replacing an empty catch that returned a hiding default. Guards the when_not: it does not catch-log-rethrow at the call site; the throw propagates to the framework's central error middleware, which handles it once.

---
