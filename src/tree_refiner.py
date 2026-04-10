"""Tree cleanup and hierarchy refinement helpers."""

from __future__ import annotations

import re
from typing import Any

from pageindex.utils import get_text_of_pages, write_node_id


def norm_title(title: str) -> str:
    return re.sub(r"\s+", " ", (title or "").strip()).lower()


def dedupe_sections(
    sections: list[dict[str, Any]],
    parent_title: str,
    parent_start: int,
    parent_end: int,
    ancestor_titles: set[str],
) -> list[dict[str, Any]]:
    seen: dict[tuple[str, int, int], dict[str, Any]] = {}
    output: list[dict[str, Any]] = []
    parent_title_normalized = norm_title(parent_title)

    for section in sections:
        section_title = norm_title(section.get("title"))
        section_start = int(section.get("start_index") or section.get("page_index") or 0)
        section_end = int(section.get("end_index") or section_start)

        if not section_title or section_title == parent_title_normalized or section_title in ancestor_titles:
            continue

        key = (section_title, section_start, section_end)
        existing = seen.get(key)
        if existing is None or len(section.get("text", "")) > len(existing.get("text", "")):
            if existing is None:
                output.append(section)
            else:
                output[output.index(existing)] = section
            seen[key] = section

    narrowed = [
        section
        for section in output
        if int(section.get("start_index") or section.get("page_index") or 0) > parent_start
        or int(section.get("end_index") or section.get("start_index") or section.get("page_index") or 0) < parent_end
    ]
    return output if len(output) >= 2 and narrowed else []


def clean_tree_structure(
    nodes: list[dict[str, Any]],
    parent_title: str | None = None,
    depth: int = 0,
    max_depth: int = 3,
) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, int, int]] = set()
    parent_title_normalized = norm_title(parent_title) if parent_title else None

    for node in nodes:
        node.setdefault("nodes", [])
        title_normalized = norm_title(node.get("title"))

        if parent_title_normalized and title_normalized == parent_title_normalized:
            promoted = clean_tree_structure(node.get("nodes", []), parent_title, depth, max_depth)
            for promoted_node in promoted:
                key = (
                    norm_title(promoted_node.get("title")),
                    int(promoted_node.get("start_index") or promoted_node.get("page_index") or 0),
                    int(promoted_node.get("end_index") or promoted_node.get("start_index") or promoted_node.get("page_index") or 0),
                )
                if key not in seen_keys:
                    cleaned.append(promoted_node)
                    seen_keys.add(key)
            continue

        if depth >= max_depth:
            node["nodes"] = []
        else:
            node["nodes"] = clean_tree_structure(node.get("nodes", []), node.get("title"), depth + 1, max_depth)

        key = (
            title_normalized,
            int(node.get("start_index") or node.get("page_index") or 0),
            int(node.get("end_index") or node.get("start_index") or node.get("page_index") or 0),
        )
        if key in seen_keys:
            continue

        seen_keys.add(key)
        cleaned.append(node)

    return cleaned


def normalize_title_for_regex(title: str) -> str:
    parts = [re.escape(part) for part in re.split(r"\s+", (title or "").strip()) if part]
    return r"\s+".join(parts)


def trim_labeled_text_to_title(labeled_text: str, title: str) -> str:
    if not labeled_text:
        return labeled_text
    title_pattern = normalize_title_for_regex(title)
    patterns = [
        rf"(?is)(\d+\.\s*{title_pattern})",
        rf"(?is)([A-Z]\.\s*{title_pattern})",
        rf"(?is)(•\s*{title_pattern})",
        rf"(?is)({title_pattern})",
    ]
    starts: list[int] = []
    for pattern in patterns:
        match = re.search(pattern, labeled_text)
        if match:
            starts.append(match.start())
    if starts:
        labeled_text = labeled_text[min(starts):]
    return labeled_text


def candidate_bullet_title(raw_title: str) -> bool:
    title = re.sub(r"\s+", " ", raw_title).strip(" :-•\t\n\r")
    if not title or len(title) > 80 or len(title.split()) > 8:
        return False
    if title.endswith(".") or ":" in title or "," in title:
        return False
    return bool(re.match(r"^[A-Z][A-Za-z0-9&/()\- ]+$", title))


def extract_headings_from_labeled_text(labeled_text: str, level: int) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    if level == 2:
        pattern = re.compile(r"(?m)^\s*([A-Z])\.\s+([^\n]+?)\s*$")
        for match in pattern.finditer(labeled_text):
            title = re.sub(r"\s+", " ", match.group(2)).strip()
            headings.append({"title": title, "offset": match.start(), "level": 2})
    elif level == 3:
        pattern = re.compile(r"(?m)^\s*•\s+([^\n]+?)\s*$")
        for match in pattern.finditer(labeled_text):
            title = re.sub(r"\s+", " ", match.group(1)).strip()
            if candidate_bullet_title(title):
                headings.append({"title": title, "offset": match.start(), "level": 3})
    return headings


