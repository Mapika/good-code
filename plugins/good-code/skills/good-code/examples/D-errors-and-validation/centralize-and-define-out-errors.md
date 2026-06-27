# centralize-and-define-out-errors

_Theme D: errors-and-validation_

## clamping accessor folds a benign out-of-range case into normal behavior  ·  `python`  ·  synthetic

**Before**
```python
def get_page_size(params):
    size = int(params.get("page_size", 50))
    if size < 1:
        raise ValueError("page_size must be >= 1")
    if size > 100:
        # every caller now has to try/except this benign case
        raise ValueError("page_size must be <= 100")
    return size
```

**After**
```python
def get_page_size(params, default=50, maximum=100):
    # Out-of-range page size is benign: clamp instead of raising so
    # no caller has to guard it. A non-numeric value still raises
    # (int()) and is caught once at the request boundary.
    size = int(params.get("page_size", default))
    return max(1, min(size, maximum))
```

**Why:** Demonstrates defining a benign 'error' out of existence: an out-of-range pagination limit becomes ordinary clamped behavior, removing a guard from every caller. When-NOT: clamp only when the case is genuinely harmless (limits); the real parse error (non-numeric) is deliberately left to surface at the boundary, and you would NOT silently clamp a semantically meaningful value like a payment amount.

---

## stop redundant per-layer error wrapping; add only the context the error lacks  ·  `go`  ·  synthetic

**Before**
```go
func (h *Handler) Signup(ctx context.Context, u User) error {
    if err := h.store.CreateUser(ctx, u); err != nil {
        return fmt.Errorf("failed to handle signup: %w", err)
    }
    return nil
}

func (s *Store) CreateUser(ctx context.Context, u User) error {
    if err := s.db.Insert(ctx, u); err != nil {
        return fmt.Errorf("failed to create user: %w", err)
    }
    return nil
}
// -> "failed to handle signup: failed to create user: insert: dup key"
```

**After**
```go
func (h *Handler) Signup(ctx context.Context, u User) error {
    // Nothing to add that the callee doesn't already say.
    return h.store.CreateUser(ctx, u)
}

func (s *Store) CreateUser(ctx context.Context, u User) error {
    if err := s.db.Insert(ctx, u); err != nil {
        return fmt.Errorf("insert user %q: %w", u.ID, err) // adds the id
    }
    return nil
}
// -> "insert user \"u_42\": dup key"
```

**Why:** Demonstrates trimming the 'failed to X: failed to Y: failed to Z' stack: each wrap adds only context the underlying error lacks (the user id), and a layer with nothing new to say returns the error unchanged. When-NOT: this is not swallowing - the %w chain and id are preserved for debugging; keep a wrap whenever it genuinely adds context.

---

## aggregate the uniform error->HTTP response at one boundary handler  ·  `typescript`  ·  synthetic

**Before**
```typescript
fastify.get("/orders/:id", async (req, reply) => {
  try {
    return await getOrder(req.params.id);
  } catch (err) {
    req.log.error(err);
    return reply.code(500).send({ error: "internal error" });
  }
});

fastify.post("/orders", async (req, reply) => {
  try {
    reply.code(201);
    return await createOrder(req.body);
  } catch (err) {
    req.log.error(err);
    return reply.code(500).send({ error: "internal error" });
  }
});
```

**After**
```typescript
fastify.get("/orders/:id", async (req) => getOrder(req.params.id));
fastify.post("/orders", async (req, reply) => {
  reply.code(201);
  return createOrder(req.body);
});

// One boundary maps domain errors -> HTTP; Fastify routes thrown
// and rejected errors here automatically.
fastify.setErrorHandler((err, req, reply) => {
  const status = err instanceof NotFound ? 404 : 500;
  req.log.error({ err }, "request failed");
  reply.code(status).send({ error: err.message });
});
```

**Why:** Demonstrates routing an identical try/catch-log-500 from every handler into a single error boundary, so handlers express only the happy path. When-NOT: the boundary still discriminates NotFound (404) from unexpected (500) and logs once - it does not silence errors or flatten security-relevant failures into a generic success.

---

## Don't just check errors, handle them gracefully — 'Only handle errors once' (Dave Cheney)  ·  `go`  ·  ✅ sourced
Source: https://dave.cheney.net/2016/04/27/dont-just-check-errors-handle-them-gracefully

**Before**
```go
func Write(w io.Writer, buf []byte) error {
        _, err := w.Write(buf)
        if err != nil {
                // annotated error goes to log file
                log.Println("unable to write:", err)

                // unannotated error returned to caller
                return err
        }
        return nil
}
```

**After**
```go
func Write(w io.Write, buf []byte) error {
        _, err := w.Write(buf)
        return errors.Wrap(err, "write failed")
}
```

**Why:** Demonstrates handling each error exactly once in one place: instead of logging at every layer and also returning the raw error (which duplicates log lines and strips context as it bubbles up), wrap once with context and let a single boundary decide. When NOT to apply: something must still handle/log it once at the top level (don't wrap-and-return forever), and when callers match sentinel errors, preserve them with %w/errors.Is rather than opaquely wrapping.

_Verified: Fetched https://dave.cheney.net/2016/04/27/dont-just-check-errors-handle-them-gracefully and confirmed the "Only handle errors once" section. The 'before' example matches exactly: func Write(w io.Writer, buf []byte) error { _, err := w.Write(buf); if err != nil { // annotated error goes to log file; log.Println("unable to write:", err); // unannotated error returned to caller; return err }; return nil }. The 'after' example also matches exactly, including the original article's typo `io.Write` (not io.Writer): func Write(w io.Write, buf []byte) error { _, err := w.Write(buf); return errors.Wrap(err, "write failed") }. Surrounding text confirms the "you should only handle errors once" guidance and the duplicate-logging problem. Both code blocks and the noted typo are genuinely present._

---
