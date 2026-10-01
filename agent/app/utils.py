import contextvars

# Set from query params on the /buy-plants request. When true, the corresponding
# plant lookup fails, surfacing a demo error. Unset means false. Set in the API
# route and read inside the tool, which is invoked by the agents SDK; a contextvar
# propagates through the awaited async chain.
#
#   validate_plant_advice -> plant advice lookup fails (File not found)
#   validate_plant_info   -> plant basic info lookup fails (Unknown plant)
validate_plant_advice: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "validate_plant_advice", default=False
)
validate_plant_info: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "validate_plant_info", default=False
)

# Demo/routing headers off the incoming request, set by the sentry_event_context
# middleware in main.py. main.py only puts these on the Sentry scope, which tags
# the agent's own transaction; stashing them here lets outbound Flask calls made
# deep inside a tool re-send them, so the downstream flask spans carry the same
# `se`/`customerType`/`cexp` values. Treat the default as read-only — always
# .set() a new dict rather than mutating in place.
request_headers: contextvars.ContextVar[dict[str, str]] = contextvars.ContextVar(
    "request_headers", default={}
)
