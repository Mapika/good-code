# reuse-stdlib-and-existing-utilities

_Theme E: reuse-and-idiom_

## ETL: hand-rolled bucket-by-key vs collections.defaultdict  ·  `python`  ·  synthetic

**Before**
```python
def group_orders_by_customer(orders):
    groups = {}
    for order in orders:
        if order.customer_id not in groups:
            groups[order.customer_id] = []
        groups[order.customer_id].append(order)
    return groups
```

**After**
```python
from collections import defaultdict

def group_orders_by_customer(orders):
    groups = defaultdict(list)
    for order in orders:
        groups[order.customer_id].append(order)
    return dict(groups)
```

**Why:** Demonstrates reaching for collections.defaultdict, the canonical bucket-by-key tool, instead of the hand-written `if key not in dict` dance. When-NOT: the `dict(groups)` cast is deliberate — leaking a live defaultdict upward auto-vivifies keys on later reads, so don't blindly return it, and if callers must distinguish 'seen-but-empty' from 'never-seen' keep an explicit form; the goal is the right built-in, not the tersest one.

---

## Outbound API call: hand-built query string vs URLSearchParams  ·  `typescript`  ·  synthetic

**Before**
```typescript
function buildSearchUrl(base: string, params: Record<string, string>): string {
  let query = "";
  for (const key of Object.keys(params)) {
    query += (query ? "&" : "") + key + "=" + params[key];
  }
  return `${base}?${query}`;
}
```

**After**
```typescript
function buildSearchUrl(base: string, params: Record<string, string>): string {
  const query = new URLSearchParams(params);
  return `${base}?${query}`;
}
```

**Why:** Reuses the platform URLSearchParams built-in, which also percent-encodes keys and values — the manual concatenation silently corrupts the URL when a value contains `&`, `=`, or spaces (a real correctness/injection bug). When-NOT: don't pull a `query-string` npm dependency for this, and if you genuinely need a non-standard separator or duplicate-key ordering the API doesn't provide, a manual builder is justified — reuse the built-in only because it actually fits.

---

## HTTP client: hand-rolled read loop vs io.ReadAll  ·  `go`  ·  synthetic

**Before**
```go
func fetchPayload(url string) ([]byte, error) {
    resp, err := http.Get(url)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    var buf bytes.Buffer
    chunk := make([]byte, 4096)
    for {
        n, err := resp.Body.Read(chunk)
        buf.Write(chunk[:n])
        if err == io.EOF {
            break
        }
        if err != nil {
            return nil, err
        }
    }
    return buf.Bytes(), nil
}
```

**After**
```go
func fetchPayload(url string) ([]byte, error) {
    resp, err := http.Get(url)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    return io.ReadAll(resp.Body)
}
```

**Why:** io.ReadAll is the stdlib one-liner for draining a reader; the hand-rolled loop is easy to get subtly wrong (it already writes chunk[:n] before checking err and re-shadows err). When-NOT: this is reuse-the-right-tool, not reuse-no-tool — for untrusted upstreams, bound it with `io.ReadAll(io.LimitReader(resp.Body, maxBytes))` rather than an unbounded read; don't swing to a naked ReadAll that can OOM the service.

---
