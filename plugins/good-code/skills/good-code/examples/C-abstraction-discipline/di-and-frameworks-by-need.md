# di-and-frameworks-by-need

_Theme C: abstraction-discipline_

## NestJS @Injectable service that only forwards to a repo  ·  `typescript`  ·  synthetic

**Before**
```typescript
@Injectable()
export class UserService {
  constructor(
    @Inject('USER_REPO') private readonly repo: UserRepository,
  ) {}

  findById(id: string): Promise<User | null> {
    return this.repo.findOne({ where: { id } });
  }
}

@Module({
  providers: [
    UserService,
    { provide: 'USER_REPO', useClass: UserRepository },
  ],
  exports: [UserService],
})
export class UserModule {}
```

**After**
```typescript
export function getUser(db: Db, id: string): Promise<User | null> {
  return db.query.users.findFirst({ where: eq(users.id, id) });
}
```

**Why:** Shows that a one-method service whose only job is to forward to a repo does not need @Injectable/@Module/@Inject token wiring: a plain function taking db explicitly is testable (pass a fake db) and needs no container to boot. When-NOT: in a large multi-team Nest codebase already standardized on modules/providers with lifecycle hooks, a lone plain function fights the grain - match the existing DI convention there.

---

## dependency-injector container for a trivial DB fetch  ·  `python`  ·  synthetic

**Before**
```python
from dependency_injector import containers, providers

class UserService:
    def __init__(self, db: Database) -> None:
        self._db = db

    def get(self, user_id: int) -> User | None:
        return self._db.fetch_one(
            users.select().where(users.c.id == user_id))

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    db = providers.Singleton(Database, url=config.db_url)
    user_service = providers.Factory(UserService, db=db)
```

**After**
```python
def get_user(db: Database, user_id: int) -> User | None:
    return db.fetch_one(
        users.select().where(users.c.id == user_id))
```

**Why:** Demonstrates dropping a DeclarativeContainer + Singleton/Factory wiring for a function that just needs the db handle passed in; tests call it with a stub db, no container bootstrap. When-NOT: if the app already standardizes on dependency-injector, or genuinely has many cross-cutting singletons with managed lifecycles, match that wiring instead of introducing a one-off bare function.

---

## uber-fx provider graph vs explicit wiring in main  ·  `go`  ·  synthetic

**Before**
```go
func main() {
    fx.New(
        fx.Provide(loadConfig, openDB, newUserStore, newServer),
        fx.Invoke(startServer),
    ).Run()
}

func newUserStore(db *sql.DB) *UserStore { return &UserStore{db: db} }
func newServer(s *UserStore, cfg *Config) *http.Server { /* routes */ }
```

**After**
```go
func main() {
    cfg := loadConfig()
    db := mustOpenDB(cfg.DSN)
    defer db.Close()

    srv := newServer(&UserStore{db: db}, cfg)
    log.Fatal(srv.ListenAndServe())
}
```

**Why:** Shows explicit construction in main reading top-to-bottom and being trivially debuggable, versus an fx provider graph resolved by reflection at runtime; for a handful of deps the container hides more than it helps. When-NOT: a large service with dozens of providers, OnStart/OnStop lifecycle hooks, and many teams can justify fx/wire - keep it where that wiring already pays off.

---
