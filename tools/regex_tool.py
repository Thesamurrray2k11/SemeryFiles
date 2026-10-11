import re
from dataclasses import dataclass, field



FLAGS = {
    "IGNORECASE": ("Игнорировать регистр", re.IGNORECASE),
    "MULTILINE":  ("Многострочный (^ и $)", re.MULTILINE),
    "DOTALL":     (". включает перевод строки", re.DOTALL),
    "VERBOSE":    ("Пробелы в паттерне игнорируются", re.VERBOSE),
    "UNICODE":    ("Юникод-режим", re.UNICODE),
    "ASCII":      ("Только ASCII", re.ASCII),
}


@dataclass
class MatchInfo:
    start: int
    end: int
    text: str
    groups: list = field(default_factory=list)
    named: dict = field(default_factory=dict)


def compile_pattern(pattern: str, flag_keys: list[str]) -> re.Pattern:
    flags = 0
    for key in flag_keys:
        if key in FLAGS:
            flags |= FLAGS[key][1]
    return re.compile(pattern, flags)


def find_all(
    pattern: re.Pattern,
    text: str,
    max_matches: int = 10000,
) -> list[MatchInfo]:
    results: list[MatchInfo] = []
    seen_spans: set[tuple[int, int]] = set()

    for m in pattern.finditer(text):
        span = m.span()
        if span in seen_spans:
            continue
        seen_spans.add(span)

        groups = []
        for i in range(1, (m.re.groups or 0) + 1):
            name = None
            for gname, gidx in (m.re.groupindex or {}).items():
                if gidx == i:
                    name = gname
                    break
            groups.append((i, name, m.group(i)))

        named = {k: m.group(k) for k in (m.re.groupindex or {})}

        results.append(MatchInfo(
            start=span[0],
            end=span[1],
            text=m.group(0),
            groups=groups,
            named=named,
        ))

        if len(results) >= max_matches:
            break

    return results


def substitute(
    pattern: re.Pattern,
    replacement: str,
    text: str,
) -> tuple[str, int]:
    count = 0

    def _repl(m):
        nonlocal count
        count += 1
        return m.expand(replacement)

    try:
        new_text = pattern.sub(_repl, text)
        return new_text, count
    except re.error as e:
        raise ValueError(f"Ошибка в строке замены: {e}")


def split_to_preview(text: str, matches: list[MatchInfo]):
    segments = []
    last = 0
    for idx, m in enumerate(matches):
        if m.start > last:
            segments.append((text[last:m.start], False, -1))
        segments.append((text[m.start:m.end], True, idx))
        last = m.end
    if last < len(text):
        segments.append((text[last:], False, -1))
    return segments


def humanize_pattern(pattern: str) -> str:
    named = len(re.findall(r"\(\?P<[^>]+>", pattern))
    # Группы вида ( ... ), кроме (?:...), (?=...), (?!...), (?<=...), (?<!...)
    all_groups = len(re.findall(r"(?<!\\)\((?!\?)", pattern))
    non_capturing = len(re.findall(r"\(\?:", pattern))
    return {
        "capturing": all_groups,
        "named": named,
        "non_capturing": non_capturing,
    }