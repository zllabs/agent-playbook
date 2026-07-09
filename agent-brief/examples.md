# Examples

Sloppy request in. Structured brief out.

## Bug fix

### 1. fix login bug

**Request:** `fix login bug`

```
Task:
Fix the login bug.

Context:
Investigate the authentication flow.

Requirements:

Make minimal changes.
Preserve existing behavior.
Add or update tests if applicable.

Verification:
Run relevant tests.
```

### 2. fix the memory leak

**Request:** `fix the memory leak`

```
Task:
Fix the memory leak.

Context:
Identify what objects or listeners are not being released.

Requirements:

Profile or trace before changing code.
Make the smallest fix that stops the leak.
Do not refactor unrelated modules.

Verification:
Confirm memory usage stabilizes under repeated use.
```

### 3. fix this

**Request:** `fix this`

```
Task:
Fix the issue in the selected code.

Context:
Investigate the selected code and identify the problem.

Requirements:

Find the root cause before changing code.
Make the smallest necessary fix.
Do not modify unrelated files.

Verification:
Run relevant tests and confirm the issue is resolved.
```

## Feature request

### 4. add authentication

**Request:** `add authentication`

```
Task:
Add authentication.

Context:
Implement within the existing application.

Requirements:

Follow existing project patterns.
Reuse current user/session models if present.
Avoid changing unrelated routes or middleware.

Verification:
Confirm login, logout, and protected routes work.
Add or update tests.
```

### 5. add dark mode

**Request:** `add dark mode`

```
Task:
Add dark mode support.

Context:
Extend the existing theme or styling system.

Requirements:

Follow current styling patterns.
Preserve light mode behavior.
Avoid redesigning unrelated UI.

Verification:
Toggle between modes and confirm styles render correctly.
```

### 6. add rate limiting

**Request:** `add rate limiting`

```
Task:
Add rate limiting.

Context:
Apply to the relevant API endpoints.

Requirements:

Inspect existing middleware patterns first.
Preserve current API behavior for normal traffic.
Use project-standard libraries if available.

Verification:
Confirm limits trigger correctly and legitimate requests still succeed.
```

## Refactor

### 7. refactor this

**Request:** `refactor this`

```
Task:
Refactor the selected code.

Context:
Improve structure without changing behavior.

Requirements:

Inspect current implementation first.
Preserve existing behavior.
Make incremental changes.
Do not expand scope beyond this code.

Verification:
Run existing tests and confirm behavior is unchanged.
```

### 8. clean up this file

**Request:** `clean up this file`

```
Task:
Clean up the selected file.

Context:
Improve readability without changing behavior.

Requirements:

Remove dead code and unused imports only where safe.
Do not refactor beyond this file.
Preserve existing behavior.

Verification:
Confirm the project builds and tests pass.
```

## Performance issue

### 9. make API faster

**Request:** `make API faster`

```
Task:
Improve API performance.

Context:
Investigate current API implementation.

Requirements:

Identify bottleneck first.
Preserve existing API behavior.
Measure improvement.

Verification:
Run performance tests.
```

## Migration

### 10. run the migration

**Request:** `run the migration`

```
Task:
Run the pending database migration.

Context:
Use the project's existing migration tooling.

Requirements:

Inspect current migration state first.
Do not modify unrelated schema.
Follow existing migration conventions.

Verification:
Confirm migration applies cleanly and schema is correct.
```

### 11. update the database

**Request:** `update the database`

**Response:** What schema change or migration is needed?

No brief — missing information.

## Debugging unknown error

### 12. app crashes on startup

**Request:** `app crashes on startup`

```
Task:
Debug the startup crash.

Context:
Identify where startup fails and what error is thrown.

Requirements:

Reproduce the crash first.
Inspect logs and stack traces.
Make the smallest fix that restores startup.

Verification:
Confirm the app starts successfully.
```

### 13. something broke in prod

**Request:** `something broke in prod`

```
Task:
Investigate the production issue.

Context:
Determine what changed and what is failing.

Requirements:

Check recent deploys and error logs first.
Do not change unrelated systems.
Preserve existing behavior once fixed.

Verification:
Confirm the reported issue is resolved in production.
```

### 14. fix the payment issue

**Request:** `fix the payment issue`

**Response:** Which payment flow or error should be investigated?

No brief — missing information.

## Skipped — already specific

These requests are clear enough. Agent Brief does not apply.

| Request | Why skipped |
|---------|-------------|
| `rename function foo to bar` | Target and action are explicit |
| `add missing import for lodash` | Exact change is specified |
| `change port to 8080` | Single concrete value change |
| `delete unused component HeaderOld` | Named file and action |
