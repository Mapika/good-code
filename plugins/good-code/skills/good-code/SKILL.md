---
name: good-code
description: >-
  Write or edit backend code (Python, TypeScript, Go) the way a senior engineer
  would — appropriately expressive, neither verbose nor cryptic. Use when writing
  new backend code, editing existing code, reviewing a diff, or on "clean up /
  refactor / make this better" requests. Teaches WHEN to comment, abstract,
  validate, and handle errors (every rule carries a when-NOT guard) so the output
  does not read as machine-generated. This is about code, not chat verbosity.
---

# Writing good code

**Good code is _appropriately expressive_, not minimal.** The characteristic failure
of generated code is *miscalibrated expressiveness* — over-commenting, narrating the
obvious, abstracting for one caller, defensive bloat — but the cure is judgment, not a
diet. Every rule below is a **WHEN**, with an explicit **when-NOT** naming the opposite
failure. If you find yourself making code terser or sparser just to comply, you are
failing the skill, not passing it.

Before a non-trivial change, read 2–3 neighboring files and match what you find.
Worked before→after examples in Python/TS/Go are in [`examples/`](examples/INDEX.md);
full rationale, sources, and the resolved canon conflicts (e.g. deep modules over many
tiny functions) are in [`REFERENCE.md`](REFERENCE.md).

---

## The judgment, in three anchors

**Comment the WHY, delete the WHAT:**
```python
retries += 1   # increment retries                      # ✗ restates the line

# Upstream flaps under load; tolerate 3 transient 5xx     # ✓ info the code can't carry
# before giving up (INC-481).
retries += 1
```

**Stay concrete until a second caller is real:**
```typescript
interface PaymentProvider { charge(cents: number): Promise<Receipt>; }  // ✗ one impl,
class StripeProvider implements PaymentProvider { /* the only one */ }  //   speculative

async function charge(cents: number): Promise<Receipt> { /* ... */ }    // ✓ inline until
                                                                        //   a 2nd provider exists
```

**Reach for a function over data first; make a class earn its place.** A class / ABC / Protocol / interface is justified by exactly one of: (a) it bundles mutable state with the behaviour that guards it (a connection pool, a batcher); (b) one consumer dispatches over interchangeable implementations through *one identical signature* (real polymorphism); (c) it's a published / plugin boundary with external implementors. "I have three implementations" is **not** justification — three impls each called through their own type-specific method are three functions.
```python
class Channel(ABC):                          # ✗ fake interface: send() is never
    @abstractmethod                          #   called polymorphically, and each
    def send(self, **kwargs): ...            #   impl takes different args
class EmailChannel(Channel):
    def send(self, to, subject, body): ...

def send_email(cfg, to, subject, body): ...  # ✓ three functions; the "interface"
def send_sms(cfg, to, message): ...          #   was never used as one
def send_webhook(cfg, payload): ...
```
If you can't name which of (a)/(b)/(c) applies, write a function over a dataclass/dict.

Terser is not the lesson. In the first anchor, a comment was *added* — the load-bearing one.

---

## A — Comments & Documentation

- **comment-why-not-what** — Comment rationale, constraints, gotchas, invariants, units, ticket links; delete comments that restate *or* narrate the adjacent statement (a `# propagate` above a bare `raise`, a `# drop the back` above the eviction it names). _Not:_ never strip a load-bearing *why* (rationale, constraint, units, ticket) just to lower the comment count.
- **fix-code-instead-of-explaining-it** — When tempted to explain *what* code does, first try a clearer name, an explaining variable, or a named constant. _Not:_ inventing a wrapper or hoisting a one-off value just to dodge a comment; a short comment is sometimes clearest.
- **document-public-contract** — Document what crosses a module boundary (params, return, errors, side effects, units, preconditions) so callers needn't read the body; scale detail to caller count. _Not:_ re-narrating the implementation, or documenting trivial private helpers.
- **keep-comments-true-and-dont-duplicate-docs** — A comment that contradicts the code is worse than none; update or delete it on change. Let types carry types, prose carry meaning. _Not:_ deleting a parameter's meaning/units because a type annotation exists.
- **explain-change-rationale-in-commit** — Lead commits/PRs with an imperative summary, then the *why*: the problem, the constraint, why this approach. _Not:_ a trivial, self-evident change needs only the summary line — don't pad mechanical commits with ceremony (or, conversely, ship "fix bug" with no why where one is needed).

## B — Function & Module Shape

