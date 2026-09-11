"""Tools backing the conversational shopping flow.

These call the real Flask backend rather than stubbing it out, so the existing
shopping functionality — its DB queries, its latency and its failure modes —
shows up inside the agent's trace.
"""

from .search_products import search_products

__all__ = ["search_products"]
