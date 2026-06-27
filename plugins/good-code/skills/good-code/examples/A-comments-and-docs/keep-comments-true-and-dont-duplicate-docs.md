# keep-comments-true-and-dont-duplicate-docs

_Theme A: comments-and-docs_

## sibling HTTP verb re-copies request()'s whole param block  ·  `python`  ·  ✅ sourced
Source: https://github.com/encode/httpx/blob/master/httpx/_api.py

**Before**
```python
def get(
    url: URL | str,
    *,
    params: QueryParamTypes | None = None,
    headers: HeaderTypes | None = None,
    cookies: CookieTypes | None = None,
    timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
) -> Response:
    """
    Sends a `GET` request.

    Parameters:
      url: URL for the new Request object.
      params: (optional) Query parameters to include in the URL.
      headers: (optional) Dictionary of HTTP headers to send.
      cookies: (optional) Dictionary of cookies to send.
      timeout: (optional) The timeout configuration to use.
    """  # full block copied from request(); drifts when request() changes
    ...
```

**After**
```python
def get(
    url: URL | str,
    *,
    params: QueryParamTypes | None = None,
    headers: HeaderTypes | None = None,
    cookies: CookieTypes | None = None,
    timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
) -> Response:
    """
    Sends a `GET` request.

    **Parameters**: See `httpx.request`.

    Note that the `data`, `files`, `json` and `content` parameters are not available
    on this function, as `GET` requests should not include a request body.
    """
    ...
```

**Why:** Documents the param set once on canonical request() and points the verb wrapper to it instead of re-copying a block that silently drifts. when_NOT guard: it does NOT strip everything to chase minimalism, it keeps the load-bearing prose the signature cannot state (which body params are intentionally absent for GET).

_Verified: Fetched https://github.com/encode/httpx/blob/master/httpx/_api.py. The get() function's docstring matches the 'after' snippet exactly: "Sends a `GET` request.\n\n**Parameters**: See `httpx.request`.\n\nNote that the `data`, `files`, `json` and `content` parameters are not available on this function, as `GET` requests should not include a request body." Sibling functions (post/put/patch/delete) follow the same concise reference pattern rather than inlining request()'s full parameter list. The 'before' is the expected synthetic anti-pattern illustration._

---

## TSDoc restates the types the signature already declares  ·  `typescript`  ·  synthetic

**Before**
```typescript
/**
 * Fetch a user by id.
 * @param {string} id - a string user id
 * @param {number} timeoutMs - a number, the timeout
 * @returns {Promise<User>} a promise that resolves to a User
 */
async function getUser(id: string, timeoutMs: number): Promise<User> {
  return client.get(`/users/${id}`, { timeoutMs })
}
```

**After**
```typescript
/**
 * Fetch a user by id.
 * @param timeoutMs - per-request budget; the call rejects with `TimeoutError` once exceeded.
 */
async function getUser(id: string, timeoutMs: number): Promise<User> {
  return client.get(`/users/${id}`, { timeoutMs })
}
```

**Why:** In typed code the `{string}`/`{number}`/`{Promise<User>}` tags and 'a string'/'a number' prose duplicate machine-checkable facts and rot when the signature changes; the type carries the type. when_NOT guard: it keeps the one fact the type can't express (timeout semantics: rejection on exceed) and omits a doc for the self-explanatory `id` rather than blanket-deleting all prose.

---

## godoc claims an expiry behavior the code no longer has  ·  `go`  ·  synthetic

**Before**
```go
// Get returns the cached value for key.
// Returns false if the key is missing or has expired.
func (c *Cache) Get(key string) (Value, bool) {
	e, ok := c.entries[key]
	if !ok {
		return Value{}, false
	}
	e.expires = time.Now().Add(c.ttl) // sliding TTL: extend on read
	return e.val, true
}
```

**After**
```go
// Get returns the cached value for key and true, extending the entry's TTL on
// access (sliding expiration). It returns the zero Value and false only when key
// is absent; a present entry is never reported as expired here.
func (c *Cache) Get(key string) (Value, bool) {
	e, ok := c.entries[key]
	if !ok {
		return Value{}, false
	}
	e.expires = time.Now().Add(c.ttl) // sliding TTL: extend on read
	return e.val, true
}
```

**Why:** The before-comment lies: it promises false 'if expired' but the body refreshes the TTL and never returns false for a present entry, so a caller writing expiry handling is misled, a contradicting comment is worse than none. when_NOT guard: the fix updates the doc to match rather than deleting it, godoc on an exported method is the contract and the meaningful sliding-TTL behavior is preserved.

---