- **size-follows-cohesion** — Function size follows cohesion, not a line cap; split when a piece does a separately-nameable job. _Not:_ chopping a coherent flow into trampoline functions to hit a number.
- **split-only-for-clean-abstraction** — Extract a function only when the new unit has a clean, nameable abstraction. If you can't name it well, it isn't a seam. _Not:_ burying a separable, cleanly-nameable concern inline just to avoid a function — if you had to stop and decode the block, extract it.
- **one-level-of-abstraction** — Keep a function at one level of abstraction; don't mix high-level orchestration with low-level fiddling in one body. _Not:_ manufacturing layers as an excuse.
- **deep-modules-no-passthrough** — Prefer deep modules: a simple interface over real functionality. Delete pass-through layers that only forward calls. _Not:_ collapsing a boundary that genuinely earns its keep.
- **pure-seams-explicit-dependencies** — Make dependencies explicit (parameters/injection) and keep core logic pure where practical, so it's testable. _Not:_ a DI framework or interface for a single obvious dependency.

## C — Abstraction Discipline

- **no-premature-abstraction** — Write the concrete code today's requirement needs; the rule of three counts *call sites that need the same behaviour through one signature*, not look-alike implementations. Before an interface/ABC, point to the one consumer that calls all variants uniformly. _Not:_ published APIs, real plugin boundaries with external implementors, a genuine uniform dispatcher, or a test seam whose second implementation already exists.
- **inline-wrong-abstraction** — A wrong abstraction is worse than duplication; when one bends to fit a new case, inline it and re-derive the right seam. _Not:_ inlining a sound abstraction merely because it has one caller today.
- **dry-for-knowledge-not-text** — DRY applies to *knowledge* (one rule, constant, format), not to text that looks similar; don't couple unrelated code to remove duplicate lines. _Not:_ leaving a real business rule copied in two places.
- **solve-todays-problem-yagni** — Build what the requirement needs; drop speculative flags, parameters, and hooks nobody calls. _Not:_ skipping a genuinely committed near-term need.
- **accept-interfaces-small-and-consumer-side** — Accept the smallest interface you use; define interfaces consumer-side, return concrete types. _Not:_ slicing an interface so thin the consumer must juggle several, or omitting one where a real second implementation or test seam already exists.
- **di-and-frameworks-by-need** — Reach for DI containers, decorators, metaprogramming, and frameworks when the problem demands them, not by default. _Not:_ hand-rolling what a framework already in the repo does well.
- **minimal-public-surface** — Export the minimum; keep helpers private so the public surface stays small and changeable. _Not:_ hiding things real external callers need.

## D — Errors & Input Validation

- **validate-at-boundaries-trust-inward** — Validate and parse rigorously *once* at trust boundaries (request, file, env, network), then trust typed values inward. _Not:_ re-validating typed args deep in the stack, normalizing an input the called API already accepts (e.g. wrapping a single class in a tuple for `isinstance`, which takes either), guarding cases that cannot occur, or skipping the boundary check.
- **handle-errors-dont-swallow** — Handle errors that can happen; never swallow them (bare `except`, empty `catch`, discarded error returns). Let real failures propagate to one handler. _Not:_ catch-log-rethrow noise at every level, or treating a benign "not found" as an error.
- **centralize-and-define-out-errors** — Centralize handling at one boundary/middleware; better, design errors out of existence with sane defaults and total functions. _Not:_ hiding a real failure behind a default that returns wrong data.
- **error-types-and-hierarchy** — Start with one error type for the module; add a subtype only when a caller actually branches on it (a different retry path, a mapped status, a distinct message) — the discriminator must exist before the subtype. Wrap with context (`%w`/cause) and put the offending value or id in the message (`%q`/`%d`/repr) so one log line is debuggable. _Not:_ a deep taxonomy for a script, error types nobody catches, restating the sentinel's own text with no added data, or logging secrets/PII/unbounded payloads.
- **guard-clauses-happy-path** — Use guard clauses and early returns to keep the happy path flat. _Not:_ early returns that skip required cleanup, or so many the flow is hard to follow.
- **bound-the-unbounded** — Bound the unbounded: timeouts on I/O, limits on retries, pagination, buffers, recursion. _Not:_ arbitrary tiny limits that break legitimate large inputs.
- **exhaustive-variant-handling** — Handle every variant of an enum/union exhaustively; make the compiler catch new cases (TS `never`, no additions-hiding default). _Not:_ forcing an exhaustive switch onto a genuinely open, caller-extended set where polymorphism fits better, or standing up exhaustiveness machinery for two fixed cases.

## E — Reuse & Idiom

- **reuse-stdlib-and-existing-utilities** — Reach for the stdlib and existing in-repo utilities before writing your own. _Not:_ pulling a heavy dependency for a trivial one-liner.
- **useful-defaults-and-zero-values** — Make defaults and zero values useful so the common path needs no configuration. _Not:_ a default that silently masks a misconfiguration that should fail loudly.

## F — Naming & Clarity

