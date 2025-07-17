fix: resolve UnboundLocalError in checkout process

The checkout function was accessing the 'quantities' variable before
it was assigned, causing an UnboundLocalError that prevented users
from completing purchases.

This fix reorders the variable assignment to occur before its first
usage, ensuring proper cart validation while maintaining all existing
functionality.

Fixes:
- UnboundLocalError: local variable 'quantities' referenced before assignment
- 500 Internal Server Error during checkout
- Malformed HTTP responses due to exception handling

Changes:
- flask/src/main.py: Move quantities assignment before length check

Impact: Critical bug fix - restores checkout functionality for all users