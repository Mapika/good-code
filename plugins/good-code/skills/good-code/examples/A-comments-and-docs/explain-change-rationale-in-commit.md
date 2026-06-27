# explain-change-rationale-in-commit

_Theme A: comments-and-docs_

## vague 'Fix bug' vs imperative summary + rationale body  ·  `go`  ·  ✅ sourced
Source: https://google.github.io/eng-practices/review/developer/cl-descriptions.html

**Before**
```go
// commit subject for the RPC server freelist change:
Fix bug
```

**After**
```go
RPC: Remove size limit on RPC server message freelist.

Servers like FizzBuzz have very large messages and would benefit from
reuse. Make the freelist larger, and add a goroutine that frees the
freelist entries slowly over time, so that idle servers eventually
release all freelist entries.
```

**Why:** Shows the exact anti-pattern this rule replaces: 'Fix bug' carries zero information, while the good message leads with an imperative one-line summary and a body explaining the problem (large messages, reuse) and the chosen approach (bigger freelist + a goroutine that drains it). When-NOT guard: this is a non-trivial functionality change, so the body earns its keep; a typo or version bump would need only the summary line, not this much prose.

_Verified: Fetched https://google.github.io/eng-practices/review/developer/cl-descriptions.html. Confirmed 'Fix bug' appears verbatim as an inadequate/bad CL description example. Also confirmed the full good functionality-change example appears verbatim: 'RPC: Remove size limit on RPC server message freelist.' followed by the body 'Servers like FizzBuzz have very large messages and would benefit from reuse. Make the freelist larger, and add a goroutine that frees the freelist entries slowly over time, so that idle servers eventually release all freelist entries.' The leading '//' line is editorial scenario framing, not claimed to be from the page._

---

## nightly ETL batch-size change: 'update' vs why-it-changed  ·  `python`  ·  synthetic

**Before**
```python
# diff: BATCH_SIZE = 1000 -> 200 in nightly_export.py
git commit -m "update"
```

**After**
```python
# diff: BATCH_SIZE = 1000 -> 200 in nightly_export.py
git commit -m "Lower nightly export batch size 1000 -> 200

The analytics replica OOM-killed the export whenever a batch held a few
rows with large JSON blobs (P99 payload ~8MB). 200 keeps peak memory
under the 512MB cgroup limit with margin; throughput is unaffected
since the job is I/O-bound on the replica read (INC-744)."
```

**Why:** Demonstrates explaining WHY a magic-number tweak was made: the diff shows 1000->200, but only the body explains the OOM cause, why 200 specifically (cgroup limit), and that throughput is safe, plus the incident link. When-NOT guard: the body is justified because the number alone looks arbitrary and risky; a self-evident change (e.g. fixing a typo'd constant name) would not warrant this and padding it would be ceremony.

---

## checkout API status-code fix: 'Fix checkout' vs problem + approach  ·  `typescript`  ·  synthetic

**Before**
```typescript
// PR title for handlers/checkout.ts change
Fix checkout
```

**After**
```typescript
// PR title + body for handlers/checkout.ts change
Return 409 (not 500) for duplicate idempotency keys

Mobile clients retry on network timeout and replay the same
Idempotency-Key. We inserted, hit the unique constraint, and surfaced a
500 — which the client treats as fatal and shows an error to users who
were in fact already charged. Map the constraint violation to 409 so the
client treats the replay as success. (FUNNEL-1290)
```

**Why:** Shows a PR description that states the user-facing problem (duplicate retries -> false error after a successful charge) and the chosen approach (map the constraint violation to 409), which the one-line diff cannot convey, versus the contentless 'Fix checkout'. When-NOT guard: appropriate because the reasoning isn't reconstructable from the diff alone — it is not an instruction to write a body for every commit; trivial mechanical PRs still need only the imperative summary.

---

## Google Eng Practices — Writing good CL (commit) descriptions: bad vs good  ·  `go`  ·  ✅ sourced
Source: https://google.github.io/eng-practices/review/developer/cl-descriptions.html

**Before**
```go
Fix bug
```

**After**
```go
RPC: Remove size limit on RPC server message freelist.

Servers like FizzBuzz have very large messages and would benefit from reuse. Make the freelist larger, and add a goroutine that frees the freelist entries slowly over time, so that idle servers eventually release all freelist entries.
```

**Why:** Contrasts an inadequate commit/CL description ("Fix bug" — no what, no why) with a good one that states what changed and, crucially, the rationale and impact (large messages benefit from reuse; how the fix bounds memory). Demonstrates explain-change-rationale-in-commit. When NOT to apply: a purely mechanical change (e.g., automated rename/revert) doesn't need a long narrative — scale the rationale to the change. Tagged go because the example's rationale is about goroutines/RPC servers.

_Verified: Fetched https://google.github.io/eng-practices/review/developer/cl-descriptions.html and confirmed both claimed elements. (1) The "Bad CL Descriptions" section explicitly states: "'Fix bug' is an inadequate CL description. What bug? What did you do to fix it?" — matching the candidate's before="Fix bug". (2) The "Good CL Descriptions" → "Functionality change" example reads: "RPC: Remove size limit on RPC server message freelist. Servers like FizzBuzz have very large messages and would benefit from reuse. Make the freelist larger, and add a goroutine that frees the freelist entries slowly over time, so that idle servers eventually release all freelist entries." — matching the candidate's after text verbatim, including the FizzBuzz/large-messages/reuse and goroutine-freelist rationale. The before→after pattern genuinely exists on the page._

---
