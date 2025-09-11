# Go Sentry Implementation Guide

This document explains how we capture and send errors to Sentry in the Go backend.

---

## Error Capture in /products Endpoint

### The Code Flow

```go
func (s *server) handleProducts(w http.ResponseWriter, r *http.Request) {
    hub := sentry.GetHubFromContext(r.Context())
    logger := sentry.NewLogger(r.Context())

    rows, err := s.getProducts(r.Context())
    if err != nil {
        logger.Error().Emitf("Processing /products - error occurred: %v", err)
        hub.CaptureException(fmt.Errorf("products database error: %w", err))
        http.Error(w, "internal server error", http.StatusInternalServerError)
        return
    }

    // ... continue processing ...
}
```

### Error handling patterns in this repo

#### Pattern 1: Handled error (current in `/products`)

```go
rows, err := s.getProducts(r.Context())
if err != nil {
    hub.CaptureException(fmt.Errorf("products database error: %w", err))
    http.Error(w, "internal server error", http.StatusInternalServerError)
    return
}
```

Pros:
- Idiomatic Go error handling
- Full control over HTTP response
- Clear correlation in Sentry (error + trace + logs)

Cons:
- Must remember to call `hub.CaptureException(err)` for error values

#### Pattern 2: Manual panic recovery (used in `/checkout`)

```go
defer func() {
    if err := recover(); err != nil {
        sentry.GetHubFromContext(r.Context()).CaptureException(fmt.Errorf("%v", err))
        http.Error(w, fmt.Sprintf("%v", err), 500)  // Return 500 error
        return
    }
}()
```

What this does:
1. If a panic occurs, the deferred function recovers it
2. Captures the error via the request hub
3. Returns HTTP 500 with a controlled body

Pros:
- Full control over response and cleanup
- Guarantees a 500 on panic paths

Cons:
- More boilerplate than handled errors

### Why We Use Both

**In `/products` - Method 1 (Automatic):**
```go
defer sentry.RecoverWithContext(r.Context())

if err != nil {
    logger.Error().Emitf("Processing /products - error occurred: %v", err)
    hub.CaptureException(err)  // Capture the error
    panic(fmt.Errorf("products database error: %w", err))  // Then panic
}
```

Current usage:
- `/products`: handled error (explicit `hub.CaptureException(err)` + HTTP 500).
- `/checkout`: manual panic recovery to guarantee a 500 and a single capture on the panic path.

### What If No Panic is Thrown?

**Scenario: Developer returns error instead of panicking**

```go
func (s *server) handleProducts(w http.ResponseWriter, r *http.Request) {
    defer sentry.RecoverWithContext(r.Context())
    
    rows, err := s.getProducts(r.Context())
    
    if err != nil {
        // Option A: Just return error (NOT sent to Sentry!)
        http.Error(w, "error", 500)
        return
        
        // Option B: Explicitly capture error (SENT to Sentry)
        hub.CaptureException(err)
        http.Error(w, "error", 500)
        return
    }
}
```

**The key point:**
- **`sentry.RecoverWithContext()` ONLY catches panics**
- **Regular error values are NOT automatically captured**
- **You must explicitly call `hub.CaptureException(err)` for error values**

In our current `/products` flow, we do not panic on DB errors; we capture the error and return HTTP 500.

**In production Go code:**

Most Go code doesn't panic - it returns errors:
```go
rows, err := s.getProducts(r.Context())
if err != nil {
    hub.CaptureException(err)
    http.Error(w, "internal server error", http.StatusInternalServerError)
    return
}
```

