# comment-why-not-what

_Theme A: comments-and-docs_

## webhook handler: narrated lines vs idempotency rationale  ·  `python`  ·  synthetic

**Before**
```python
def handle_webhook(event):
    # only handle successful payments
    if event.type == "payment_intent.succeeded":
        # get the payment intent id
        pid = event.data.object.id
        # if we have seen this id, skip it
        if pid in processed:
            return
        # add the id to the processed set
        processed.add(pid)
        # fulfill the order
        fulfill(pid)
```

**After**
```python
def handle_webhook(event):
    if event.type != "payment_intent.succeeded":
        return
    pid = event.data.object.id
    # Stripe re-delivers webhooks until it gets a 2xx, so the same event can
    # arrive several times; dedupe on payment_intent id to stay idempotent (PAY-212).
    if pid in processed:
        return
    processed.add(pid)
    fulfill(pid)
```

**Why:** Demonstrates deleting comments that restate the adjacent line (get the id, add to set, fulfill) while KEEPING the one comment a reader cannot reconstruct from the code: the external-system quirk (Stripe re-delivery) that motivates the dedupe. The when_not is honored - the rationale + ticket link are preserved, not stripped to chase a lower comment count.

---

## retry backoff: per-line narration vs rate-limit constraint  ·  `typescript`  ·  synthetic

**Before**
```typescript
async function fetchUser(id: string): Promise<User> {
  // try up to 3 times
  for (let attempt = 0; attempt < 3; attempt++) {
    // make the request
    const res = await fetch(`${BASE}/users/${id}`);
    // if the response is ok, return the parsed body
    if (res.ok) return res.json();
    // wait before retrying
    await sleep(2 ** attempt * 100);
  }
  // throw if all attempts failed
  throw new Error(`failed to fetch user ${id}`);
}
```

**After**
```typescript
async function fetchUser(id: string): Promise<User> {
  for (let attempt = 0; attempt < 3; attempt++) {
    const res = await fetch(`${BASE}/users/${id}`);
    if (res.ok) return res.json();
    // Provider 429s under burst load; exponential backoff (100/200/400ms) keeps
    // us under their 10 req/s cap without a full token bucket.
    await sleep(2 ** attempt * 100);
  }
  throw new Error(`failed to fetch user ${id}`);
}
```

**Why:** Shows that 'try up to 3 times' / 'make the request' / 'throw if all attempts failed' add nothing the code doesn't already say, whereas the surviving comment encodes an external constraint and the tradeoff (why these specific delays, why not a token bucket). Guards the opposite pole: the non-obvious why is kept, not deleted in the name of terseness.

---

## transfer lock ordering: narrated steps vs deadlock-avoidance why  ·  `go`  ·  synthetic

**Before**
```go
func transfer(tx *sql.Tx, from, to Account, cents int64) error {
	// put the accounts in a slice
	accts := []Account{from, to}
	// sort the accounts by id
	sort.Slice(accts, func(i, j int) bool { return accts[i].ID < accts[j].ID })
	// loop over the accounts
	for _, a := range accts {
		// lock the account row
		if err := lockRow(tx, a.ID); err != nil {
			return err
		}
	}
	return applyTransfer(tx, from, to, cents)
}
```

**After**
```go
func transfer(tx *sql.Tx, from, to Account, cents int64) error {
	// Lock rows in ascending id order: two opposite-direction transfers would
	// otherwise grab the same two locks in reverse and deadlock.
	accts := []Account{from, to}
	sort.Slice(accts, func(i, j int) bool { return accts[i].ID < accts[j].ID })
	for _, a := range accts {
		if err := lockRow(tx, a.ID); err != nil {
			return err
		}
	}
	return applyTransfer(tx, from, to, cents)
}
```

**Why:** The before narrates every mechanical step yet never states the one thing that matters - WHY the sort exists. The after drops the narration and replaces it with the invariant (consistent lock ordering to avoid deadlock), which is exactly the kind of load-bearing why-comment the rule says to keep; removing it (the minimalist overcorrection) would lose information no name or signature can carry.

---

## Google Python Style Guide §3.8.5 — explain intent; never describe the code  ·  `python`  ·  ✅ sourced
Source: https://google.github.io/styleguide/pyguide.html#385-block-and-inline-comments

**Before**
```python
# BAD COMMENT: Now go through the b array and make sure whenever i occurs
# the next element is i+1
```

**After**
```python
# We use a weighted dictionary search to find out where i is in
# the array.  We extrapolate position based on the largest num
# in the array and the array size and then do binary search to
# get the exact number.

if i & (i-1) == 0:  # True if i is 0 or a power of 2.
```

**Why:** The guide's BAD example narrates line-by-line what the code does; the GOOD example explains why (the chosen search strategy) and decodes a non-obvious expression ("True if i is 0 or a power of 2"). Demonstrates comment-why-not-what directly. When NOT to apply: self-evident code needs no comment at all — adding a why-comment to trivial code is just clutter.

_Verified: Fetched https://google.github.io/styleguide/pyguide.html#385-block-and-inline-comments and confirmed all claimed content in section 3.8.5 "Block and Inline Comments": (1) the good example "We use a weighted dictionary search to find out where i is in the array." is present; (2) the line "# True if i is 0 or a power of 2." is present; (3) the bad example beginning "# BAD COMMENT: Now go through the b array and make sure whenever i occurs" is present; (4) the instruction "On the other hand, never describe the code." is present. The candidate's before/after fields accurately represent the page content._

---
