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