**Panics are for truly exceptional cases:**
- Out of memory
- Nil pointer dereference
- Array index out of bounds
- **Our demo bugs** (to show Sentry's panic recovery)

---

## Manual Instrumentation for N+1 Detection

### The Problem: No Database Integration

Go SDK has **no automatic database instrumentation**. Unlike Python's `SqlalchemyIntegration()` which automatically creates spans for every query, Go requires manual span creation.

### The Solution: Manual Span Creation with Required Attributes

```go
func (s *server) getProducts(ctx context.Context) (string, error) {
    // Step 1: Extract transaction from context
    transaction := sentry.TransactionFromContext(ctx)
    if transaction == nil {
        return "", fmt.Errorf("no transaction in context")
    }
    
    // Step 2: Get transaction context for span creation
    transactionCtx := transaction.Context()
    
    // Step 3: Create span for products query
    productsSpan := sentry.StartSpan(transactionCtx, "db.query", 
        sentry.WithDescription("SELECT * FROM products WHERE id IN (...)"))
    productsSpan.SetTag("db.operation", "select")
    productsSpan.SetTag("db.system", "postgresql")  // Required!
    productsSpan.SetData("db.statement", parameterizedProductsQuery)
    
    products, err := conn.Query(ctx, actualProductsQuery)
    productsSpan.Finish()
    
    // Step 4: Create span for EACH review query (N+1 pattern)
    for products.Next() {
        parameterizedQuery := "SELECT * FROM reviews, product_bundles WHERE productId = %s"
        
        // Create span at transaction level (sibling, not child)
        reviewSpan := sentry.StartSpan(transactionCtx, "db.query", 
            sentry.WithDescription(parameterizedQuery))
        reviewSpan.SetTag("db.operation", "select")
        reviewSpan.SetTag("db.system", "postgresql")  // CRITICAL for N+1 detection!
        reviewSpan.SetData("db.statement", parameterizedQuery)
        reviewSpan.SetData("productId", pid)
        
        revs, err := s.db.Query(ctx, "SELECT * FROM reviews WHERE productId = $1", pid)
        reviewSpan.Finish()
    }
}
```

### Why Each Part is Necessary

#### 1. Extract Transaction Context
```go
transaction := sentry.TransactionFromContext(ctx)
transactionCtx := transaction.Context()
```

**Why?**
- We need a **valid context that lives for the entire request**
- If we use a child span's context and that span finishes, we get "span ID does not exist" error
- Transaction context is valid until the request completes

**What we learned the hard way:**
- Not recommended: Creating spans from a finished span context -> "span ID does not exist"
- Recommended: Creating spans from the transaction context -> works correctly

#### 2. Use Transaction Context for Spans, Original Context for DB

```go
// For Sentry spans - use transaction context
reviewSpan := sentry.StartSpan(transactionCtx, "db.query", ...)

// For database operations - use original context
revs, err := s.db.Query(ctx, query, pid)
```

**Why two contexts?**
- **`transactionCtx`**: For span hierarchy and Sentry instrumentation
- **`ctx`**: For database cancellation, timeouts, and request values

#### 3. Set Required Span Attributes

```go
reviewSpan.SetTag("db.operation", "select")
reviewSpan.SetTag("db.system", "postgresql")  // CRITICAL
reviewSpan.SetData("db.statement", parameterizedQuery)
```

**Why each attribute matters:**

**`op="db.query"`** (in StartSpan):
- Tells Sentry this is a database query operation
- Without it, Sentry treats it as generic span

**`db.system="postgresql"`**:
- **THIS IS THE CRITICAL TAG FOR N+1 DETECTION**
- Sentry's N+1 algorithm specifically looks for this tag
- Without it: Spans show in Performance tab, but NO Issue created
- With it: Issue appears in Issues tab

**`db.statement`**:
- The parameterized query (with `%s` placeholders)
- Used for grouping identical queries
- Sentry groups all queries with same statement

**`db.operation="select"`**:
- Additional context about query type
- Helps with filtering and analysis

#### 4. Create Spans at Transaction Level (Siblings)

```go
// All review spans created from transactionCtx (not nested under productsSpan)
for products.Next() {
    reviewSpan := sentry.StartSpan(transactionCtx, "db.query", ...)
}
```

**Why siblings, not children?**

Sentry's N+1 detection looks for: **Multiple identical spans at the same hierarchy level**

**If nested:**
```
Transaction
└─ productsSpan
   ├─ reviewSpan 1
   ├─ reviewSpan 2
   └─ reviewSpan 3
```
Sentry might not detect N+1 (spans are children of productsSpan)

**If siblings:**
```
Transaction
├─ productsSpan
├─ reviewSpan 1
├─ reviewSpan 2
└─ reviewSpan 3
```
Sentry detects: "Multiple identical db.query spans at transaction level = N+1!"

### Why `hub.CaptureException()` Instead of `sentry.CaptureException()`?

You'll notice throughout the code we use:
```go
hub := sentry.GetHubFromContext(r.Context())
hub.CaptureException(err)
```

Instead of the simpler:
```go
sentry.CaptureException(err)
```

**The difference:**

**`sentry.CaptureException(err)`** - Package-level function
```go
func CaptureException(exception error) *EventID {
    hub := CurrentHub()  // gets global hub
    return hub.CaptureException(exception)
}
```
- Uses `CurrentHub()` which returns the **global/default hub**
- Works for simple, single-threaded applications
- **Loses request-specific context** that was set by middleware:
  - Missing `se` tag
  - Missing `customerType` tag  
  - Missing user email
  - Missing transaction/span hierarchy from current request

**`hub.CaptureException(err)`** - Hub from request context
```go
hub := sentry.GetHubFromContext(r.Context())  // gets request-specific hub
hub.CaptureException(err)
```
- Gets the hub created by `sentryhttp` middleware for this specific request
- Preserves **all request-specific context**:
  - Tags set by `sentryContextMiddleware` (se, customerType)
  - User info (email)
  - Transaction and span hierarchy
  - Request-specific scope

**Why this matters in concurrent web servers:**

From Sentry's documentation:
> "In threaded environments, you have to take care of the data that's living inside it... `Hub` keeps track of corresponding `Scope` and `Client`, allowing them to communicate with each other."

**Example of concurrent requests:**
```go
// Request 1 (goroutine 1) - /products?customerType=premium
hub1 := sentry.GetHubFromContext(r1.Context())
hub1.Scope().SetTag("customerType", "premium")
hub1.CaptureException(err)  // error tagged with "premium"

// Request 2 (goroutine 2) - /products?customerType=basic (happening simultaneously)
hub2 := sentry.GetHubFromContext(r2.Context())
hub2.Scope().SetTag("customerType", "basic")
hub2.CaptureException(err)  // error tagged with "basic"
```

**With hub from context:**
- Each request has an isolated hub
- Tags don't leak between requests
- Correct context for each error

**With global `sentry.CaptureException()`:**
- Both requests share the same hub
- Tags can leak between requests (e.g., Request 2's tag could appear on Request 1)
- Race conditions are possible

**In our implementation:**

The per-request hub is created by the Sentry HTTP middleware:
```go
// In main() - middleware setup
sentryHandler := sentryhttp.New(sentryhttp.Options{Repanic: true})
handler := withCORS(sentryHandler.Handle(sentryContextMiddleware(logged)))
```

The `sentryhttp` middleware:
1. Clones the hub for each incoming request
2. Attaches it to request context
3. Makes it available via `GetHubFromContext(r.Context())`

Then in every handler:
```go
hub := sentry.GetHubFromContext(r.Context())  // Get request-specific hub
hub.CaptureException(err)  // Capture with request context
```

**This pattern applies to both errors:**
- **Checkout panic** - `hub.CaptureException()` in recovery
- **N+1 detection** - Uses hub for logging: `logger := sentry.NewLogger(r.Context())`

**Exception: Worker process**
```go
// In cmd/worker/main.go
sentry.CaptureException(err)  // package-level is fine here
```

The worker is **single-threaded** (processes one job at a time from queue), so there's no concurrency - global hub is appropriate.

### Why `CaptureException()` Instead of `CaptureMessage()`?

We use `CaptureException()` for actual errors:
```go
if err != nil {
    hub.CaptureException(err)  // for error values
    return err
}
```

But we DO use `CaptureMessage()` in one place:
```go
// In proxyRuby() - line 1020
if resp.StatusCode >= 400 {
    hub.CaptureMessage(fmt.Sprintf("ruby backend error: status %d", resp.StatusCode))
}
```

**The difference:**

**`CaptureException(err error)`** - For error values
- Takes an `error` type
- Creates an "Error" issue type in Sentry
- **Includes stack trace** (from where error was created)
- Shows error type, message, and full context
- Use for: Actual errors, exceptions, failures

**`CaptureMessage(msg string)`** - For informational messages
- Takes a `string` 
- Creates a "Message" issue type in Sentry (lower severity)
- **No stack trace** (it's just a message, not an error)
- Just records the message with context
- Use for: Warnings, notifications, unusual conditions that aren't errors

**Why we use `CaptureMessage` for HTTP errors:**
```go
if resp.StatusCode >= 400 {
    hub.CaptureMessage(fmt.Sprintf("ruby backend error: status %d", resp.StatusCode))
}
```

We could use `CaptureException`:
```go
if resp.StatusCode >= 400 {
    hub.CaptureException(fmt.Errorf("ruby backend error: status %d", resp.StatusCode))
}
```

**But `CaptureMessage` is more appropriate because:**
- It's not an error in **our** code - the ruby backend returned an error
- We're just noting that the backend had a problem
- Lower severity than an actual exception in our code
- We successfully handled the response (closed body, checked status)

**For all errors in our own code, we use `CaptureException`:**
- Database errors: `hub.CaptureException(fmt.Errorf("database error: %w", err))`
- JSON decode errors: `hub.CaptureException(fmt.Errorf("decode error: %w", err))`
- Redis errors: `hub.CaptureException(fmt.Errorf("redis error: %w", err))`
- Panics: `hub.CaptureException(fmt.Errorf("%v", err))`

**Note on naming: Why "CaptureException" when Go has errors, not exceptions?**

The name `CaptureException` is confusing in Go because:
- Go doesn't have exceptions - it has **error values** and **panics**
- The method is named `CaptureException` for **cross-language consistency** across all Sentry SDKs
- In Python/Java/C#: Captures exceptions
- In Go: Captures error values and panics (converted to errors)

**More accurate name would be:** `CaptureError()` but Sentry uses `CaptureException()` across all languages for consistency.

**So in Go:**
- `hub.CaptureException(err)` = Capture an **error value** or **panic** (not an exception)
- The "exception" terminology is just Sentry's universal naming convention

**We still use the hub (`hub.CaptureException`) even for simple errors like JSON decode because:**
- The hub has the request-specific context (tags, user, transaction)
- Without the hub, we'd lose the `se` tag, `customerType` tag, and user email
- The error would be sent to Sentry but without any of that valuable context

---

## What Happens Without Panics?

**Production Go code typically doesn't panic - it returns errors:**

```go
func (s *server) handleProducts(w http.ResponseWriter, r *http.Request) {
    defer sentry.RecoverWithContext(r.Context())  // Safety net for unexpected panics
    
    hub := sentry.GetHubFromContext(r.Context())
    
    rows, err := s.getProducts(r.Context())
    if err != nil {
        // This is a normal error value, NOT a panic
        hub.CaptureException(err)  // must explicitly capture
        http.Error(w, "database error", 500)
        return
    }
    
    // Continue processing...
}
```

**What happens:**
1. `getProducts()` returns an error value (not a panic)
2. We check `if err != nil`
3. **We must explicitly call `hub.CaptureException(err)`**
4. Return HTTP 500 to client
5. `RecoverWithContext()` does nothing (no panic occurred)

**Key point:** `sentry.RecoverWithContext()` **ONLY catches panics, not error values**

### Why Our Demo Uses Panics

**In our `/products` handler:**
```go
if err != nil {
    logger.Error().Emitf("Processing /products - error occurred: %v", err)
    hub.CaptureException(err)  // Capture the error value
    panic(fmt.Errorf("products database error: %w", err))  // Then panic
}
```

**Why panic here?**
1. **Demonstrate panic recovery** - Show that `RecoverWithContext()` works
2. **Dramatic failure** - Makes it clear in demo that something went wrong
3. **Show stack traces** - Panics include goroutine information
4. **Educational** - Shows both error capture and panic recovery

**In production, this would be:**
```go
if err != nil {
    hub.CaptureException(err)
    http.Error(w, "database error", 500)
    return  // Just return, don't panic
}
```

### The Three Error Handling Patterns

#### Pattern 1: Error Value (Production Pattern)
```go
rows, err := s.getProducts(r.Context())
if err != nil {
    hub.CaptureException(err)  // explicit capture required
    http.Error(w, "internal server error", http.StatusInternalServerError)
    return
}
```
- Idiomatic Go
- Explicit error handling
- Must remember to call `CaptureException()`

#### Pattern 2: Panic with Automatic Recovery (Demo Pattern)
```go
defer sentry.RecoverWithContext(r.Context())  // automatic capture

if err != nil {
    panic(err)  // Panic triggers RecoverWithContext
}
```
- Automatic capture
- Simple code
- Not idiomatic Go (panics should be rare)
- Less control over response

#### Pattern 3: Panic with Manual Recovery (Checkout Pattern)
```go
defer func() {
    if err := recover(); err != nil {
        hub.CaptureException(fmt.Errorf("%v", err))
        http.Error(w, fmt.Sprintf("%v", err), 500)
        return
    }
}()

// ... code that panics
```
- Full control over response
- Explicit capture
- Guarantees HTTP 500 on error
- Most boilerplate

### What we use in `/products` and why

Handled error pattern:
```go
rows, err := s.getProducts(r.Context())
if err != nil {
    hub.CaptureException(err)
    http.Error(w, "internal server error", http.StatusInternalServerError)
    return
}
```

**Why this combination?**
1. **Explicit `CaptureException(err)`** - Captures the original error value with full context
2. **Then `panic(err)`** - Demonstrates panic recovery for educational purposes
3. **`RecoverWithContext()` as safety net** - Catches the panic automatically

**This shows both:**
- How to capture error values explicitly
- How automatic panic recovery works

---

## Manual Instrumentation for N+1 Detection

### Why Manual Instrumentation is Necessary

**The fundamental limitation:**
- Go SDK has **no database integration** (no pgx, gorm, or database/sql integration)
- Database queries are **not automatically instrumented**
- We must **manually create spans** for Sentry to see the queries

**Without manual instrumentation:**
```go
for products.Next() {
    // Just execute query - Sentry sees nothing
    revs, err := s.db.Query(ctx, "SELECT * FROM reviews WHERE productId = $1", pid)
}
```
- No spans created
- No performance data
- No N+1 detection
- Sentry has no visibility into database operations

### The Manual Instrumentation Pattern

```go
// Step 1: Extract transaction context (required for valid span creation)
transaction := sentry.TransactionFromContext(ctx)
transactionCtx := transaction.Context()

// Step 2: Create span for EACH database query
for products.Next() {
    parameterizedQuery := "SELECT * FROM reviews, product_bundles WHERE productId = %s"
    
    // Step 3: Create span with ALL required attributes
    reviewSpan := sentry.StartSpan(transactionCtx, "db.query", 
        sentry.WithDescription(parameterizedQuery))
    
    // Step 4: Set required tags for N+1 detection
    reviewSpan.SetTag("db.operation", "select")
    reviewSpan.SetTag("db.system", "postgresql")  // CRITICAL
    reviewSpan.SetData("db.statement", parameterizedQuery)
    reviewSpan.SetData("productId", pid)
    
    // Step 5: Execute the actual query
    revs, err := s.db.Query(ctx, "SELECT * FROM reviews WHERE productId = $1", pid)
    
    // Step 6: Finish the span
    reviewSpan.Finish()
}
```

### Breaking Down Each Step

#### Step 1: Transaction Context
```go
transaction := sentry.TransactionFromContext(ctx)
transactionCtx := transaction.Context()
```

**Why?**
- Need a context that's **valid for the entire request**
- Can't use child span contexts (they finish before we create review spans)
- Transaction context lives until request completes

**The "span ID does not exist" error:**
- Happens if you create spans from a finished span's context
- Solution: Always use transaction context for span creation

#### Step 2-3: Create Span
```go
reviewSpan := sentry.StartSpan(transactionCtx, "db.query", 
    sentry.WithDescription(parameterizedQuery))
```

**Why `transactionCtx` not `ctx`?**
- `transactionCtx` is for Sentry span hierarchy
- `ctx` (original) is for database operations (cancellation, timeouts)

**Why `"db.query"` not `"db"`?**
- Sentry's N+1 algorithm looks for `op="db.query"` specifically
- Generic `"db"` won't trigger detection

#### Step 4: The Critical Tag - `db.system`
```go
reviewSpan.SetTag("db.system", "postgresql")
```

**This tag is REQUIRED for N+1 detection!**

**Without it:**
- Spans appear in Performance tab
- Sentry doesn't recognize them as database queries
- N+1 detection algorithm doesn't run
- **No Issue created in Issues tab**

**With it:**
- Sentry knows: "These are PostgreSQL queries"
- N+1 detection algorithm analyzes the pattern
- Sees multiple identical queries
- **Creates Issue in Issues tab**

**Why this tag is required:**
- Sentry's backend specifically looks for `db.system` to identify database spans
- The algorithm won't run without it
- In Python, `SqlalchemyIntegration()` sets this automatically from connection metadata
- In Go, we must set it manually

#### Step 5-6: Execute and Finish
```go
revs, err := s.db.Query(ctx, actualQuery, pid)  // Use original ctx
reviewSpan.Finish()
```

**Why use `ctx` not `transactionCtx` for query?**
- Database operations need the original request context
- Carries cancellation signals, timeouts, request-scoped values
- Sentry context is only for span hierarchy

### The Result in Sentry

**What Sentry sees:**
```
Transaction: GET /products
├─ db.query: SELECT * FROM products (250ms)
├─ db.query: SELECT * FROM reviews WHERE productId = %s (80ms)
├─ db.query: SELECT * FROM reviews WHERE productId = %s (80ms)
├─ db.query: SELECT * FROM reviews WHERE productId = %s (80ms)
└─ db.query: SELECT * FROM reviews WHERE productId = %s (80ms)
```

**Sentry's algorithm detects:**
1. Multiple spans with `op="db.query"`
2. Same `db.statement` (parameterized query)
3. All have `db.system="postgresql"` tag
4. At same hierarchy level (siblings)

---

## Summary

### Error Capture
- **Handled errors**: capture with `hub.CaptureException(err)` and return HTTP 500 (used in `/products`)
- **Manual `recover()` + `CaptureException()`**: for controlled panic handling (used in `/checkout`)
- **`sentry.RecoverWithContext()`**: automatic panic capture used as a safety net where appropriate
- **Error values** must be explicitly captured with `hub.CaptureException(err)`
- **Panics** are for exceptional scenarios; most production handlers return errors

### N+1 Detection
- **Manual span creation required** (no database integration)
- **`db.system` tag is critical** - Without it, N+1 detection won't work
- **Transaction context management** - Avoid "span ID does not exist" by using transaction context