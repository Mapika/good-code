# good-code — Reference

Full rationale for every rule in the skill. Loaded on demand; `SKILL.md` carries the condensed, always-on version. Each rule is framed as a **judgment** (when to apply / when NOT) because the failure being fixed is *miscalibrated expressiveness*, not "too much" or "too little" of anything. Worked before→after examples in Python/TS/Go live under `examples/`.

Source of truth: distilled and adversarially critiqued from clean OSS backends + engineering books. `contested` marks rules where respected experts genuinely disagree (the eval should test both poles).

## A — Comments & Documentation

### 1. `comment-why-not-what`  · _contested_

Comment the WHY, not the WHAT. Add a comment only when it carries information the code cannot express: rationale, intent, a non-obvious tradeoff, an external constraint, a gotcha, an invariant, units, or a link to a ticket/spec. Delete comments that merely restate the adjacent line. This is judgment about selectivity, not volume: a load-bearing why-comment is high value and must be kept.

- **Apply when:** Inside function bodies in any language; whenever a reader could not reconstruct the reason for a line from the code itself (workarounds, surprising ordering, business rules, external-system quirks).
- **NOT when (overcorrection guard):** When the comment paraphrases what the next line literally does, or when a better name/extraction would make the code self-explanatory. Do not strip rationale comments to chase minimalism.
- **Replaces (LLM anti-pattern):** Over-commenting / narrating obvious code line-by-line (the single most prevalent LLM tell; OX found redundant comments in 90-100% of AI repos), and the overcorrection of stripping all comments into cryptic code.
- **Sources:** https://google.github.io/eng-practices/review/reviewer/looking-for.html · https://peps.python.org/pep-0008/ · https://google.github.io/styleguide/pyguide.html · https://github.com/cockroachdb/cockroach/blob/master/docs/style.md
- **Examples:** [`examples/A-comments-and-docs/comment-why-not-what.md`](examples/A-comments-and-docs/comment-why-not-what.md)


### 2. `fix-code-instead-of-explaining-it`

If you need a comment to explain WHAT unclear code does, prefer fixing the code (rename, extract, introduce an explaining variable or named constant) over annotating it. Reserve explanatory what-comments for genuinely irreducible complexity (regex, bit tricks, hot-path algorithms), and signal-boost easily-misread lines.

- **Apply when:** When a block needs a paraphrase to be understood, or a magic number/expression needs a unit or meaning; turn the comment into a name or a named constant.
- **NOT when (overcorrection guard):** When the logic is genuinely non-obvious and no name can capture it (e.g. a clever bit trick or an inverted check) — there, a short clarifying comment is correct and expected.
- **Replaces (LLM anti-pattern):** Pairing cryptic code with a paraphrase comment instead of making the code self-documenting; reflexive `# 30 days in seconds` annotations on magic numbers.
- **Sources:** https://google.github.io/eng-practices/review/reviewer/looking-for.html · https://refactoring.guru/smells/comments · https://www.workingsoftware.dev/summary-of-tidy-first-book/ · https://google.github.io/styleguide/pyguide.html
- **Examples:** [`examples/A-comments-and-docs/fix-code-instead-of-explaining-it.md`](examples/A-comments-and-docs/fix-code-instead-of-explaining-it.md)


### 3. `document-public-contract`

Document the public contract of exported/published symbols (functions, classes, interfaces, enums, HTTP handlers): what callers get, parameters, return value, side effects, errors raised, preconditions, units, concurrency, and zero-value behavior — stated so a caller need not read the body. Keep implementation/algorithm detail out of the interface comment. Scale length to how many callers depend on the contract; skip doc comments on small private helpers whose name and signature already say everything. Use the host convention (imperative-mood docstrings/PEP 257, JSDoc/TSDoc, godoc beginning with the symbol name).

- **Apply when:** On anything crossing a module boundary, especially backend libraries, SDKs, and shared service modules.
- **NOT when (overcorrection guard):** On trivial one-line private helpers, or when the doc would just restate the identifier; do not re-narrate the implementation in a contract comment.
- **Replaces (LLM anti-pattern):** Either skipping the contract entirely, or writing a docstring that re-narrates the loop body / restates the type already in the signature.
- **Sources:** https://peps.python.org/pep-0257/ · https://go.dev/doc/comment · https://github.com/microsoft/vscode/wiki/Coding-Guidelines · https://www.mattduck.com/2021-04-a-philosophy-of-software-design.html
- **Examples:** [`examples/A-comments-and-docs/document-public-contract.md`](examples/A-comments-and-docs/document-public-contract.md)


### 4. `keep-comments-true-and-dont-duplicate-docs`

Any comment or doc you write must stay true to the code; a comment that contradicts the code is worse than none. Do not duplicate machine-checkable facts (types the signature already states) or copy a full parameter-doc block across near-identical functions — document parameters once on the canonical function and point variants to it.

- **Apply when:** In typed codebases (let annotations carry types; prose carries meaning the types cannot); when writing sibling/wrapper functions that share a parameter set.
- **NOT when (overcorrection guard):** In untyped code the type belongs in the docstring; a tiny self-contained function needs no cross-reference.
- **Replaces (LLM anti-pattern):** Restating types in prose ('timeout: an integer of seconds'), regenerating the entire param block on every sibling function, and stale comments that diverge from the logic.
- **Sources:** https://peps.python.org/pep-0008/ · https://raw.githubusercontent.com/encode/httpx/master/httpx/_api.py · https://google.github.io/styleguide/go/decisions
- **Examples:** [`examples/A-comments-and-docs/keep-comments-true-and-dont-duplicate-docs.md`](examples/A-comments-and-docs/keep-comments-true-and-dont-duplicate-docs.md)


### 5. `explain-change-rationale-in-commit`

