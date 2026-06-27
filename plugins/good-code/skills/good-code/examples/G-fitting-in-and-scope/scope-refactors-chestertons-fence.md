# scope-refactors-chestertons-fence

_Theme G: fitting-in-and-scope_

## ETL export drops a guard it didn't understand  ·  `python`  ·  synthetic

**Before**
```python
# task: add `region` to the exported row
def export_rows(records):
    # agent also rewrote the loop into a comprehension and removed the ts==0 skip
    return [
        {"id": r.id, "amount": r.amount, "region": r.region}
        for r in records
    ]
```

**After**
```python
# task: add `region` to the exported row -> add exactly that
def export_rows(records):
    out = []
    for r in records:
        # Vendor sends ts=0 for backfilled rows; exporting them double-counts (DATA-712).
        if r.ts == 0:
            continue
        out.append({"id": r.id, "amount": r.amount, "region": r.region})
    return out
```

**Why:** Shows Chesterton's fence: the ts==0 skip looks redundant but is a paid-for bug fix, so a one-field task must add the field and leave it. when_not: if the task were explicitly 'clean up export_rows', rewriting the loop and re-justifying the guard would be legitimate, not scope creep.

---

## const bump silently deletes 429/Retry-After branch  ·  `go`  ·  synthetic

**Before**
```go
const maxAttempts = 5 // was 3

func doWithRetry(req *http.Request) (*http.Response, error) {
    // agent also "simplified" the loop, dropping the 429/Retry-After branch
    for attempt := 0; attempt < maxAttempts; attempt++ {
        resp, err := client.Do(req)
        if err == nil {
            return resp, nil
        }
        time.Sleep(backoff(attempt))
    }
    return nil, errExhausted
}
```

**After**
```go
const maxAttempts = 5 // was 3 -- the only change the task asked for

func doWithRetry(req *http.Request) (*http.Response, error) {
    for attempt := 0; attempt < maxAttempts; attempt++ {
        resp, err := client.Do(req)
        if err == nil && resp.StatusCode != http.StatusTooManyRequests {
            return resp, nil
        }
        // Upstream 429s are spurious under load; honor Retry-After (INC-481).
        sleep := backoff(attempt)
        if resp != nil && resp.StatusCode == http.StatusTooManyRequests {
            sleep = retryAfter(resp)
        }
        time.Sleep(sleep)
    }
    return nil, errExhausted
}
```

**Why:** A one-line config change (3->5) should not touch the retry body; deleting the 429 special-case is removing a fence whose purpose (a real outage workaround) wasn't understood. when_not: if reviewers had confirmed the 429 handling is now dead/wrong and the task covered the retry path, removing it deliberately would be fine.

---

## one-field add churns the whole handler  ·  `typescript`  ·  synthetic

**Before**
```typescript
// task: add `phone` to the update payload
export const updateUser = async (request: Request, response: Response) => {
  const payload = request.body                       // renamed u -> payload
  const errors = validate(payload)                   // new validator nobody asked for
  if (errors.length) return response.status(422).json({ errors }) // changed 400 -> 422
  try {                                               // wrapped in unrequested try/catch
    const result = await repo.save({ name: payload.name, email: payload.email, phone: payload.phone })
    return response.status(200).json(result)
  } catch (e) { return response.status(500).json({ error: String(e) }) }
}
```

**After**
```typescript
// task: add `phone` to the update payload -> add exactly that
export async function updateUser(req: Request, res: Response) {
  const u = req.body
  if (!u.email) return res.status(400).json({ error: "email required" })
  const saved = await repo.save({ name: u.name, email: u.email, phone: u.phone })
  return res.json(saved)
}
```

**Why:** Demonstrates scope discipline: the only needed edit is `phone`, so renaming locals, swapping 400->422, adding a validator, and wrapping in try/catch is diff-inflating scope creep that hides the real change in review. when_not: if those were genuine defects in the direct path of the change (e.g. the handler truly lacked validation), fixing them deliberately and calling it out would be warranted.

---