def page_range_from_labeled_chunk(chunk: str, default_start: int, default_end: int) -> tuple[int, int]:
    pages = [int(page) for page in re.findall(r"<start_index_(\d+)>", chunk)]
    if not pages:
        return default_start, default_end
    return min(pages), max(pages)


def split_labeled_text_by_headings(
    labeled_text: str,
    headings: list[dict[str, Any]],
    default_start: int,
    default_end: int,
) -> list[dict[str, Any]]:
    if not headings:
        return []

    sections: list[dict[str, Any]] = []
    for index, heading in enumerate(headings):
        start = heading["offset"]
        end = headings[index + 1]["offset"] if index + 1 < len(headings) else len(labeled_text)
        chunk = labeled_text[start:end].strip()
        if not chunk:
            continue

        start_page, end_page = page_range_from_labeled_chunk(chunk, default_start, default_end)
        clean_text = re.sub(r"<start_index_\d+>|<end_index_\d+>", "", chunk).strip()
        sections.append(
            {
                "title": heading["title"],
                "start_index": start_page,
                "end_index": end_page,
                "page_index": start_page,
                "text": clean_text,
                "nodes": [],
            }
        )
    return sections


def get_labeled_text_cached(pdf_path: str, start_page: int, end_page: int, cache: dict[tuple[int, int], str]) -> str:
    key = (start_page, end_page)
    if key not in cache:
        cache[key] = get_text_of_pages(pdf_path, start_page, end_page, tag=True)
    return cache[key]


def maybe_split_node(
    node: dict[str, Any],
    pdf_path: str,
    depth: int = 0,
    max_depth: int = 3,
    seen: set[tuple[str, int, int]] | None = None,
    text_cache: dict[tuple[int, int], str] | None = None,
    ancestor_titles: set[str] | None = None,
) -> None:
    if seen is None:
        seen = set()
    if text_cache is None:
        text_cache = {}
    if ancestor_titles is None:
        ancestor_titles = set()
    if depth >= max_depth:
        node["nodes"] = []
        return

    start_page = int(node.get("start_index") or node.get("page_index") or 0)
    end_page = int(node.get("end_index") or start_page)
    title = (node.get("title") or "").strip()
    title_normalized = norm_title(title)
    if start_page <= 0 or end_page < start_page:
        return

    state_key = (title_normalized, start_page, end_page)
    if state_key in seen:
        return
    seen.add(state_key)

    labeled_text = get_labeled_text_cached(pdf_path, start_page, end_page, text_cache)
    labeled_text = trim_labeled_text_to_title(labeled_text, title)
    if not labeled_text or len(labeled_text) < 80:
        return

    next_ancestors = set(ancestor_titles)
    next_ancestors.add(title_normalized)

    letter_sections = split_labeled_text_by_headings(
        labeled_text,
        extract_headings_from_labeled_text(labeled_text, level=2),
        start_page,
        end_page,
    )
    letter_sections = dedupe_sections(letter_sections, title, start_page, end_page, next_ancestors)
    if letter_sections:
        node["nodes"] = letter_sections
        for child in node["nodes"]:
            maybe_split_node(child, pdf_path, depth + 1, max_depth, seen, text_cache, next_ancestors)
        return

    bullet_sections = split_labeled_text_by_headings(
        labeled_text,
        extract_headings_from_labeled_text(labeled_text, level=3),
        start_page,
        end_page,
    )
    bullet_sections = dedupe_sections(bullet_sections, title, start_page, end_page, next_ancestors)
    if bullet_sections:
        node["nodes"] = bullet_sections
        for child in node["nodes"]:
            maybe_split_node(child, pdf_path, depth + 1, max_depth, seen, text_cache, next_ancestors)
    else:
        node.setdefault("nodes", [])


def refine_tree_hierarchy(tree_result: list[dict[str, Any]], pdf_path: str) -> None:
    text_cache: dict[tuple[int, int], str] = {}
    for node in tree_result:
        node.setdefault("nodes", [])
        maybe_split_node(node, pdf_path, depth=0, max_depth=3, seen=set(), text_cache=text_cache, ancestor_titles=set())
    cleaned = clean_tree_structure(tree_result, parent_title=None, depth=0, max_depth=3)
    tree_result[:] = cleaned
    write_node_id(tree_result, 0)
