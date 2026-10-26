You are reviewing a pull request that an unattended agent opened to fix a production issue
in the Flask backend. A human will decide whether to merge it; your comment helps them decide.

The PR description is in `{{OUT}}/pr.md` and the diff is in `{{OUT}}/pr.diff`. The repo
working tree is checked out at the PR head. Read `AGENTS.md` for the rules agents follow.

Check:

1. **Root cause.** Does the change fix the actual cause, or does it hide the symptom
   (catching, wrapping or rewording the exception, skipping validation, returning early)?
2. **Regression test.** Is there a test that would fail without the fix? Run
   `python -m pytest flask/src/test` to confirm the suite passes.
3. **Scope.** Is the change limited to what the fix needs, and only under `flask/`?
4. **Risk.** Anything else that could break checkout?

Write your review to `{{OUT}}/review.md` as GitHub markdown. The first line must be exactly one of:

- `**Verdict: MERGE**` — correct root-cause fix with a real regression test.
- `**Verdict: ADJUST**` — right direction, but needs specific changes (list them).
- `**Verdict: CLOSE**` — masks the problem or is wrong.

Then give a short explanation, and point to lines in the diff where relevant. Keep it under
200 words. You never approve PRs; a human does.
