# Example Corpus Index

96 before→after pairs · 32 principles × ~3 languages · 6 sourced (verified) / rest synthetic.

Each pair tags **sourced** (real repo, URL adversarially fetch-verified) or **synthetic** (idiomatic, no false attribution).

## Verified real-repo sources

- `document-public-contract` (python): https://raw.githubusercontent.com/pallets/flask/main/src/flask/helpers.py
- `keep-comments-true-and-dont-duplicate-docs` (python): https://github.com/encode/httpx/blob/master/httpx/_api.py
- `deep-modules-no-passthrough` (typescript): https://github.com/puppeteer/puppeteer/pull/5826/files#diff-Target.ts
- `error-types-and-hierarchy` (python): https://raw.githubusercontent.com/psf/requests/main/src/requests/exceptions.py
- `error-types-and-hierarchy` (typescript): https://github.com/goldbergyoni/nodebestpractices/blob/master/sections/errorhandling/useonlythebuiltinerror.md
- `explain-change-rationale-in-commit` (go): https://google.github.io/eng-practices/review/developer/cl-descriptions.html

## By theme

### A — comments-and-docs
- [comment-why-not-what](A-comments-and-docs/comment-why-not-what.md) — go,python,typescript
- [fix-code-instead-of-explaining-it](A-comments-and-docs/fix-code-instead-of-explaining-it.md) — go,python,typescript
- [document-public-contract](A-comments-and-docs/document-public-contract.md) — go,python,typescript · 1 sourced
- [keep-comments-true-and-dont-duplicate-docs](A-comments-and-docs/keep-comments-true-and-dont-duplicate-docs.md) — go,python,typescript · 1 sourced
- [explain-change-rationale-in-commit](A-comments-and-docs/explain-change-rationale-in-commit.md) — go,python,typescript · 1 sourced

### B — function-and-module-shape
- [size-follows-cohesion](B-function-and-module-shape/size-follows-cohesion.md) — go,python,typescript
- [split-only-for-clean-abstraction](B-function-and-module-shape/split-only-for-clean-abstraction.md) — go,python,typescript
- [one-level-of-abstraction](B-function-and-module-shape/one-level-of-abstraction.md) — go,python,typescript
- [deep-modules-no-passthrough](B-function-and-module-shape/deep-modules-no-passthrough.md) — go,python,typescript · 1 sourced
- [pure-seams-explicit-dependencies](B-function-and-module-shape/pure-seams-explicit-dependencies.md) — go,python,typescript

### C — abstraction-discipline
- [no-premature-abstraction](C-abstraction-discipline/no-premature-abstraction.md) — go,python,typescript
- [inline-wrong-abstraction](C-abstraction-discipline/inline-wrong-abstraction.md) — go,python,typescript
- [dry-for-knowledge-not-text](C-abstraction-discipline/dry-for-knowledge-not-text.md) — go,python,typescript
- [solve-todays-problem-yagni](C-abstraction-discipline/solve-todays-problem-yagni.md) — go,python,typescript
- [accept-interfaces-small-and-consumer-side](C-abstraction-discipline/accept-interfaces-small-and-consumer-side.md) — go,python,typescript
- [di-and-frameworks-by-need](C-abstraction-discipline/di-and-frameworks-by-need.md) — go,python,typescript
- [minimal-public-surface](C-abstraction-discipline/minimal-public-surface.md) — go,python,typescript

### D — errors-and-validation
- [validate-at-boundaries-trust-inward](D-errors-and-validation/validate-at-boundaries-trust-inward.md) — go,python,typescript
- [handle-errors-dont-swallow](D-errors-and-validation/handle-errors-dont-swallow.md) — go,python,typescript
- [centralize-and-define-out-errors](D-errors-and-validation/centralize-and-define-out-errors.md) — go,python,typescript
- [error-types-and-hierarchy](D-errors-and-validation/error-types-and-hierarchy.md) — go,python,typescript · 2 sourced
- [guard-clauses-happy-path](D-errors-and-validation/guard-clauses-happy-path.md) — go,python,typescript
- [bound-the-unbounded](D-errors-and-validation/bound-the-unbounded.md) — go,python,typescript
- [exhaustive-variant-handling](D-errors-and-validation/exhaustive-variant-handling.md) — go,python,typescript

### E — reuse-and-idiom
- [reuse-stdlib-and-existing-utilities](E-reuse-and-idiom/reuse-stdlib-and-existing-utilities.md) — go,python,typescript
- [useful-defaults-and-zero-values](E-reuse-and-idiom/useful-defaults-and-zero-values.md) — go,python,typescript

### F — naming-and-clarity
- [name-scaled-to-scope](F-naming-and-clarity/name-scaled-to-scope.md) — go,python,typescript
- [prefer-clear-over-clever](F-naming-and-clarity/prefer-clear-over-clever.md) — go,python,typescript
- [types-at-boundaries-no-escape-hatches](F-naming-and-clarity/types-at-boundaries-no-escape-hatches.md) — python,typescript

### G — fitting-in-and-scope
- [match-surrounding-style](G-fitting-in-and-scope/match-surrounding-style.md) — go,python,typescript
- [scope-refactors-chestertons-fence](G-fitting-in-and-scope/scope-refactors-chestertons-fence.md) — go,python,typescript
- [information-hiding-stable-boundaries](G-fitting-in-and-scope/information-hiding-stable-boundaries.md) — go,python,typescript
