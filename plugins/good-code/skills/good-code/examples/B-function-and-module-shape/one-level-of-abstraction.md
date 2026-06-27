# one-level-of-abstraction

_Theme B: function-and-module-shape_

## CSV import handler mixes byte-decoding with domain upsert  ·  `python`  ·  synthetic

**Before**
```python
def import_orders(raw_rows):
    saved = []
    for raw in raw_rows:
        cols = raw.decode("utf-8").rstrip("\n").split(",")
        order = Order(
            id=int(cols[0]),
            total=Decimal(cols[1]) / 100,
            created=datetime.strptime(cols[2], "%Y-%m-%dT%H:%M:%S"),
        )
        if order.total > 0:
            db.upsert(order)
            saved.append(order.id)
    return saved
```

**After**
```python
def import_orders(raw_rows):
    saved = []
    for raw in raw_rows:
        order = parse_order_row(raw)
        if order.total > 0:
            db.upsert(order)
            saved.append(order.id)
    return saved
```

**Why:** The loop now reads at one altitude (parse -> validate -> persist) instead of interleaving byte-decoding and field coercion with orchestration. Guards the when-NOT: parse_order_row earns its existence by hiding real complexity (decode, split, int/Decimal/date coercion); if it were a one-line constructor call it would be a trampoline and you'd inline it.

---

## webhook handler inlines HMAC signature verification  ·  `typescript`  ·  synthetic

**Before**
```typescript
export async function handleWebhook(req: Request): Promise<Response> {
  const raw = await req.text();
  const sig = req.headers.get("x-signature") ?? "";
  const expected = crypto
    .createHmac("sha256", SECRET)
    .update(raw, "utf8")
    .digest("hex");
  if (!crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expected))) {
    return new Response("bad signature", { status: 401 });
  }
  const event = JSON.parse(raw) as StripeEvent;
  await processEvent(event);
  return new Response("ok");
}
```

**After**
```typescript
export async function handleWebhook(req: Request): Promise<Response> {
  const raw = await req.text();
  if (!isValidSignature(raw, req.headers.get("x-signature"))) {
    return new Response("bad signature", { status: 401 });
  }
  await processEvent(JSON.parse(raw) as StripeEvent);
  return new Response("ok");
}
```

**Why:** The handler now reads purely at HTTP altitude (read body, authenticate, process, respond); the HMAC digest and timing-safe byte comparison drop one level into isValidSignature, which genuinely hides crypto mechanics. Guards the when-NOT: JSON.parse and new Response stay inline because they are already at the handler's level; wrapping them in parseEvent()/ok() trampolines would add indirection that hides nothing.

---

## retry dispatcher mixes backoff loop with raw HTTP plumbing  ·  `go`  ·  synthetic

**Before**
```go
func dispatch(ctx context.Context, e Event) error {
    payload, _ := json.Marshal(e)
    for attempt := 0; attempt < maxRetries; attempt++ {
        req, _ := http.NewRequestWithContext(ctx, http.MethodPost, hookURL, bytes.NewReader(payload))
        req.Header.Set("Content-Type", "application/json")
        resp, err := httpClient.Do(req)
        if err == nil && resp.StatusCode < 500 {
            resp.Body.Close()
            return nil
        }
        if resp != nil {
            resp.Body.Close()
        }
        time.Sleep(time.Duration(1<<attempt) * time.Second)
    }
    return fmt.Errorf("dispatch %s: exhausted %d attempts", e.ID, maxRetries)
}
```

**After**
```go
func dispatch(ctx context.Context, e Event) error {
    payload, err := json.Marshal(e)
    if err != nil {
        return fmt.Errorf("marshal event %s: %w", e.ID, err)
    }
    for attempt := 0; attempt < maxRetries; attempt++ {
        if err := postJSON(ctx, hookURL, payload); err == nil {
            return nil
        }
        time.Sleep(backoff(attempt))
    }
    return fmt.Errorf("dispatch %s: exhausted %d attempts", e.ID, maxRetries)
}
```

**Why:** The loop now reads as the policy it is (deliver, back off, retry, then give up) instead of mixing that with request construction, status checks, and body-closing. postJSON is a deep unit that hides all the transport mechanics, and backoff names the exponential-delay decision. Guards the when-NOT: extraction is justified because postJSON hides substantial complexity, not to chase line count; the obvious fmt.Errorf returns stay inline rather than becoming wrapper functions.

---

## Extract Method (Compose Method) — printOwing  ·  `typescript`  ·  ✅ sourced
Source: https://refactoring.guru/extract-method

**Before**
```typescript
printOwing(): void {
  printBanner();

  // Print details.
  console.log("name: " + name);
  console.log("amount: " + getOutstanding());
}
```

**After**
```typescript
printOwing(): void {
  printBanner();
  printDetails(getOutstanding());
}

printDetails(outstanding: number): void {
  console.log("name: " + name);
  console.log("amount: " + outstanding);
}
```

**Why:** Before, printOwing mixes one high-level operation (printBanner()) with low-level console.log printing statements, so the reader jumps between abstraction levels. After, the detail printing is extracted behind printDetails(...), so every line in printOwing is a peer operation at the same level of abstraction. When NOT to do it: do not extract if the new method would just rename a single trivial expression and add no clearer intent — that produces a shallow pass-through, not a cleaner abstraction.

_Verified: Fetched https://refactoring.guru/extract-method successfully. The page hosts the Extract Method refactoring with code tabs for Java, C#, PHP, Python, and TypeScript. The TypeScript tab shows exactly the claimed before/after. BEFORE: printOwing(): void { printBanner(); // Print details. console.log("name: " + name); console.log("amount: " + getOutstanding()); }. AFTER: printOwing(): void { printBanner(); printDetails(getOutstanding()); } and a newly extracted printDetails(outstanding: number): void { console.log("name: " + name); console.log("amount: " + outstanding); }. This matches the candidate before/after verbatim (only a trivial blank-line whitespace difference in the before block). The pattern (inlined detail console.log lines replaced by a call to an extracted printDetails(getOutstanding()) method) is genuinely present and supports the one-level-of-abstraction rule._

---
