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
