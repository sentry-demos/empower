This is the AI shopping agent (`agent/`, Python, OpenAI Agents SDK). Its LLM calls are
`gen_ai.chat` spans and its tool calls are `gen_ai.execute_tool` spans. Tool spans may carry
attributes describing their output (for example its size), and logs from the same trace may too.

The alert is about LLM input size: the `gen_ai.usage.input_tokens` on one `gen_ai.chat` span, far
above a normal turn's. Find which input made it that large (a tool result, history, or a system
prompt), and the code that produced it.

**What a real fix looks like here:** the model gets only what it needs to answer, in a form it can
use, so the same question costs a normal number of tokens and still gets the right answer.
Truncating a payload blindly isn't a fix if it can cut off the answer.

**Prove it with the check.** `{{CHECK}}` calls the affected tool for a few real customer questions
and counts the tokens it returns. It passes only when every answer is under the budget and the
return-policy question still contains its answer. Run it before your fix (it fails) and after
(it must pass).

**Impact** (in `result.json`): add to `impact`:
- `input_tokens_spike`: the spike's input tokens (from the alert or the span).
- `input_tokens_normal`: a normal turn's input tokens, from comparable `gen_ai.chat` spans.
- `input_tokens_after_fix`: what the check measured for the same question after your fix.
- `occurrences` and `first_seen`: from the issue.

`impact_short` example: "~48k input tokens per policy question, ~25× a normal turn".
