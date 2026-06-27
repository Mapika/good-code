# name-scaled-to-scope

_Theme F: naming-and-clarity_

## ETL revenue aggregation drowning in type-echoing names  ·  `python`  ·  synthetic

**Before**
```python
def calculate_total_revenue_for_all_completed_orders(list_of_order_objects):
    total_revenue_accumulator_value = Decimal("0")
    for individual_order_object in list_of_order_objects:
        if individual_order_object.status_string == "completed":
            total_revenue_accumulator_value += individual_order_object.amount
    return total_revenue_accumulator_value
```

**After**
```python
def completed_revenue(orders: list[Order]) -> Decimal:
    total = Decimal("0")
    for order in orders:
        if order.status == "completed":
            total += order.amount
    return total
```

**Why:** Shows length scaled to scope: a descriptive domain function name (completed_revenue) with short, readable locals (total, order) replacing list_of_order_objects / total_revenue_accumulator_value. Guards the opposite pole by keeping the loop explicit and names pronounceable (order, not o/lst/t) and by signalling that the fix is renaming, not collapsing to a one-liner.

---

## data-access function name encoding its whole body  ·  `typescript`  ·  synthetic

**Before**
```typescript
async function fetchAllActiveUserAccountObjectsFromTheDatabase(
  databaseConnectionObject: Database,
): Promise<UserAccount[]> {
  const arrayOfActiveUserAccountObjects: UserAccount[] = [];
  const allUserRecordsList = await databaseConnectionObject.users.findMany();
  for (const currentUserRecordObject of allUserRecordsList) {
    if (currentUserRecordObject.isActive) {
      arrayOfActiveUserAccountObjects.push(currentUserRecordObject);
    }
  }
  return arrayOfActiveUserAccountObjects;
}
```

**After**
```typescript
async function activeUsers(db: Database): Promise<UserAccount[]> {
  const users = await db.users.findMany();
  return users.filter((user) => user.isActive);
}
```

**Why:** Drops type/context echoes (fetchAll...FromTheDatabase, arrayOfActiveUserAccountObjects, currentUserRecordObject) for names scaled to scope: descriptive activeUsers, conventional db, plural users, short arrow param user. Guards the cryptic pole by keeping real words rather than u/acc/arr soup, and lets the type annotation carry the type instead of the name.

---

## repository method with Get-prefix, stutter, and type-suffixed locals  ·  `go`  ·  synthetic

**Before**
```go
func (userRepository *UserRepository) GetUserByUserID(userIDString string) (*User, error) {
    userResultObject, errorValue := userRepository.databaseHandle.FindUser(userIDString)
    if errorValue != nil {
        return nil, fmt.Errorf("get user: %w", errorValue)
    }
    return userResultObject, nil
}
```

**After**
```go
func (r *UserRepository) User(id string) (*User, error) {
    u, err := r.db.FindUser(id)
    if err != nil {
        return nil, fmt.Errorf("find user %s: %w", id, err)
    }
    return u, nil
}
```

**Why:** Removes the Go-specific tells the rule names: the Get- prefix (method becomes User), package/type stutter, and type-suffixed locals (userIDString, errorValue) become idiomatic short locals (r, id, u, err). Guards the opposite pole by matching Go's density norm (very short locals) WITHOUT shrinking the wide-scope exported UserRepository or method name into one-letter soup.

---

## Google Go Style Guide: variable names proportional to scope (omit redundant type words)  ·  `go`  ·  ✅ sourced
Source: https://google.github.io/styleguide/go/decisions.html#variable-name-vs-type

**Before**
```go
var numUsers int
var nameString string
var primaryProject *Project
```

**After**
```go
var users int
var name string
var primary *Project
```

**Why:** Demonstrates the guide's rule that a name's length should be proportional to its scope and inversely proportional to its usage: within a scope where the compiler and usage already make the type obvious, the redundant type word adds nothing, so `numUsers`->`users`, `nameString`->`name`, `primaryProject`->`primary`. When-NOT: the same section says to keep a type-like qualifier when two versions of a value coexist in scope (e.g. an unparsed `ageString` alongside the parsed `age`), and longer names are warranted in large/file-level scopes.

_Verified: Fetched https://google.github.io/styleguide/go/decisions.html#variable-name-vs-type. The "Variable name vs. type" section contains a table mapping "Repetitive Name" to "Better Name" with exactly these three rows: `var numUsers int` -> `var users int`, `var nameString string` -> `var name string`, and `var primaryProject *Project` -> `var primary *Project`. All three match the candidate's before/after pairs verbatim. The "Variable names" section also states: "The general rule of thumb is that the length of a name should be proportional to the size of its scope and inversely proportional to the number of times that it is used within that scope." This confirms both the table mapping and the scope-proportionality claim in verify_hint._

---
