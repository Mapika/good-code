# inline-wrong-abstraction

_Theme C: abstraction-discipline_

## channel flags collapse a notification sender  ·  `python`  ·  synthetic

**Before**
```python
def notify(user, message, *, is_email=False, is_sms=False,
           is_push=False, urgent=False, include_footer=False):
    if is_email:
        body = message + ("\n--\nUnsubscribe" if include_footer else "")
        smtp.send(user.email, body, priority="high" if urgent else "normal")
    elif is_sms:
        twilio.send(user.phone, message[:160])   # urgent/footer ignored
    elif is_push:
        fcm.send(user.device_token, message, high_priority=urgent)
    else:
        raise ValueError("pick a channel")
```

**After**
```python
def email_notify(user, message, *, urgent=False, include_footer=False):
    body = message + ("\n--\nUnsubscribe" if include_footer else "")
    smtp.send(user.email, body, priority="high" if urgent else "normal")

def sms_notify(user, message):
    twilio.send(user.phone, message[:160])

def push_notify(user, message, *, urgent=False):
    fcm.send(user.device_token, message, high_priority=urgent)
```

**Why:** The is_email/is_sms/is_push flags select three unrelated callers, and options like include_footer only apply to one path (silently ignored elsewhere) - the wrong-abstraction tell. Splitting gives each channel exactly the params it uses. when-NOT: if every channel had to apply one shared suppression/opt-out rule that changes in lockstep, factor out that single rule (DRY-for-knowledge), don't keep the flag-driven god-function.

---

## asCSV bool drags an irrelevant header flag  ·  `go`  ·  synthetic

**Before**
```go
func Export(w io.Writer, rows []Row, asCSV bool, withHeader bool) error {
    if asCSV {
        cw := csv.NewWriter(w)
        if withHeader {
            cw.Write([]string{"id", "name"})
        }
        for _, r := range rows {
            cw.Write([]string{r.ID, r.Name})
        }
        cw.Flush()
        return cw.Error()
    }
    return json.NewEncoder(w).Encode(rows) // withHeader meaningless here
}
```

**After**
```go
func ExportCSV(w io.Writer, rows []Row, withHeader bool) error {
    cw := csv.NewWriter(w)
    if withHeader {
        cw.Write([]string{"id", "name"})
    }
    for _, r := range rows {
        cw.Write([]string{r.ID, r.Name})
    }
    cw.Flush()
    return cw.Error()
}

func ExportJSON(w io.Writer, rows []Row) error {
    return json.NewEncoder(w).Encode(rows)
}
```

**Why:** The asCSV boolean picks between two unrelated encoders and withHeader only means something on one branch - the Go boolean-parameter smell. Two functions each take only their relevant option. when-NOT: the column projection (the id,name field order) is shared knowledge; if both formats needed it, extract just that mapping, not a mode flag that re-branches the whole body.

---

## isAdmin flags branch a user serializer per caller  ·  `typescript`  ·  synthetic

**Before**
```typescript
function serializeUser(
  u: User,
  opts: { isAdmin?: boolean; includeEmail?: boolean; forList?: boolean } = {},
) {
  const out: any = { id: u.id, name: u.name };
  if (opts.includeEmail || opts.isAdmin) out.email = u.email;
  if (opts.isAdmin) {
    out.role = u.role;
    out.lastLoginIp = u.lastLoginIp;
  }
  if (!opts.forList) out.createdAt = u.createdAt;
  return out;
}
```

**After**
```typescript
function publicUser(u: User) {
  return { id: u.id, name: u.name, createdAt: u.createdAt };
}

func; // (two distinct view shapes, one per route)
function adminUser(u: User) {
  return {
    id: u.id, name: u.name, email: u.email,
    role: u.role, lastLoginIp: u.lastLoginIp, createdAt: u.createdAt,
  };
}
```

**Why:** The isAdmin/forList flags exist only so two routes (public view vs admin view) reuse one body, forcing per-caller if/else and a loose any return. Splitting into publicUser/adminUser gives each a precise typed shape. when-NOT: if both views must apply the same field-redaction/PII rule that must change together, extract that one rule, not the whole serializer.

---

## Refactoring.Guru: Inline Method (Python example)  ·  `python`  ·  ✅ sourced
Source: https://refactoring.guru/inline-method

**Before**
```python
class PizzaDelivery:
    # ...
    def getRating(self):
        return 2 if self.moreThanFiveLateDeliveries() else 1
  
    def moreThanFiveLateDeliveries(self):
        return self.numberOfLateDeliveries > 5
```

**After**
```python
class PizzaDelivery:
  # ...
  def getRating(self):
    return 2 if self.numberOfLateDeliveries > 5 else 1
```

**Why:** When a helper method's body is as clear as (or clearer than) the method itself, the extra method is a needless indirection; inline the body at the call site and delete the method. Demonstrates collapsing an abstraction that isn't pulling its weight. When NOT: the page explicitly warns 'make sure that the method isn't redefined in subclasses' — if it is overridden, polymorphism depends on it, so do not inline.

_Verified: Fetched https://refactoring.guru/inline-method and read the Python code examples. The BEFORE block matches exactly: `class PizzaDelivery:` defining both `def getRating(self): return 2 if self.moreThanFiveLateDeliveries() else 1` and `def moreThanFiveLateDeliveries(self): return self.numberOfLateDeliveries > 5`. The AFTER block matches exactly: `class PizzaDelivery:` with only `def getRating(self): return 2 if self.numberOfLateDeliveries > 5 else 1`, inlining the condition directly and removing the moreThanFiveLateDeliveries() helper. Both the before/after code and the verify_hint pattern (Python tab, helper inlined into getRating and removed) are genuinely present on the page._

---
