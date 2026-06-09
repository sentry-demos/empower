import contextvars
import random
from typing import Optional

# Controls the demo error injection via the ?agent_crash query param. Tri-state:
#   True  -> force the plant advice error 100% of the time
#   False -> suppress all injected errors (never crash)
#   None  -> no override; fall back to the default random probabilities
# Set in the API route and read inside the tool, which is invoked by the agents
# SDK; a contextvar propagates through the awaited async chain.
agent_crash_mode: contextvars.ContextVar[Optional[bool]] = contextvars.ContextVar(
    "agent_crash_mode", default=None
)


def maybe_throw(probability: float, exception: Exception) -> None:
    # An explicit ?agent_crash=false disables injected errors entirely.
    if agent_crash_mode.get() is False:
        return
    if random.random() < probability:
        raise exception
