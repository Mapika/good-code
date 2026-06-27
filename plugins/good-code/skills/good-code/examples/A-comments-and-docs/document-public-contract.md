# document-public-contract

_Theme A: comments-and-docs_

## send_from_directory documents the security precondition, not the body  ·  `python`  ·  ✅ sourced
Source: https://raw.githubusercontent.com/pallets/flask/main/src/flask/helpers.py

**Before**
```python
def send_from_directory(directory, path, **kwargs):
    # joins directory and path, then calls send_file on the result
    return send_file(safe_join(directory, path), **kwargs)
```

**After**
```python
def send_from_directory(
    directory: os.PathLike[str] | str,
    path: os.PathLike[str] | str,
    **kwargs: t.Any,
) -> Response:
    """Send a file from within a directory using :func:`send_file`.

    This is a secure way to serve files from a folder, such as static
    files or uploads. Uses :func:`~werkzeug.security.safe_join` to
    ensure the path coming from the client is not maliciously crafted to
    point outside the specified directory.
    """
    ...
```

**Why:** The real Flask contract tells a caller the one thing they cannot see from the signature: this path is client-safe (uses safe_join), whereas send_file is not. The bad version wastes its comment narrating the body (join + call send_file) and omits the precondition. when_NOT: it deliberately stays at caller altitude and does not re-explain the joining algorithm, and a one-line private helper would get no docstring at all.

_Verified: Fetched the raw Flask source. send_from_directory has the exact signature def send_from_directory(directory: os.PathLike[str] | str, path: os.PathLike[str] | str, **kwargs: t.Any) -> Response, and the docstring begins 'Send a file from within a directory using :func:`send_file`.' and includes the safe_join text ensuring the path is not 'maliciously crafted to point outside the specified directory.' The AFTER matches verbatim; BEFORE is correctly noted as illustrative._

---

## retry wrapper: TSDoc states throws + non-retry behavior  ·  `typescript`  ·  synthetic

**Before**
```typescript
// Loops up to maxAttempts times, calls fetch, sleeps with exponential
// backoff between tries, then parses and returns the JSON body.
export async function getJson(url: string, maxAttempts: number): Promise<any> {
  // ...
}
```

**After**
```typescript
/**
 * GET a JSON resource, retrying transient network and 5xx failures.
 *
 * @param url Absolute URL to fetch.
 * @param opts.maxAttempts Total attempts including the first (default 3).
 * @returns The decoded body of the first 2xx response.
 * @throws {HttpError} on a 4xx (not retried) or after all attempts fail.
 */
export async function getJson<T>(
  url: string,
  opts?: { maxAttempts?: number },
): Promise<T> {
  // ...
}
```

**Why:** The contract surfaces what a caller must know but cannot infer: 4xx is NOT retried, the default attempt count, and the typed throw. The bad version uses `any`, re-narrates the backoff loop, and hides the throw behavior. when_NOT: the doc omits the backoff formula (implementation detail) rather than expanding it, so it documents the boundary without restating the body.

---

## godoc states blocking, error, and concurrency contract  ·  `go`  ·  synthetic

**Before**
```go
// Acquire loops checking the bucket's tokens, sleeps until one frees up,
// then decrements the counter and returns nil.
func (l *Limiter) Acquire(ctx context.Context) error {
	// ...
}
```

**After**
```go
// Acquire blocks until a rate-limit token is available or ctx is done.
// It returns ctx.Err() if the context is canceled or its deadline passes
// before a token is granted, and nil once a token has been consumed.
// Acquire is safe for concurrent use by multiple goroutines.
func (l *Limiter) Acquire(ctx context.Context) error {
	// ...
}
```

**Why:** Follows godoc convention (comment starts with the symbol name) and documents the three things a caller needs: it blocks, it returns ctx.Err() on cancellation, and it is goroutine-safe. The bad comment narrates the token-bucket loop instead. when_NOT: the contract omits the bucket-refill mechanics, and an unexported helper like refill() would need no such comment.

---
