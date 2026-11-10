"""Keep agent commits and PRs from closing the Sentry issue they respond to.

Sentry's GitHub integration reads commit messages and PR text for a fix keyword followed by an
issue short ID or URL ("Fixes KUNAL-MANAGER-AGENT-5"). It links the commit as the issue's fix, and
until that commit ships in a Sentry release, new occurrences don't reopen the issue, so its alert
never fires again. Agent PRs are drafts that may never merge, so they must reference the issue
without a fix keyword.

The patterns mirror sentry/utils/groupreference.py (case-insensitive). The keyword doesn't have
to sit right before the ID: "Fix the policy search, KUNAL-MANAGER-AGENT-5" matches too, because the
capture runs over letters, digits, whitespace (newlines included), commas and hyphens. Sentry
reduces markdown links to their text before matching, so this does as well.
"""
import re

FIX_KEYWORDS = r"(?:Fix|Fixes|Fixed|Close|Closes|Closed|Resolve|Resolves|Resolved)"
FIXES_RE = re.compile(rf"\b{FIX_KEYWORDS}:?\s+([A-Za-z0-9_\-\s\,]+)\b", re.I)
FIXES_URL_RE = re.compile(rf"\b{FIX_KEYWORDS}:?\s+(https?://[^\s]+)", re.I)
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
KEYWORD_RE = re.compile(rf"\b{FIX_KEYWORDS}\b", re.I)
NEUTRAL = {"fix": "address", "fixes": "addresses", "fixed": "addressed",
           "close": "address", "closes": "addresses", "closed": "addressed",
           "resolve": "address", "resolves": "addresses", "resolved": "addressed"}


def strip_links(text):
    return MARKDOWN_LINK_RE.sub(r"\1", text)


def _mentions(capture, short_id):
    return bool(short_id) and re.search(rf"(?<![\w-]){re.escape(short_id)}(?![\w-])", capture, re.I)


def _is_issue_url(url, issue_url):
    url = url.rstrip(").,;")
    return "/issues/" in url or bool(issue_url) and url.startswith(issue_url.rstrip("/"))


def closing_references(text, short_id, issue_url=""):
    """The spans of text Sentry would read as "this commit/PR fixes <the issue>"."""
    text = strip_links(text or "")
    found = [m.group(0) for m in FIXES_RE.finditer(text) if _mentions(m.group(1), short_id)]
    found += [m.group(0) for m in FIXES_URL_RE.finditer(text) if _is_issue_url(m.group(1), issue_url)]
    return found


def _closes_here(text, short_id, issue_url):
    """Whether the fix keyword at the very start of text leads to the issue."""
    text = strip_links(text)
    m = FIXES_RE.match(text)
    if m and _mentions(m.group(1), short_id):
        return True
    m = FIXES_URL_RE.match(text)
    return bool(m and _is_issue_url(m.group(1), issue_url))


def _neutral_word(word):
    replacement = NEUTRAL[word.lower()]
    if word.isupper():
        return replacement.upper()
    return replacement.capitalize() if word[0].isupper() else replacement


def neutralize(text, short_id, issue_url=""):
    """Swap each fix keyword that leads to the issue for "address", keeping the reference itself."""
    text = text or ""
    out, last = [], 0
    for m in KEYWORD_RE.finditer(text):
        if _closes_here(text[m.start():], short_id, issue_url):
            out += [text[last:m.start()], _neutral_word(m.group(0))]
            last = m.end()
    return "".join(out) + text[last:]


class ClosingReference(ValueError):
    pass


def check(texts, short_id, issue_url=""):
    """Raise if any of the texts would still close the issue. Run right before commit and PR."""
    bad = {name: refs for name, text in texts.items() if (refs := closing_references(text, short_id, issue_url))}
    if bad:
        raise ClosingReference(f"commit/PR text would close {short_id or issue_url} in Sentry: {bad}")
