import re

# Strip bullets, numbered lists, and optional markdown checkboxes.
_LIST_MARKER = re.compile(
    r"""
    ^\s*
    (?:
        (?:[-*+]|\d+[.)])\s+
        (?:\[[ xX]\]\s+)?
        |
        \[[ xX]\]\s+
    )
    """,
    re.VERBOSE,
)

# Open (incomplete) checkboxes, including after a list marker.
_OPEN_CHECKBOX = re.compile(r"^(?:(?:[-*+]|\d+[.)])\s+)?\[\s\]\s+\S")

# Completed checkboxes should not be extracted as new work.
_DONE_CHECKBOX = re.compile(r"^(?:(?:[-*+]|\d+[.)])\s+)?\[[xX]\]\s+")

_LABEL_LINE = re.compile(
    r"""
    ^(?:
        TODO|TO-DO|ACTION(?:\s*ITEMS?)?|TASK|FIXME|XXX|HACK|NEXT|WIP
    )
    \s*[:\-–]\s*\S
    """,
    re.IGNORECASE | re.VERBOSE,
)

_INLINE_LABEL = re.compile(
    r"""
    \b(?P<label>
        TODO|TO-DO|ACTION(?:\s*ITEMS?)?|TASK|FIXME|XXX|HACK|NEXT|WIP
    )
    \s*[:\-–]\s*
    (?P<body>\S.*)
    $
    """,
    re.IGNORECASE | re.VERBOSE,
)

_IMPERATIVE = re.compile(
    r"""
    ^(?:
        please|
        remember\s+to|
        don'?t\s+forget\s+to|
        do\s+not\s+forget\s+to|
        need(?:s)?\s+to|
        must|
        should|
        let'?s
    )\b
    .{2,}
    """,
    re.IGNORECASE | re.VERBOSE,
)

_ASSIGNEE = re.compile(r"^@[\w.-]+\s*[:\-–]\s*\S")

_DUE = re.compile(
    r"""
    .+\b(?:due(?:\s+date)?|deadline|by|before)\s+
    (?:
        \d{4}-\d{2}-\d{2}
        |\d{1,2}/\d{1,2}(?:/\d{2,4})?
        |today|tomorrow|tonight
        |next\s+(?:week|month|monday|tuesday|wednesday|thursday|friday|saturday|sunday)
        |(?:mon(?:day)?|tue(?:s(?:day)?)?|wed(?:nesday)?|thu(?:rs(?:day)?)?|
           fri(?:day)?|sat(?:urday)?|sun(?:day)?)
    )\b
    """,
    re.IGNORECASE | re.VERBOSE,
)

_EXCLAMATION = re.compile(r".+!$")

_LINE_PATTERNS = (_LABEL_LINE, _IMPERATIVE, _ASSIGNEE, _DUE, _EXCLAMATION)


def _normalize_line(line: str) -> str:
    return _LIST_MARKER.sub("", line.strip(), count=1).strip()


def extract_action_items(text: str) -> list[str]:
    """Return unique actionable lines using several regex patterns."""
    results: list[str] = []
    seen: set[str] = set()

    for raw in text.splitlines():
        if not raw.strip():
            continue

        if _DONE_CHECKBOX.search(raw.strip()):
            continue

        is_open_checkbox = bool(_OPEN_CHECKBOX.search(raw.strip()))
        line = _normalize_line(raw)
        if not line:
            continue

        matched = is_open_checkbox or any(pattern.search(line) for pattern in _LINE_PATTERNS)
        if not matched:
            inline = _INLINE_LABEL.search(line)
            if inline:
                line = f"{inline.group('label')}: {inline.group('body')}".strip()
                matched = True

        if not matched:
            continue

        key = re.sub(r"\s+", " ", line).casefold()
        if key in seen:
            continue
        seen.add(key)
        results.append(line)

    return results
