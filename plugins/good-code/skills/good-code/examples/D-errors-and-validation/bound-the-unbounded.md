# bound-the-unbounded

_Theme D: errors-and-validation_

## unbounded job poll loop hangs the request  ·  `python`  ·  synthetic

**Before**
```python
def wait_for_export(job_id):
    done = False
    while not done:  # no cap; spins forever if upstream never finishes
        resp = client.get(f"/exports/{job_id}")
        if resp.json()["state"] == "ready":
            done = True
            return resp.json()["url"]
        time.sleep(2)
```

**After**
```python
MAX_POLLS = 60  # ~2 min at 2s; export SLA is 90s

def wait_for_export(job_id: str) -> str:
    for _ in range(MAX_POLLS):
        resp = client.get(f"/exports/{job_id}")
        if resp.json()["state"] == "ready":
            return resp.json()["url"]
        time.sleep(2)
    raise TimeoutError(f"export {job_id} not ready after {MAX_POLLS} polls")
```

**Why:** Replaces an open-ended `while not done` poll that depends on the upstream behaving with a bounded loop that fails loudly when exhausted. when-NOT: the cap is derived from the real SLA (operating envelope), and it adds exactly one bound rather than carpeting the function with assertions for impossible states.

---

## cursor pagination trusts upstream to terminate  ·  `typescript`  ·  synthetic

**Before**
```typescript
async function fetchAllContacts(): Promise<Contact[]> {
  const all: Contact[] = [];
  let cursor: string | undefined;
  do {
    const page = await api.contacts.list({ cursor }); // unbounded
    all.push(...page.items);
    cursor = page.nextCursor;
  } while (cursor);
  return all;
}
```

**After**
```typescript
const MAX_PAGES = 500; // 500 * 100/page = 50k, above tenant ceiling

async function fetchAllContacts(): Promise<Contact[]> {
  const all: Contact[] = [];
  let cursor: string | undefined;
  for (let page = 0; page < MAX_PAGES; page++) {
    const res = await api.contacts.list({ cursor });
    all.push(...res.items);
    if (!res.nextCursor) return all;
    cursor = res.nextCursor;
  }
  throw new Error(`pagination exceeded ${MAX_PAGES} pages; cursor likely looping`);
}
```

**Why:** Bounds a pagination fan-out whose accumulator would OOM the process if a buggy or looping cursor never ends. when-NOT: the cap is set above the legitimate data ceiling so it never truncates real paging — it trips only on a genuine bug and fails loudly instead of silently returning a partial list.

---

## infinite reconnect loop blocks the caller  ·  `go`  ·  synthetic

**Before**
```go
func publish(ctx context.Context, msg []byte) error {
    for { // retries forever; a permanently-down broker hangs the caller
        if err := broker.Send(ctx, msg); err == nil {
            return nil
        }
        time.Sleep(time.Second)
    }
}
```

**After**
```go
const maxAttempts = 5

func publish(ctx context.Context, msg []byte) error {
    var err error
    for attempt := 0; attempt < maxAttempts; attempt++ {
        if err = broker.Send(ctx, msg); err == nil {
            return nil
        }
        time.Sleep(time.Second << attempt) // exponential backoff
    }
    return fmt.Errorf("publish failed after %d attempts: %w", maxAttempts, err)
}
```

**Why:** Replaces an unbounded `for {}` retry with a bounded one that surfaces the last error via %w, the Go error-as-value idiom. when-NOT: it bounds the retry count only and propagates the real failure — no assertion noise for impossible states, and the legitimate work itself is not capped.

---
