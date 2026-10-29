"""A mock Confluence export of the Empower Plant help centre.

search_policies searches these pages and returns only the matches, as text. Each
page is wrapped in the chrome a real space export carries — navigation,
breadcrumbs, inline styles, analytics tags — so most of a raw page is markup
rather than policy, and must not reach the model.

Built in code at import time rather than committed as a ~150KB fixture. The
pages are deterministic, so the token count of the spike is the same every run.
"""

from typing import Any

# One of these holds the answer the customer is after. The rest are what a help
# centre export plausibly also contains, and are what makes the payload large.
RETURNS_PAGE_TITLE = "Returns & refunds"

RETURNS_BODY = (
    "<p>We accept returns within <strong>30 days</strong> of delivery. Items"
    " must be unused, in their original pot and packaging, and accompanied by"
    " the order number.</p>"
    "<p>Once the return is received and inspected, the refund is issued to the"
    " <strong>original payment method</strong> within 5&ndash;7 business days."
    " Shipping costs are not refunded unless the item arrived damaged.</p>"
    "<p>Live plants that have been repotted, and gift cards, cannot be"
    " returned. To start a return, contact support with your order number.</p>"
)

_TITLES = [
    RETURNS_PAGE_TITLE,
    "Shipping times and carriers",
    "International shipping",
    "Order tracking",
    "Changing or cancelling an order",
    "Damaged on arrival",
    "Plant health guarantee",
    "Gift cards",
    "Promo codes and discounts",
    "Loyalty programme",
    "Payment methods",
    "Sales tax",
    "Invoices and receipts",
    "Account and password",
    "Email preferences",
    "Privacy policy",
    "Cookie policy",
    "Terms of service",
    "Accessibility statement",
    "Corporate gifting",
    "Wholesale accounts",
    "Plant care: light",
    "Plant care: watering",
    "Plant care: humidity",
    "Plant care: repotting",
    "Plant care: pests",
    "Plant care: fertiliser",
    "Pet-safe plants",
    "Pots and planters",
    "Soil and substrates",
    "Grow lights",
    "Plant Mood sensor setup",
    "Plant Mood sensor troubleshooting",
    "Plant Mood app pairing",
    "Firmware updates",
    "Warranty for devices",
    "Recycling packaging",
    "Sustainability commitments",
    "Store locations",
    "Opening hours",
    "Workshops and events",
    "Careers",
    "Press and media",
    "Affiliate programme",
    "Reviews policy",
    "Out-of-stock notifications",
    "Pre-orders",
    "Subscriptions",
    "Holiday delivery cut-offs",
    "Contact support",
]

PAGE_COUNT = len(_TITLES)

# Everything below is the export's page chrome, identical on every page. It is
# deliberately the bulk of each page: that is what a raw export looks like.
_STYLE = (
    "<style>body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,"
    "Oxygen,Ubuntu,sans-serif;margin:0;color:#172b4d}"
    "#header{background:#0747a6;height:56px;display:flex;align-items:center}"
    "#header a{color:#fff;padding:0 12px;text-decoration:none}"
    ".aui-nav-breadcrumbs{list-style:none;padding:8px 24px;margin:0;font-size:12px}"
    ".aui-nav-breadcrumbs li{display:inline;color:#5e6c84}"
    ".wiki-content{padding:16px 24px;line-height:1.6;max-width:760px}"
    ".page-metadata{font-size:12px;color:#6b778c;padding:0 24px}"
    "#footer{border-top:1px solid #dfe1e6;padding:16px 24px;font-size:11px}"
    ".confluence-information-macro{border-left:3px solid #0052cc;padding:8px}"
    "</style>"
)

_NAV = (
    '<div id="header" role="banner"><nav class="aui-header" aria-label="Site">'
    '<a href="/wiki/spaces/HELP/overview" class="aui-nav-imagelink">Help Centre</a>'
    '<a href="/wiki/spaces/HELP/pages">Pages</a>'
    '<a href="/wiki/spaces/HELP/blog">Blog</a>'
    '<a href="/wiki/spaces/HELP/settings">Space settings</a>'
    '<a href="/wiki/people">People</a>'
    '<a href="/wiki/templates">Templates</a>'
    '<a href="/wiki/search" class="aui-nav-search">Search</a>'
    "</nav></div>"
)

_SIDEBAR = (
    '<div class="ia-secondary-container" data-tree-type="pages">'
    '<ul class="plugin_pagetree">'
    + "".join(
        f'<li><a href="/wiki/spaces/HELP/pages/{100200 + i}">{title}</a></li>'
        for i, title in enumerate(_TITLES[:6])
    )
    + "</ul></div>"
)

_FOOTER = (
    '<div id="footer" role="contentinfo"><section class="footer-body">'
    "<p>Powered by Atlassian Confluence &middot; Report a bug &middot; Atlassian"
    " News</p></section></div>"
    '<script type="text/javascript">window.dataLayer=window.dataLayer||[];'
    "function gtag(){dataLayer.push(arguments)}gtag('js',new Date());"
    "gtag('config','G-EMPWRHELP1',{anonymize_ip:true,page_path:location.pathname});"
    "(function(w,d,s,l){var f=d.getElementsByTagName(s)[0],j=d.createElement(s);"
    "j.async=true;j.src='https://cdn.segment.example/analytics.js/v1/help/"
    "analytics.min.js';f.parentNode.insertBefore(j,f)})(window,document,'script');"
    "</script>"
)


def _filler(title: str) -> str:
    """Body copy for a page that isn't about returns."""
    return (
        f"<p>This page describes {title.lower()} at Empower Plant. It is"
        " maintained by the customer experience team and reviewed every"
        " quarter.</p>"
        '<div class="confluence-information-macro"><p>For anything not covered'
        " here, contact support from your account page.</p></div>"
    )


def _page(page_id: int, title: str) -> str:
    body = RETURNS_BODY if title == RETURNS_PAGE_TITLE else _filler(title)
    return (
        f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        f"<title>{title} - Help Centre - Confluence</title>{_STYLE}</head>"
        f'<body id="com-atlassian-confluence" class="theme-default">{_NAV}'
        '<ol class="aui-nav-breadcrumbs"><li><a href="/wiki">Confluence</a></li>'
        '<li><a href="/wiki/spaces/HELP">Help Centre</a></li>'
        '<li><a href="/wiki/spaces/HELP/pages/100100">Policies</a></li>'
        f"<li>{title}</li></ol>{_SIDEBAR}"
        f'<div id="main-content" class="wiki-content" data-page-id="{page_id}">'
        f"<h1>{title}</h1>{body}</div>"
        '<div class="page-metadata">Created by Customer Experience, last updated'
        " 3 March 2026</div>"
        f"{_FOOTER}</body></html>"
    )


_PAGES: list[dict[str, Any]] = [
    {"id": 100200 + i, "title": title, "html": _page(100200 + i, title)}
    for i, title in enumerate(_TITLES)
]


def pages() -> list[dict[str, Any]]:
    """Every page in the export, raw HTML and all."""
    return _PAGES
