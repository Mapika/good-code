# no-premature-abstraction

_Theme C: abstraction-discipline_

## strategy + factory for a single notification channel  ·  `typescript`  ·  synthetic

**Before**
```typescript
interface NotificationChannel {
  send(to: string, body: string): Promise<void>
}
class EmailChannel implements NotificationChannel {
  async send(to: string, body: string) { await mailer.send(to, body) }
}
class NotificationFactory {
  create(): NotificationChannel { return new EmailChannel() }
}

const notifier = new NotificationFactory().create()
await notifier.send(user.email, "Welcome aboard!")
```

**After**
```typescript
async function sendEmail(to: string, body: string): Promise<void> {
  await mailer.send(to, body)
}

await sendEmail(user.email, "Welcome aboard!")
```

**Why:** Shows that a single-implementation interface plus factory is pure scaffolding when email is the only channel that ships today; write the concrete call. When-NOT: the instant SMS/push become real, reintroduce NotificationChannel at that second call site — the rule says abstract at the second genuine use, not never.

---

## abstract base repository with one concrete subclass  ·  `python`  ·  synthetic

**Before**
```python
from abc import ABC, abstractmethod

class AbstractUserRepository(ABC):
    @abstractmethod
    def get(self, user_id: int) -> User: ...

class PostgresUserRepository(AbstractUserRepository):
    def get(self, user_id: int) -> User:
        row = db.execute("select * from users where id=%s", [user_id]).fetchone()
        return User(**row)

repo: AbstractUserRepository = PostgresUserRepository()
```

**After**
```python
def get_user(user_id: int) -> User:
    row = db.execute("select * from users where id=%s", [user_id]).fetchone()
    return User(**row)
```

**Why:** An ABC with exactly one subclass invents a polymorphism seam for a backend that has no second implementor and no test double a plain function/monkeypatch wouldn't serve. When-NOT: keep the ABC the moment a real second store (in-memory, DynamoDB) or a published extension point exists — this is 'wait for the second implementation', not 'never use ABCs'.

---

## single-impl interface returned from constructor  ·  `go`  ·  synthetic

**Before**
```go
type Storer interface {
    Save(ctx context.Context, e Event) error
}

type pgStore struct{ db *sql.DB }

func (s *pgStore) Save(ctx context.Context, e Event) error {
    _, err := s.db.ExecContext(ctx, "INSERT INTO events (id, body) VALUES ($1, $2)", e.ID, e.Body)
    return err
}

func NewStore(db *sql.DB) Storer { return &pgStore{db: db} }
```

**After**
```go
type EventStore struct{ db *sql.DB }

func (s *EventStore) Save(ctx context.Context, e Event) error {
    _, err := s.db.ExecContext(ctx, "INSERT INTO events (id, body) VALUES ($1, $2)", e.ID, e.Body)
    return err
}

func NewEventStore(db *sql.DB) *EventStore { return &EventStore{db: db} }
```

**Why:** Idiomatic Go returns concrete types and lets the consumer declare the interface; a one-method Storer with one implementation, handed back from the constructor, adds dispatch and hides nothing. When-NOT: when a real second backend or a genuine test boundary appears, define a small interface at the consumer that needs it — so this guards against both eager interfaces and the opposite 'never abstract' pole.

---
