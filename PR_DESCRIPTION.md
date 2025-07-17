# Fix UnboundLocalError in checkout process

## Summary
This PR fixes a critical bug in the checkout process that was causing an `UnboundLocalError` when users attempted to complete their purchases. The issue was caused by accessing the `quantities` variable before it was assigned a value in the Flask backend's checkout function.

## Issue Description
Users were experiencing a "500 - Internal Server Error" when attempting to checkout. The error was occurring due to:

1. The `quantities` variable being used in a length check before being assigned from `cart['quantities']`
2. This caused Python to raise an `UnboundLocalError: local variable 'quantities' referenced before assignment`
3. The error was propagated through the CORS wrapper and resulted in a malformed HTTP response
4. The frontend received an undefined status code and threw a new error

## Root Cause Analysis
The bug was in the `/checkout` endpoint in `flask/src/main.py`:

```python
# BEFORE (buggy code)
if validate_inventory:
    with sentry_sdk.start_span(op="process_order", description="function"):
        if len(quantities) == 0:  # ❌ quantities used before assignment
            raise Exception("Invalid checkout request")
        
        quantities = cart['quantities']  # ❌ assigned AFTER first use
        # ... rest of code
```

## Solution
Reordered the variable assignment to occur before its first usage:

```python
# AFTER (fixed code)
if validate_inventory:
    with sentry_sdk.start_span(op="process_order", description="function"):
        quantities = cart['quantities']  # ✅ assigned FIRST
        if len(quantities) == 0:  # ✅ now quantities is properly defined
            raise Exception("Invalid checkout request")
        # ... rest of code
```

## Changes Made

### Backend (`flask/src/main.py`)
- **Line 12-15**: Moved the assignment `quantities = cart['quantities']` before the length check `if len(quantities) == 0:`
- This ensures the variable is properly initialized before any attempt to access it

### Frontend (`react/src/components/Checkout.jsx`)
- No changes required - the frontend code was already handling errors appropriately
- The fix in the backend resolves the malformed response issue

## Testing
- [x] Manual testing: Checkout process now completes successfully
- [x] Error path still works: Empty cart validation still functions correctly
- [x] No regression: All existing functionality preserved

## Impact
- **Severity**: Critical - This was preventing all checkout attempts from succeeding
- **Users Affected**: All users attempting to checkout
- **Risk**: Low - Simple variable reordering with no logic changes

## Verification Steps
1. Add items to cart
2. Navigate to checkout page
3. Fill out checkout form
4. Submit checkout
5. Verify successful completion without 500 error

## Related Issues
- Fixes the UnboundLocalError reported in checkout flow
- Resolves 500 Internal Server Error during purchase attempts
- Ensures proper cart validation continues to work as expected

---

**Type**: Bug Fix  
**Priority**: High  
**Reviewer**: @backend-team @frontend-team