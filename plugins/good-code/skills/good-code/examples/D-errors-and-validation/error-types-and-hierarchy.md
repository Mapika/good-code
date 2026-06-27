# error-types-and-hierarchy

_Theme D: errors-and-validation_

## HTTP client raises bare Exception with context in the message  ·  `python`  ·  ✅ sourced
Source: https://raw.githubusercontent.com/psf/requests/main/src/requests/exceptions.py

**Before**
```python
def raise_for_status(resp):
    if 400 <= resp.status_code < 600:
        # bare Exception: loses the response object, callers can only string-match
        raise Exception(
            f"request to {resp.url} failed with {resp.status_code}"
        )
```

**After**
```python
class RequestException(IOError):
    """There was an ambiguous exception that occurred while handling your request."""
    def __init__(self, *args, **kwargs):
        self.response = kwargs.pop("response", None)
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

class HTTPError(RequestException):
    """An HTTP error occurred."""

# at the call site, context rides as a field, not buried in the string:
raise HTTPError(f"{resp.status_code} for url: {resp.url}", response=resp)
```

**Why:** Shows the canonical fix: throw a standard typed exception (subclass of IOError), carry context as a structured field (response=) callers can read, and give a single-rooted two-level hierarchy so callers catch RequestException broadly or HTTPError narrowly, each with a one-line docstring. When-NOT: this stops at two levels on purpose - do not explode into a class-per-status-code tree nobody catches.

_Verified: Fetched the raw file from psf/requests main. It defines `class RequestException(IOError)` with docstring "There was an ambiguous exception that occurred while handling your request." (wrapped across two lines) and an __init__ that does `kwargs.pop("response", None)` and `self.request = kwargs.pop("request", None)` before `super().__init__(*args, **kwargs)`. It also defines `class HTTPError(RequestException)` with docstring "An HTTP error occurred.". The raise call site is illustrative usage as noted in the hint._

---

## API layer throws a string / plain object instead of an Error  ·  `typescript`  ·  ✅ sourced
Source: https://github.com/goldbergyoni/nodebestpractices/blob/master/sections/errorhandling/useonlythebuiltinerror.md

**Before**
```typescript
function getUser(id: string) {
  const user = db.find(id);
  // string throw: no stack trace; object throw: inconsistent shape
  if (!user) throw `user ${id} not found`;
  if (!user.active) throw { code: 409, msg: "inactive" };
  return user;
}
```

**After**
```typescript
export class AppError extends Error {
  constructor(
    public readonly name: string,
    public readonly httpCode: HttpCode,
    description: string,
    public readonly isOperational: boolean,
  ) {
    super(description);
    Object.setPrototypeOf(this, new.target.prototype);
    Error.captureStackTrace(this);
  }
}

throw new AppError("NotFound", HttpCode.NOT_FOUND, `user ${id} not found`, true);
```

**Why:** Shows extending the built-in Error so the stack trace survives, with context (httpCode, isOperational) as typed fields rather than packed into the message or a bare object. One AppError suffices because callers branch on httpCode, not on subclass. When-NOT: resist exploding into a deep NotFoundError/ConflictError/... tree when one AppError with fields covers it - but never regress to throwing raw strings/objects.

_Verified: Fetched the nodebestpractices useonlythebuiltinerror.md page. The Best Practice block has `export class AppError extends Error` with readonly name/httpCode/isOperational, calls super(description), Object.setPrototypeOf(this, new.target.prototype) and Error.captureStackTrace(this) (actual source assigns the fields in the constructor body rather than via parameter-property shorthand, an equivalent rendering). The Anti-Pattern section shows throwing a bare string (`throw ('How can I add new product when no value provided?');`)._

---

## Go data-access flattens the cause into a string instead of wrapping  ·  `go`  ·  synthetic

**Before**
```go
var ErrNotFound = errors.New("user not found")

func GetUser(id string) (*User, error) {
    u, err := store.Get(id)
    if err != nil {
        // string-concats the cause: callers can't errors.Is(err, ErrNotFound)
        return nil, errors.New("get user " + id + ": " + err.Error())
    }
    return u, nil
}
```

**After**
```go
var ErrNotFound = errors.New("user not found")

func GetUser(id string) (*User, error) {
    u, err := store.Get(id)
    if err != nil {
        // %w preserves the chain so callers can errors.Is / errors.As
        return nil, fmt.Errorf("get user %s: %w", id, err)
    }
    return u, nil
}

// caller: if errors.Is(err, ErrNotFound) { return http.StatusNotFound }
```

**Why:** Demonstrates the when-NOT for this rule: Go is error-as-value, so the fix is wrapping with %w plus a sentinel that callers inspect via errors.Is/As - not porting an exception hierarchy into Go. When-NOT: don't flatten the cause with %v or string concatenation (it breaks Is/As), and don't manufacture a custom error-type tree where a wrapped sentinel already lets callers branch.

---