Write commit/PR descriptions to explain WHY (the problem and the chosen approach), not just a vague WHAT. Use an imperative one-line summary, then a body giving rationale. This extends the why-not-what principle to the durable record where reasoning is preserved.

- **Apply when:** Every commit and PR body in a backend repo, especially non-trivial changes.
- **NOT when (overcorrection guard):** Truly mechanical, self-evident changes need only the summary line; don't pad with ceremony.
- **Replaces (LLM anti-pattern):** Empty/vague messages ('Fix bug', 'Update', 'Phase 1') that carry no information.
- **Sources:** https://google.github.io/eng-practices/review/developer/cl-descriptions.html
- **Examples:** [`examples/A-comments-and-docs/explain-change-rationale-in-commit.md`](examples/A-comments-and-docs/explain-change-rationale-in-commit.md)


## B — Function & Module Shape

### 6. `size-follows-cohesion`  · _contested_

Function and module length is an OUTPUT of cohesion, not a target. Do not split code to hit a line/'one screen' limit, and do not grow a function with multiple unrelated concerns. The unit is right-sized when it expresses one coherent idea at one level of abstraction; the line count then follows.

- **Apply when:** Whenever deciding whether a function is 'too long' or 'too short' — judge by whether it does one coherent thing, not by counting lines. A cohesive 40-150 line function with a simple signature is fine.
- **NOT when (overcorrection guard):** Do not use this to justify a 300-line function mixing parsing, I/O, and business rules; genuinely distinct concerns still warrant separation.
- **Replaces (LLM anti-pattern):** Clean Code's hard 2-4 line target driving tiny-function disease, and the opposite god-function dumping ground. (McConnell: routines up to ~100-200 lines are not more error-prone.)
- **Sources:** https://milkov.tech/assets/psd.pdf · https://cbarrete.com/carmack.html · https://github.com/johnousterhout/aposd-vs-clean-code · https://nikola-breznjak.com/blog/books/programming/code-complete-2-steve-mcconnell-high-quality-routines/
- **Examples:** [`examples/B-function-and-module-shape/size-follows-cohesion.md`](examples/B-function-and-module-shape/size-follows-cohesion.md)


### 7. `split-only-for-clean-abstraction`  · _contested_

Extract a piece into its own function only when the result is a clean, INDEPENDENT abstraction: a reader can understand the child without reading the parent, and vice versa. The trigger to extract is the gap between intention and implementation (you had to stop and figure out what a block does, or you were about to write a what-comment), not line count. If the pieces can only be understood together — they thread shared mutable state in a fixed order — keep them inline as a visible sequence.

- **Apply when:** When a block has a meaningful name that reveals more than the code, removes real duplication, or names a non-obvious operation; when steps are pure (value in, value out).
- **NOT when (overcorrection guard):** When the helper shares many of the caller's locals / mutates shared self-state, is called exactly once, and forces the reader to flip back and forth (conjoined methods) — inline it. Do not extract a trivial rename of one obvious line.
- **Replaces (LLM anti-pattern):** 'Extract till you drop' producing lasagna code and single-use passthrough helpers that scatter a linear flow across files.
- **Sources:** https://github.com/johnousterhout/aposd-vs-clean-code/blob/main/README.md · https://milkov.tech/assets/psd.pdf · https://refactoring.guru/smells/long-method · https://github.com/cybran77/refactoring-2nd-edition
- **Examples:** [`examples/B-function-and-module-shape/split-only-for-clean-abstraction.md`](examples/B-function-and-module-shape/split-only-for-clean-abstraction.md)


### 8. `one-level-of-abstraction`

Keep a single function at one level of abstraction: do not mix high-level orchestration with low-level byte/string/transport fiddling in the same body. A change in altitude is the principled reason to extract (pushing detail down behind a named call), as opposed to splitting on line count.

- **Apply when:** When a function interleaves domain logic with low-level mechanics; push the mechanics one level down behind a descriptive call so the body reads at a consistent altitude.
- **NOT when (overcorrection guard):** Do not weaponize this into 2-line trampolines; pair it with the deep-module test so the extracted unit genuinely hides complexity.
- **Replaces (LLM anti-pattern):** God-functions that mix concerns, AND pointless trampolines created by splitting on length.
- **Sources:** https://qntm.org/clean · https://gerlacdt.github.io/blog/posts/clean_code/ · https://google.github.io/styleguide/go/best-practices.html
- **Examples:** [`examples/B-function-and-module-shape/one-level-of-abstraction.md`](examples/B-function-and-module-shape/one-level-of-abstraction.md)


### 9. `deep-modules-no-passthrough`

Judge a module/function by its interface-to-functionality ratio (depth): prefer a simple interface hiding substantial implementation over a shallow unit whose interface is nearly as complex as its body. Delete pass-through methods and pass-through variables — a layer that only forwards to another with essentially the same signature adds interface complexity and hides nothing. Keep a layer only when it adds real behavior (validation, authz, transactions, mapping, caching) or is a deliberate seam (port/adapter, proxy, test boundary).

- **Apply when:** At service/library boundaries and layered backends (controller -> service -> repository); before adding any wrapper, ask whether it lets callers ignore real complexity.
- **NOT when (overcorrection guard):** When the forwarding layer transforms something or is a genuine abstraction/test seam — that is not a pass-through. Library/framework public APIs may keep a stable thin facade deliberately.
- **Replaces (LLM anti-pattern):** Classitis: swarms of one-method classes, single-implementation interfaces 'for mocking', and ceremonial service wrappers that just delegate to a repository.
- **Sources:** https://milkov.tech/assets/psd.pdf · https://www.mattduck.com/2021-04-a-philosophy-of-software-design.html · https://refactoring.guru/smells/middle-man · https://go.dev/wiki/CodeReviewComments
- **Examples:** [`examples/B-function-and-module-shape/deep-modules-no-passthrough.md`](examples/B-function-and-module-shape/deep-modules-no-passthrough.md)