- **name-scaled-to-scope** — Scale name length to scope: short in tight loops, descriptive across wide scope; let names carry intent so comments needn't. _Not:_ cryptic one-letters in wide scope, or type-echoing noise like `userListArray`.
- **prefer-clear-over-clever** — Prefer the clear form over the clever one; readability at read-time beats brevity at write-time. _Not:_ "clear" as license for plodding repetition — unrolling a fine one-liner into noise is also a failure.
- **types-at-boundaries-no-escape-hatches** — Type the boundaries precisely; avoid escape hatches (`any`, `as any`, `@ts-ignore`, `interface{}` everywhere). _Not:_ elaborate generics where a simple type or one localized, commented cast is clearer.

## G — Fitting In & Scope

- **match-surrounding-style** — Read 2–3 neighboring files and mirror their naming, error style, logging, imports, and comment density; local consistency outranks your preferences and any generic house style. _Not:_ propagating a genuinely broken or unsafe local pattern — fix that deliberately.
- **scope-refactors-chestertons-fence** — Keep the diff scoped to the task; don't rewrite working code you merely touched, and don't delete a guard/check you don't understand. _Not:_ dodging a refactor the task actually requires.
- **information-hiding-stable-boundaries** — Hide implementation details behind stable boundaries so modules change internals without rippling. _Not:_ over-engineering boundaries for code with no second consumer.

---

## Language context

Most rules transfer; a few bind to language:

- **exhaustive-variant-handling** — exhaustiveness + `never` are TS/Rust; in Go, write explicit case checks.
- **error-types-and-hierarchy** — class hierarchies in Python/TS; in Go, error *values* wrapped with `%w` and matched via `errors.Is/As`.
- **types-at-boundaries** — Python/TS are gradually typed (annotate the edges); Go is statically typed (avoid `interface{}` sprawl).
- **useful-defaults-and-zero-values** — the *judgment* is universal; Go's usable zero values are the idiomatic expression of it.

## Building something new (greenfield)

No neighbours to match, and an open-ended "build a system" prompt is where models pile up scaffolding. Two rules:

**Default to functions over data; make every type earn its place.** For each class, ABC/Protocol, interface, Enum, or exception subtype, state its justification in one line — its mutable state, its uniform dispatcher, its second caller, or the caller that branches on it. If you can't, downgrade: class→function over a dataclass/dict, Enum→string literals + an exhaustive check, exception subtype→one error type, ABC→plain functions.

**Reducing abstraction ≠ reducing expressiveness.** Cut *speculative indirection* (interfaces for one impl, hooks nobody calls, `Manager`/`Service` pass-throughs) — never the substance. On a new system the floor is not zero:
- still document what crosses each module boundary and keep load-bearing *why* comments;
- still validate trust boundaries and bound I/O (timeouts, limits) from the first commit;
- still keep the error discrimination callers need, and never swallow;
- 3+ real variants with divergent state **do** get modelled (union/enum + exhaustive handling, or polymorphism) — that's concrete, not premature;
- it isn't one God function — cohesion still sets size;
- names stay descriptive; set one set of conventions in the first files and stay internally consistent.

## Before you finish an edit

1. You read 2–3 neighboring files and matched their style. (`match-surrounding-style`)
2. The diff is scoped to the task — no opportunistic rewrites, no removed guards you can't explain. (`scope-refactors-chestertons-fence`)
3. Every class, ABC/Protocol, Enum, and exception subtype you introduced has a one-line justification (mutable state it guards / a uniform dispatcher / a second caller / a caller that branches on it) — or you downgraded it.
4. You ran the project formatter: `gofmt` / `prettier` / `black` / `ruff`.
5. Optional self-check: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/measure.py <changed-paths>` — or `/good-code:measure`. Read the numbers as tripwires, never targets.

## Do not overcorrect

These are the opposite-pole failures the when-NOT guards exist to prevent. If a change introduces any of them, the rule was misapplied:

- stripped a rationale/gotcha comment to lower the comment count
- cryptic single-letter names in wide scope
- swallowed an error to remove a `try`/`catch`
- dropped boundary validation in the name of simplicity
- collapsed a useful module into pass-through trampolines, or inlined a sound abstraction
- deleted a guard or check you didn't understand
- replaced a precise type with `any` to make an error go away
- a `Manager`/`Service`/`Handler` whose methods each just forward to one collaborator (pass-through wrapper)
- a class hierarchy or ABC whose "shared" method takes different arguments per implementation (a fake interface)
- on greenfield: dropped contract docs, boundary validation, or error discrimination because the code is "new", or collapsed a coherent system into one God function

**The target is what a thoughtful reviewer couldn't tell was machine-written — not the shortest diff.**
