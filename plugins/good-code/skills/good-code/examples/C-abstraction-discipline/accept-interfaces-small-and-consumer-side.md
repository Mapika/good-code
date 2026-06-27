# accept-interfaces-small-and-consumer-side

_Theme C: abstraction-discipline_

## report reader takes fat implementer-side Storage interface  ·  `go`  ·  synthetic

**Before**
```go
// package storage — interface declared next to the implementation
type Storage interface {
	Get(ctx context.Context, key string) ([]byte, error)
	Put(ctx context.Context, key string, val []byte) error
	Delete(ctx context.Context, key string) error
	List(ctx context.Context, prefix string) ([]string, error)
	Close() error
}

// package report — forced to depend on all 5 methods just to read one blob
func Render(s storage.Storage, key string) ([]byte, error) {
	return s.Get(context.Background(), key)
}
```

**After**
```go
// package report — declare only the behavior this consumer actually uses
type blobGetter interface {
	Get(ctx context.Context, key string) ([]byte, error)
}

func Render(g blobGetter, key string) ([]byte, error) {
	return g.Get(context.Background(), key)
}
```

**Why:** Shows the Go idiom: accept a one-method interface defined at the consumer (unexported, named for behavior) instead of importing a fat God-interface from the implementer package; any *storage.S3, *storage.Disk, or a test fake satisfies it structurally. When-NOT: if Render genuinely needed Get+Put+Delete, declare those three rather than splitting one interface per method, and a deliberately published API may keep a wider stable interface.

---

## greet() depends on whole UserRepository to read one record  ·  `typescript`  ·  synthetic

**Before**
```typescript
interface UserRepository {
  findById(id: string): Promise<User>;
  save(u: User): Promise<void>;
  delete(id: string): Promise<void>;
  findAll(): Promise<User[]>;
  count(): Promise<number>;
}

async function greet(repo: UserRepository, id: string): Promise<string> {
  const user = await repo.findById(id);
  return `Hello, ${user.name}`;
}
```

**After**
```typescript
// accept only the capability this function uses, narrowed at the call site
type FindsUser = Pick<UserRepository, "findById">;

async function greet(repo: FindsUser, id: string): Promise<string> {
  const user = await repo.findById(id);
  return `Hello, ${user.name}`;
}
```

**Why:** Demonstrates interface segregation in TS via Pick: the consumer declares the minimal structural shape it depends on, so a stub or a partial fake satisfies greet without the full repository. When-NOT: don't narrow to one method when the function legitimately calls several (then Pick the real set), and don't invent a brand-new interface when the concrete type is fine and never substituted.

---

## config loader hard-depends on the concrete S3 client  ·  `python`  ·  synthetic

**Before**
```python
class S3Client:
    def get_object(self, bucket: str, key: str) -> bytes: ...
    def put_object(self, bucket: str, key: str, body: bytes) -> None: ...
    def delete_object(self, bucket: str, key: str) -> None: ...
    def list_objects(self, bucket: str) -> list[str]: ...

def load_config(client: S3Client, key: str) -> dict:
    raw = client.get_object("configs", key)
    return json.loads(raw)
```

**After**
```python
from typing import Protocol

class ObjectGetter(Protocol):
    def get_object(self, bucket: str, key: str) -> bytes: ...

def load_config(client: ObjectGetter, key: str) -> dict:
    raw = client.get_object("configs", key)
    return json.loads(raw)
```

**Why:** Shows the Python analog: a small structural Protocol named for the one behavior used, so the real boto3 client and an in-memory fake both satisfy load_config without inheritance. When-NOT: don't add a Protocol when the function is only ever called with the concrete client and never substituted (a plain type hint suffices), and don't list methods the body doesn't call — introduce the seam when a real test double or second backend exists.

---