### 10. `pure-seams-explicit-dependencies`

When you keep code behind a function boundary, make its dependencies explicit: pass state in as parameters and return results, prefer pure functions, and avoid reading or mutating hidden global/shared-mutable state. The real enemy is hidden dependency and state mutation, not function count — a boundary is fine when its seam is pure, harmful when functions communicate through hidden state. Never reduce an argument count by promoting parameters to mutable instance/static state.

- **Apply when:** Designing function/module seams in backends (pure core / imperative shell, dependency injection, avoiding module-level mutable singletons); when a function reads only a piece or two of global state, pass it in.
- **NOT when (overcorrection guard):** Genuinely stateful objects with a coherent lifecycle are fine; this targets hidden/ambient state, not all state.
- **Replaces (LLM anti-pattern):** Hiding parameters as mutable class/global state (breaks command-query separation, thread-safety, testability — e.g. Clean Code's PrimeGenerator), spooky action at a distance.
- **Sources:** https://cbarrete.com/carmack.html · https://pwn.ersh.io/notes/john_carmack__inlining_code/ · https://bugzmanov.github.io/cleancode-critique/clean_code_second_edition_review.html · https://peps.python.org/pep-0020/
- **Examples:** [`examples/B-function-and-module-shape/pure-seams-explicit-dependencies.md`](examples/B-function-and-module-shape/pure-seams-explicit-dependencies.md)


## C — Abstraction Discipline

### 11. `no-premature-abstraction`

Write the concrete code the current requirement needs; introduce an abstraction (interface, base class, factory, strategy hook, generic helper, config flag) only when there are 2+ real call sites today or a committed near-term need (rule of three). When in doubt, inline and let the second real use reveal the right seam. Do not design the reusable API up front from zero or one example.

- **Apply when:** Backend service code, especially where speculative interfaces and plugin scaffolding proliferate; abstract at the second genuine use.
- **NOT when (overcorrection guard):** Published library/framework APIs and real plugin boundaries where external implementors exist may justify designing the seam before all in-tree call sites — but do so deliberately, accepting the guessing risk.
- **Replaces (LLM anti-pattern):** Premature/unnecessary abstraction: single-implementation interfaces, strategy/factory patterns for one concrete case, over-parameterized functions with options nobody calls.
- **Sources:** https://caseymuratori.com/blog_0015 · https://refactoring.guru/smells/speculative-generality · https://google.github.io/eng-practices/review/reviewer/looking-for.html · https://grugbrain.dev/
- **Examples:** [`examples/C-abstraction-discipline/no-premature-abstraction.md`](examples/C-abstraction-discipline/no-premature-abstraction.md)


### 12. `inline-wrong-abstraction`

Treat proliferating boolean/mode parameters and branching inside a shared function as the signal that the abstraction is wrong. The fix is to inline it back to the call sites and re-derive, sharing only the truly-common core — not to add another flag. Prefer duplication over the wrong abstraction.

- **Apply when:** During refactors/maintenance when callers pass flags to make shared code handle their special case and the body fills with if/else per caller.
- **NOT when (overcorrection guard):** When the function captures genuinely shared knowledge that must change in lockstep — keep it unified (see DRY-for-knowledge).
- **Replaces (LLM anti-pattern):** DRY-ing two superficially-similar blocks into a flag-driven god-function and then perpetually patching it.
- **Sources:** https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction · https://kentcdodds.com/blog/aha-programming · https://gerlacdt.github.io/blog/posts/clean_code/
- **Examples:** [`examples/C-abstraction-discipline/inline-wrong-abstraction.md`](examples/C-abstraction-discipline/inline-wrong-abstraction.md)


### 13. `dry-for-knowledge-not-text`

Apply DRY to knowledge, not to text. Deduplicate when a single rule, constant, validation, or wire format must change in lockstep (one authoritative representation). Tolerate incidental/coincidental duplication of code that merely looks alike, and prefer a little copying over a little coupling. A bug fixed in one copy must not silently survive in clones.

- **Apply when:** When you spot a real shared rule (tax calc, business constant, schema) — unify it. When two small blocks coincidentally match — leave them.
- **NOT when (overcorrection guard):** Do not merge unrelated callers behind a shared helper just because the lines resemble each other (that creates the wrong abstraction).
- **Replaces (LLM anti-pattern):** Copy-paste sprawl of real logic (GitClear: 8x rise in 5+ line duplicate blocks; arXiv: 30.7% LLM repetition vs 3.8% human) AND over-DRYing incidental similarity.
- **Sources:** https://github.com/HugoMatilla/The-Pragmatic-Programmer/blob/master/readme.md · https://go-proverbs.github.io/ · https://www.jonas.rs/2025/02/09/report-summary-gitclear-ai-code-quality-research-2025.html · https://arxiv.org/html/2504.12608v1
- **Examples:** [`examples/C-abstraction-discipline/dry-for-knowledge-not-text.md`](examples/C-abstraction-discipline/dry-for-knowledge-not-text.md)


### 14. `solve-todays-problem-yagni`

Solve the problem you actually have now, not a speculated future one. Don't add config knobs, parameters, extension hooks, or generality with no current caller; pick a sensible internal default and pull complexity downward so a simple interface absorbs the hard part once, instead of exposing options every caller must understand. Add a parameter only when a real caller needs to vary it.

- **Apply when:** Whenever tempted to add 'flexibility' — flags, options, generic mechanisms, plugin registries — for hypotheticals; favor the simplest construct (a plain loop over a generic Map used once).
- **NOT when (overcorrection guard):** When two real callers genuinely need different behavior, the option is legitimate; framework/library extension points with real external users are justified.
- **Replaces (LLM anti-pattern):** Speculative generality / over-engineering; over-parameterized signatures where every call site passes the same args; reflection/DSLs/generics for a single concrete use.
- **Sources:** https://google.github.io/eng-practices/review/reviewer/looking-for.html · https://www.mattduck.com/2021-04-a-philosophy-of-software-design.html · https://go-proverbs.github.io/ · https://accu.org/journals/overload/30/167/teodorescu/
- **Examples:** [`examples/C-abstraction-discipline/solve-todays-problem-yagni.md`](examples/C-abstraction-discipline/solve-todays-problem-yagni.md)


### 15. `accept-interfaces-small-and-consumer-side`

Depend on abstractions lazily and minimally: accept interfaces, return concrete types, and define an interface at the consumer that needs it, declaring only the methods it actually uses. The bigger the interface, the weaker the abstraction — prefer one- or two-method interfaces named for the behavior. Don't define interfaces on the implementer side 'for mocking' or introduce one before a real second implementation or test seam exists.

- **Apply when:** Go especially (structural interfaces), and analogously anywhere applying dependency inversion / interface segregation; a function that only reads should take a Reader, not a 12-method God-interface.
- **NOT when (overcorrection guard):** When a real second implementation or genuine test seam exists, the interface is justified; published APIs may expose a deliberate interface.
- **Replaces (LLM anti-pattern):** Wrapping every struct in a single-implementation interface, and fat God-interfaces that are hard to satisfy and test.
- **Sources:** https://go.dev/wiki/CodeReviewComments · https://go-proverbs.github.io/ · https://go.dev/doc/effective_go · https://google.github.io/styleguide/go/decisions
- **Examples:** [`examples/C-abstraction-discipline/accept-interfaces-small-and-consumer-side.md`](examples/C-abstraction-discipline/accept-interfaces-small-and-consumer-side.md)


### 16. `di-and-frameworks-by-need`  · _contested_

Default to plain functions/modules with explicit dependencies passed as arguments; introduce DI containers, decorator wiring, and heavy layered provider frameworks only when team size and scale genuinely call for it. Frameworks earn their keep in very large, multi-team codebases — this is a default, not an absolute.

- **Apply when:** Most backend services: pass the db/client/dependency explicitly to the function that needs it.
- **NOT when (overcorrection guard):** Large, multi-team systems where a DI framework's wiring and lifecycle management genuinely pay off; or an existing codebase already standardized on one (match it).
- **Replaces (LLM anti-pattern):** Reaching for NestJS-style @Injectable/@Module/@Inject wiring (and ~25x slower startup, anecdotal) for a service that a plain function would serve.
- **Sources:** https://github.com/nestjs/nest/issues/12620 · https://www.wwt.com/article/nestjs-101 · https://orm.drizzle.team/docs/overview
- **Examples:** [`examples/C-abstraction-discipline/di-and-frameworks-by-need.md`](examples/C-abstraction-discipline/di-and-frameworks-by-need.md)


### 17. `minimal-public-surface`

Keep the public/exported surface minimal: don't export functions, types, or symbols not actually shared across modules — a speculatively wide surface is a form of premature abstraction and is harder to change later. (Language-specific form in TS/JS: prefer top-level `function foo()` over `export const foo = () => {}` for better stack traces and hoisting.)

- **Apply when:** When deciding visibility; export only what a second module genuinely consumes, keep the rest local.
- **NOT when (overcorrection guard):** Library/framework public APIs intentionally export their documented surface; don't hide what is meant to be the contract.
- **Replaces (LLM anti-pattern):** Exporting helpers used in only one file 'just in case', widening the API surface speculatively.
- **Sources:** https://github.com/microsoft/vscode/wiki/Coding-Guidelines
- **Examples:** [`examples/C-abstraction-discipline/minimal-public-surface.md`](examples/C-abstraction-discipline/minimal-public-surface.md)


## D — Errors & Input Validation

### 18. `validate-at-boundaries-trust-inward`  · _contested_

Validate and parse untrusted input once at the trust boundary (HTTP handler, queue consumer, deserialization, public API edge), converting it into a typed value; then trust that value inward. Do not re-check the same invariant — null/type/range guards — in every internal/private function. Assume the happy path and catch the specific expected failure narrowly (EAFP) rather than pre-checking conditions the types already guarantee.

- **Apply when:** At system edges (parse/validate rigorously there); inside the system, rely on the types and contracts already established.
- **NOT when (overcorrection guard):** Boundary validation itself is still required — do not drop it. Genuinely-invalid internal states (real 'should never happen' that would corrupt data) may warrant an assertion.
- **Replaces (LLM anti-pattern):** Defensive bloat: scattering isinstance/None/typeof guards through the whole call stack, re-validating typed args, and blanket try/except on impossible states (OX: phantom-edge-case logic in 70-80% of repos).
- **Sources:** https://colinhacks.com/essays/zod · https://docs.python.org/3/glossary.html · https://www.eyrie.org/~eagle/reviews/books/0-7356-1967-0.html · https://noenthuda.substack.com/p/why-llms-write-horrible-code
- **Examples:** [`examples/D-errors-and-validation/validate-at-boundaries-trust-inward.md`](examples/D-errors-and-validation/validate-at-boundaries-trust-inward.md)


### 19. `handle-errors-dont-swallow`

Never swallow errors (bare except + pass, empty catch, discarded error return, or a default that hides failure). Catch only what you can actually act on: recover, retry, or add context and re-raise; otherwise let it propagate. Handle each error once (log OR return, not both). Catch the narrowest type you can handle, at the layer that can do something about it.

- **Apply when:** Backend services everywhere errors cross I/O, network, or domain boundaries; catch locally only to recover, translate to a domain error, or add context.
- **NOT when (overcorrection guard):** Do not wrap every call in try/catch-log-rethrow (duplicate logs, buried happy path); do not catch broad Exception just to continue.
- **Replaces (LLM anti-pattern):** Under-handling (silent swallow making bugs invisible for months) AND defensive per-layer try/catch bloat. (TigerBeetle: 92% of catastrophic failures stem from mishandled non-fatal errors.)
- **Sources:** https://go.dev/wiki/CodeReviewComments · https://github.com/goldbergyoni/nodebestpractices/blob/master/sections/errorhandling/centralizedhandling.md · https://peps.python.org/pep-0020/ · https://bugzmanov.github.io/cleancode-critique/clean_code_second_edition_review.html
- **Examples:** [`examples/D-errors-and-validation/handle-errors-dont-swallow.md`](examples/D-errors-and-validation/handle-errors-dont-swallow.md)


### 20. `centralize-and-define-out-errors`

Reduce the number of places that can fail. First, define errors out of existence where the case is genuinely benign — redesign the interface so a common 'error' becomes ordinary behavior (idempotent delete, clamping accessor). For real errors, handle them in as few places as possible: mask low and resolve, or aggregate at one boundary (request middleware, top-of-request mapping), rather than a handler at every call site. Add only context the underlying error lacks; don't echo what it already says.

- **Apply when:** When the same error response is produced uniformly across many call sites (route it to one boundary handler); when a special case is harmless and can be folded into normal behavior.
- **NOT when (overcorrection guard):** Do not collapse real, unrecoverable, or security-relevant failures into silence; handle locally when recovery is genuinely call-site-specific. Don't hide a real error just to remove a branch.
- **Replaces (LLM anti-pattern):** Per-layer try/except around every call; redundant error wrapping ('failed to X: failed to Y: failed to Z'); raising for benign common cases forcing every caller to guard.
- **Sources:** https://www.mattduck.com/2021-04-a-philosophy-of-software-design.html · https://github.com/goldbergyoni/nodebestpractices/blob/master/sections/errorhandling/centralizedhandling.md · https://google.github.io/styleguide/go/best-practices.html · https://raw.githubusercontent.com/uber-go/guide/master/style.md
- **Examples:** [`examples/D-errors-and-validation/centralize-and-define-out-errors.md`](examples/D-errors-and-validation/centralize-and-define-out-errors.md)


### 21. `error-types-and-hierarchy`

Throw the language's standard error type (never a string or bare object), and carry context as structured fields on the exception, not stuffed into the message. For a library/service, give it a small single-rooted exception hierarchy (one base all others subclass) so callers can catch broadly or narrowly; keep each exception's docstring to one descriptive line. Avoid both bare/blanket exceptions and a sprawling class-per-condition hierarchy.

- **Apply when:** Backend libraries and services that surface errors to callers (most OO/exception-based languages: Python, TS/Node, Java).
- **NOT when (overcorrection guard):** In Go and other error-as-value languages, return error values with wrapping (%w) instead of an exception hierarchy. Don't invent many unrelated exception types for an app that needs one AppError with fields.
- **Replaces (LLM anti-pattern):** Raising bare Exception/strings (loses stack trace, inconsistent shape) and over-engineered deep error hierarchies.
- **Sources:** https://raw.githubusercontent.com/psf/requests/main/src/requests/exceptions.py · https://github.com/goldbergyoni/nodebestpractices/blob/master/sections/errorhandling/useonlythebuiltinerror.md
- **Examples:** [`examples/D-errors-and-validation/error-types-and-hierarchy.md`](examples/D-errors-and-validation/error-types-and-hierarchy.md)


### 22. `guard-clauses-happy-path`

Handle preconditions, edge cases, and errors first with early returns so the happy path stays at minimal indentation and reads top-to-bottom. Drop the else after a terminating branch. Use guards for exceptional/invalid cases — not as a license to scatter returns through genuine, equally-weighted branching logic.

- **Apply when:** Request handlers and any function with validation + error checks; especially idiomatic in Go (`if err != nil { return }`).
- **NOT when (overcorrection guard):** When both branches are equally important domain logic of the same weight, a symmetric if/else is clearer than forcing early returns everywhere.
- **Replaces (LLM anti-pattern):** Deeply nested arrow-code / pyramid of null-and-exists checks, and the unnecessary else LLMs emit after a return.
- **Sources:** https://go.dev/wiki/CodeReviewComments · https://refactoring.com/catalog/replaceNestedConditionalWithGuardClauses.html · https://raw.githubusercontent.com/uber-go/guide/master/style.md · https://henrikwarne.com/2024/01/10/tidy-first/
- **Examples:** [`examples/D-errors-and-validation/guard-clauses-happy-path.md`](examples/D-errors-and-validation/guard-clauses-happy-path.md)


### 23. `bound-the-unbounded`

Put a bound on anything that can grow without limit — retry loops, queues, batch sizes, pagination, request fan-out — and assert the few invariants that catch real bugs. Calibrate intensity to the domain: bound the unbounded everywhere, but don't import safety-critical assertion density (two asserts per function, assert the negative space) into ordinary CRUD services.

- **Apply when:** Backend services where unbounded retries/queues/pagination cause real outages; replace open-ended loops with explicit caps that fail loudly when exhausted.
- **NOT when (overcorrection guard):** Don't carpet ordinary service code with assertions for impossible states (that is defensive bloat); reserve assertions for invariants whose violation signals a genuine bug.
- **Replaces (LLM anti-pattern):** Unbounded `while not done` retry/poll loops, and the opposite overcorrection of TigerBeetle-grade assertion noise in normal services.
- **Sources:** https://github.com/tigerbeetle/tigerbeetle/blob/main/docs/TIGER_STYLE.md
- **Examples:** [`examples/D-errors-and-validation/bound-the-unbounded.md`](examples/D-errors-and-validation/bound-the-unbounded.md)


### 24. `exhaustive-variant-handling`

Model a closed set of variants as a tagged/discriminated union and handle them with an exhaustive switch plus a compile-time `never`/exhaustiveness check, so the compiler flags any unhandled case when a variant is added. Prefer this over speculative runtime defensive branches for 'impossible' cases. For a closed, small, never-extended set, a switch over an enum is clearer (and faster) than introducing a class hierarchy or virtual dispatch.

- **Apply when:** TypeScript/Rust/Swift/Kotlin with tagged unions; backend code dispatching over a known, finite kind/enum where the compiler can enforce completeness.
- **NOT when (overcorrection guard):** When the set is genuinely open-ended and callers add new cases without touching existing code, polymorphism/extension is the right tool (open/closed for a real reason). The `never` mechanism is TS-specific.
- **Replaces (LLM anti-pattern):** Silent fall-through (`else return ...`) that becomes wrong when a new variant is added, AND premature polymorphic class hierarchies for two fixed cases.
- **Sources:** https://www.totaltypescript.com/bonuses/typescript-expert-interviews/colin-mcdonnell-talks-about-the-design-choices-behind-zod · https://www.computerenhance.com/p/clean-code-horrible-performance
- **Examples:** [`examples/D-errors-and-validation/exhaustive-variant-handling.md`](examples/D-errors-and-validation/exhaustive-variant-handling.md)


## E — Reuse & Idiom

### 25. `reuse-stdlib-and-existing-utilities`

Before hand-writing a loop, utility, or resource-management boilerplate, check whether the standard library, an already-imported dependency, or an existing project helper does it. Prefer the idiomatic built-in (max/sum/sorted-with-key, set/dict dedup, collections/itertools, context managers, Array methods, Go's slices/maps) and delegate to lower layers. Reimplement only when the built-in genuinely doesn't fit. Route through real named packages, not vague util/common/helper dumping grounds.

- **Apply when:** Whenever the needed operation is a common one (dedup, max, URL parsing, UUIDs, retries, date math, resource cleanup).
- **NOT when (overcorrection guard):** When the stdlib version genuinely doesn't fit the requirement, or pulling a heavy dependency for a tiny stable helper is worse than copying 5 lines (a little copying beats a little dependency).
- **Replaces (LLM anti-pattern):** Reimplementing the stdlib / 'vanilla style coding' (BigCodeBench shows LLMs under-invoke libraries; GitClear shows reuse falling 24.1%->9.5%).
- **Sources:** https://www.helpnetsecurity.com/2025/10/27/ai-code-security-risks-report/ · https://docs.python-guide.org/writing/reading/ · https://google.github.io/styleguide/go/best-practices.html · https://hono.dev/docs
- **Examples:** [`examples/E-reuse-and-idiom/reuse-stdlib-and-existing-utilities.md`](examples/E-reuse-and-idiom/reuse-stdlib-and-existing-utilities.md)


### 26. `useful-defaults-and-zero-values`

Design defaults and zero values so the common case works without setup ceremony, reducing required initialization and null-guarding at call sites. A type whose zero/default state is already valid needs no defensive constructor guard and fewer nil/None checks downstream.

- **Apply when:** When designing constructors, default arguments, and value types (empty-but-usable collections, ready zero-value buffers); the judgment 'make the default path require no setup' transfers across languages even where the mechanism (Go zero values) does not.
- **NOT when (overcorrection guard):** Don't pick a convenient zero value that masks the difference between 'unset' and a legitimate zero when that distinction is semantically required (e.g. price 0 vs no price).
- **Replaces (LLM anti-pattern):** Mandatory constructors/initialization boilerplate plus defensive nil-re-initialization for values that are already valid.
- **Sources:** https://go-proverbs.github.io/ · https://go.dev/doc/effective_go
- **Examples:** [`examples/E-reuse-and-idiom/useful-defaults-and-zero-values.md`](examples/E-reuse-and-idiom/useful-defaults-and-zero-values.md)


## F — Naming & Clarity

### 27. `name-scaled-to-scope`

Name for clarity at the shortest length that is unambiguous in context, scaling length to scope: short names for tight local/loop scopes and generics, descriptive names for exported/long-lived/domain symbols. Don't encode the type, package, or enclosing context into the name (no userDict, no widget.NewWidget, no calculate_total_for_all_items_in_cart inside Cart), don't prefix getters with Get, and avoid both cryptic abbreviations and bureaucratic verbosity. A name that must encode the whole body is a sign of over-extraction.

- **Apply when:** Every identifier; let the namespace/scope carry context. Match the host language's density norm (Go favors very short locals; Python/TS tolerate moderately longer).
- **NOT when (overcorrection guard):** Don't shorten a wide-scope or domain identifier into one-letter soup, and don't lengthen a 3-line loop index past `i`.
- **Replaces (LLM anti-pattern):** Verbose type-echoing/over-qualified names (theListOfActiveUserAccountObjects, send_http_get_request_to_url) AND the overcorrection into cryptic d/lst/tmp.
- **Sources:** https://peps.python.org/pep-0008/ · https://go.dev/wiki/CodeReviewComments · https://google.github.io/styleguide/go/best-practices.html · https://arxiv.org/html/2503.06327v2
- **Examples:** [`examples/F-naming-and-clarity/name-scaled-to-scope.md`](examples/F-naming-and-clarity/name-scaled-to-scope.md)


### 28. `prefer-clear-over-clever`

Optimize for clarity and reader cognition, not for the fewest tokens or the cleverest construct. When a terse expression is hard to read, bind intermediate steps to well-named locals even if it adds lines; 'simple' means not complicated, not 'no complexity'. Express irreducible complexity directly rather than hiding it behind a leaky one-size simplification. Good code is appropriately expressive, not minimal.

- **Apply when:** Whenever a dense one-liner, nested comprehension, clever bit trick, or reflection-based shortcut would be unreviewable; and whenever a domain is genuinely complex (state machines, retries, partial failure) — handle the real cases explicitly.
- **NOT when (overcorrection guard):** Don't inflate trivial code into ceremony either; clarity cuts both ways. A simple, well-understood one-liner needs no expansion.
- **Replaces (LLM anti-pattern):** Cryptic terse one-liners and the overcorrection of 'write less', plus false-simple abstractions that handle 80% and leak the rest into every caller.
- **Sources:** https://go-proverbs.github.io/ · https://peps.python.org/pep-0020/ · https://grugbrain.dev/ · https://github.com/tigerbeetle/tigerbeetle/blob/main/docs/TIGER_STYLE.md
- **Examples:** [`examples/F-naming-and-clarity/prefer-clear-over-clever.md`](examples/F-naming-and-clarity/prefer-clear-over-clever.md)


### 29. `types-at-boundaries-no-escape-hatches`

In gradually-typed languages, put type annotations where they document contracts and catch real errors — public signatures, data models, module boundaries — and let inference handle obvious locals (count = 0, not count: int = 0). Do not silence the type checker with Any/cast/`as any`/non-null `!`; if you must cast at a proven-safe library edge, pair it with a runtime assertion and a justifying comment. Derive types from a single source of truth (infer from the schema) instead of hand-maintaining a parallel type that drifts.

- **Apply when:** Python (type hints) and TypeScript: annotate boundaries, infer locals, validate external shapes before trusting them.
- **NOT when (overcorrection guard):** N/A for Go and other mandatorily-typed languages; in app (non-library) code, fix the types rather than casting. Annotate a local only when inference can't or when it documents a non-obvious shape.
- **Replaces (LLM anti-pattern):** Over-annotating trivial locals (ceremony) AND defeating the type system with Any/cast to make errors disappear; maintaining a duplicate interface alongside a runtime schema.
- **Sources:** https://dagster.io/blog/dignified-python-10-rules-to-improve-your-llm-agents · https://colinhacks.com/essays/zod · https://www.totaltypescript.com/bonuses/typescript-expert-interviews/colin-mcdonnell-talks-about-the-design-choices-behind-zod · https://arxiv.org/html/2503.06327v2
- **Examples:** [`examples/F-naming-and-clarity/types-at-boundaries-no-escape-hatches.md`](examples/F-naming-and-clarity/types-at-boundaries-no-escape-hatches.md)


## G — Fitting In & Scope

### 30. `match-surrounding-style`

Match the surrounding code. Before writing, read 2-3 neighboring files and mirror their established naming, structure, error-handling style (exceptions vs Result vs error returns), logging, import organization, comment density, and formatter/linter config. Consistency with the local module outranks your own stylistic preferences or a generic house style — a reviewer should not be able to tell which lines the model added from style alone.

- **Apply when:** Always, especially when editing an existing repo rather than greenfield code; run the project's formatter (gofmt, prettier, black, ruff).
- **NOT when (overcorrection guard):** When the local pattern is actually broken or unsafe — fix it deliberately and consistently, rather than silently adding a third dialect; don't propagate a genuinely harmful pattern.
- **Replaces (LLM anti-pattern):** Importing a foreign idiom (extra docstrings, defensive checks, renamed locals, print vs logger, throw vs Result) that produces a diff reading as machine-generated.
- **Sources:** https://peps.python.org/pep-0008/ · https://go-proverbs.github.io/ · https://github.com/fastify/fastify/blob/main/CONTRIBUTING.md · https://google.github.io/eng-practices/review/reviewer/standard.html
- **Examples:** [`examples/G-fitting-in-and-scope/match-surrounding-style.md`](examples/G-fitting-in-and-scope/match-surrounding-style.md)


### 31. `scope-refactors-chestertons-fence`

Keep changes scoped to the task. Don't rewrite, restructure, or delete surrounding working code that the task didn't ask you to touch, and don't remove a guard or branch whose purpose you don't yet understand (Chesterton's fence) — the non-obvious branch is often a paid-for bug fix. Prefer small, incremental refactors over big-bang rewrites.

- **Apply when:** Agentic edits in an existing repo: make the requested change and leave unrelated working code alone unless cleanup is in scope.
- **NOT when (overcorrection guard):** When the task is explicitly a refactor/cleanup, or a 'broken window' is directly in the path of the change and fixing it is warranted — do it deliberately, not as silent scope creep.
- **Replaces (LLM anti-pattern):** LLM agents that 'helpfully' restructure error handling, rename a dozen symbols, or delete branches while doing a one-field change (inflates diff and review time).
- **Sources:** https://grugbrain.dev/ · https://pragprog.com/tips/ · https://www.sonarsource.com/blog/the-inevitable-rise-of-poor-code-quality-in-ai-accelerated-codebases/
- **Examples:** [`examples/G-fitting-in-and-scope/scope-refactors-chestertons-fence.md`](examples/G-fitting-in-and-scope/scope-refactors-chestertons-fence.md)


### 32. `information-hiding-stable-boundaries`

Practice information hiding: keep internal data structures and design decisions inside the module; cross a boundary with a stable domain type, not a storage- or transport-shaped one. Two modules must not both depend on the same internal representation, and a change to one module's internals should not force edits in another (information leakage / change amplification).

- **Apply when:** At repository/service boundaries in backends; map rows/ORM models/driver types into domain objects before returning them up the stack.
- **NOT when (overcorrection guard):** Internal-only helpers within the same module can share representation freely; don't add a mapping layer where there is no real boundary.
- **Replaces (LLM anti-pattern):** Returning raw ORM models, DB rows, or driver-specific types from a service up to the HTTP/business layer (leaks the schema and blocks future optimization).
- **Sources:** https://bagerbach.com/books/a-philosophy-of-software-design/ · https://www.mattduck.com/2021-04-a-philosophy-of-software-design.html
- **Examples:** [`examples/G-fitting-in-and-scope/information-hiding-stable-boundaries.md`](examples/G-fitting-in-and-scope/information-hiding-stable-boundaries.md)


## Adjudicated contradictions

Where canonical sources directly conflict, here is how the skill resolves it (these are the load-bearing decisions — e.g. deep modules over many tiny functions):

**Conflict:** Clean Code (Robert C. Martin): functions should be very small (~2-4 lines), 'extract till you drop', many tiny single-purpose functions. vs A Philosophy of Software Design (Ousterhout): prefer DEEP modules (simple interface hiding substantial implementation); 'length by itself is rarely a good reason for splitting up a method'; over-decomposition creates shallow, entangled interfaces.

**Resolution:** Resolved in favor of APOSD as the primary guide, because this directly drives the LLM tiny-function failure mode and because the conflict is adjudicated in Martin's own debate repo where he concedes his PrimeGenerator was hard to re-read, and McConnell's empirical data (routines up to ~100-200 lines not more error-prone) supports it. Synthesis (principles size-follows-cohesion, split-only-for-clean-abstraction, deep-modules-no-passthrough): length is an OUTPUT of cohesion, never a target. KEEP Clean Code's genuinely good sub-rules that survive critique: 'one level of abstraction per function' and intention-revealing names. The extraction test is the intention/implementation gap and whether the child is understandable independently of the parent (not a line count). Marked contested=true on the size and splitting principles. This is judgment, not 'write longer functions' — a 300-line mixed-concern function is still wrong.

---

**Conflict:** Clean Code: 'Comments are always failures'; prefer self-documenting code and delete comments. vs APOSD / Code Complete / PEP 8 / Google: comments capture WHY/intent/units/invariants that code cannot express; missing comments cost far more than the comment.

**Resolution:** Resolved against the absolutist 'comments are failures' framing, which produces BOTH LLM failure poles: narrating-the-obvious AND stripping load-bearing rationale. Synthesis (comment-why-not-what, fix-code-instead-of-explaining-it, document-public-contract, keep-comments-true): the keep/cut test is whether deleting the comment loses information not recoverable from the code. Cut what-comments (or fix the code so they're unneeded); keep why-comments, public API contracts, and annotations on genuinely non-obvious logic. Marked contested=true on comment-why-not-what so the eval penalizes both poles per dimension.

---

**Conflict:** Defensive programming (Code Complete: validate inputs, assert) and single-rooted exception robustness vs simplicity/YAGNI and EAFP/'define errors out of existence' (APOSD, Python glossary, Zod parse-don't-validate).

**Resolution:** Resolved by location, not amount: validate/parse rigorously ONCE at trust boundaries, then trust typed values inward; use assertions only for genuine 'should never happen' invariants, real handling for 'can happen'. This preserves Code Complete's defensive value where it matters (the edge) while killing the LLM defensive-bloat failure (re-validating typed args, guarding impossible states, blanket try/except) inside the system. See validate-at-boundaries-trust-inward (contested=true), handle-errors-dont-swallow, centralize-and-define-out-errors. Both under-handling (silent swallow) and over-defense are penalized.

---

**Conflict:** DRY (Pragmatic Programmer, Clean Code): every piece of knowledge has one authoritative representation; eliminate duplication. vs Sandi Metz / Kent C. Dodds / Go Proverb: 'duplication is far cheaper than the wrong abstraction'; 'a little copying is better than a little dependency'; tolerate duplication (rule of three).

**Resolution:** Resolved by distinguishing knowledge from text. DRY applies to KNOWLEDGE — a single rule/constant/format that must change in lockstep gets one representation (a cloned tax calc is a bug). Incidental/coincidental duplication of code that merely looks alike should be tolerated until a real, stable shared shape emerges (rule of three); merging it prematurely creates the wrong, flag-driven abstraction. See dry-for-knowledge-not-text, no-premature-abstraction, inline-wrong-abstraction. Quantitative evidence (GitClear 8x duplicate blocks, arXiv 30.7% LLM repetition) means the eval must also penalize genuine copy-paste of real logic, not only over-DRYing.

---

**Conflict:** Inlining school (Carmack 'consider inlining single-use functions'; Muratori semantic compression; Acton data-oriented design) and Clean Code anti-switch ('prefer polymorphism') vs backend needs for testability seams, dependency injection, and Muratori-style performance-motivated anti-encapsulation that doesn't transfer to I/O-bound services.

**Resolution:** Resolved by separating the transferable clarity argument from the performance/games-domain argument. KEEP: keep ordered/visible flows linear rather than scattered through deep nesting; inline shallow single-use passthroughs; fight hidden state. REJECT for backend: Carmack's literal 2000-line function as a target, and Acton's anti-encapsulation stance (explicitly cache/performance-motivated; domain modeling/encapsulation are legitimately valuable in business logic). The counterweight is pure-seams-explicit-dependencies: keep the boundary when it aids testability/ownership, but make the seam pure rather than removing it. On polymorphism-vs-switch (exhaustive-variant-handling): switch+exhaustiveness for closed sets, polymorphism only for genuinely open extension. Muratori's 1.5x-25x perf numbers are domain-specific to tight CPU loops and are NOT cited as a reason to avoid abstraction in I/O-bound handlers.

---

**Conflict:** 'Many small classes' / SOLID / DI everywhere (Clean Code culture, NestJS) vs deep classes and 'classitis' warning (APOSD), and accept-interfaces/return-concrete + no-interface-for-mocking (Go).

**Resolution:** Resolved toward deep classes and lazy abstraction: prefer rich behavior behind a small interface over swarms of one-method classes, single-implementation interfaces, and mandatory DI wiring. Extract a class/interface for a real seam (independent reuse, a stable boundary, a genuine second implementation, a real test seam), not to satisfy SRP/DIP per rule. DI frameworks are a default-off choice that earns its keep only at large multi-team scale. See deep-modules-no-passthrough, accept-interfaces-small-and-consumer-side, di-and-frameworks-by-need (contested=true). Caveat preserved: published library APIs and real plugin boundaries legitimately justify an interface with one in-tree implementation.

---
