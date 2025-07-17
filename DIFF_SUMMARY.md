# Git Diff Summary

## Files Changed: 1

### `flask/src/main.py`
**Lines modified:** 12-15 (in checkout function)

```diff
     try:
         if validate_inventory:
             with sentry_sdk.start_span(op="process_order", description="function"):
+                quantities = cart['quantities']
                 if len(quantities) == 0:
                     raise Exception("Invalid checkout request")
 
-                quantities = cart['quantities']
                 inventoryDict = {x.productid: x for x in inventory}
```

**Change Summary:**
- Moved line `quantities = cart['quantities']` from after the length check to before it
- This fixes the UnboundLocalError by ensuring the variable is assigned before first use
- No other logic changes - simple reordering fix

**Impact:**
- Resolves critical checkout failure
- Maintains all existing validation logic
- Zero functional changes beyond fixing the bug