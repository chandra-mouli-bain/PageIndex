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
        rf"(?is)(\u2022\s*{title_pattern})",
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
    title = re.sub(r"\s+", " ", raw_title).strip(" :-\u2022\t\n\r")
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
        pattern = re.compile(r"(?m)^\s*\u2022\s+([^\n]+?)\s*$")
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


def looks_like_running_header(line: str) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped) > 140:
        return False
    if re.search(r"https?://|www\.", stripped, flags=re.IGNORECASE):
        return False
    alpha_count = sum(1 for char in stripped if char.isalpha())
    if alpha_count < 8:
        return False
    upper_ratio = sum(1 for char in stripped if char.isupper()) / alpha_count
    if upper_ratio < 0.85:
        return False
    word_count = len(stripped.split())
    punctuation_count = sum(1 for char in stripped if char in ".,:/-")
    return word_count >= 3 and punctuation_count >= 1


def looks_like_dense_footer_start(line: str) -> bool:
    stripped = line.strip()
    if len(stripped) < 100:
        return False
    word_count = len(stripped.split())
    punctuation_count = sum(1 for char in stripped if char in ",;:()")
    lowercase_count = sum(1 for char in stripped if char.islower())
    alpha_count = sum(1 for char in stripped if char.isalpha())
    if alpha_count == 0:
        return False
    lowercase_ratio = lowercase_count / alpha_count
    return word_count >= 16 and punctuation_count >= 4 and lowercase_ratio >= 0.65


def clean_page_text(raw_text: str) -> str:
    cleaned_lines: list[str] = []
    for raw_line in raw_text.replace("\r", "\n").splitlines():
        line = raw_line.replace("\xa0", " ").replace("Ã‚Â©", "Â©").strip()
        if not line:
            continue
        line = re.sub(r"spglobal\.com/marketintelligence\s*\d*", "", line, flags=re.IGNORECASE).strip()
        if not line:
            continue
        if looks_like_running_header(line):
            continue
        if re.match(r"^[A-Za-z]+\s*(?:©|\(c\))?\s*\d{4}\b", line, flags=re.IGNORECASE):
            continue
        if looks_like_dense_footer_start(line):
            break
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()


def get_clean_page_text(pdf_path: str, page_number: int, cache: dict[tuple[int, int], str]) -> str:
    labeled = get_labeled_text_cached(pdf_path, page_number, page_number, cache)
    plain_text = re.sub(r"<start_index_\d+>|<end_index_\d+>", "", labeled)
    return clean_page_text(plain_text)


def build_text_from_pages(
    pdf_path: str,
    start_page: int,
    end_page: int,
    cache: dict[tuple[int, int], str],
) -> str:
    texts = [get_clean_page_text(pdf_path, page_number, cache) for page_number in range(start_page, end_page + 1)]
    return "\n\n".join([text for text in texts if text]).strip()


def meaningful_lines(page_text: str) -> list[str]:
    return [line.strip() for line in (page_text or "").splitlines() if line.strip()]


def looks_like_sentence(line: str) -> bool:
    words = line.split()
    if len(words) >= 12:
        return True
    if len(words) >= 8 and re.search(r"[,.!?;:]", line):
        return True
    return False


def count_sentence_like_lines(text: str) -> int:
    return sum(1 for line in meaningful_lines(text) if looks_like_sentence(line))


def count_numeric_heavy_lines(text: str) -> int:
    count = 0
    for line in meaningful_lines(text):
        digit_count = sum(1 for char in line if char.isdigit())
        alpha_count = sum(1 for char in line if char.isalpha())
        if digit_count >= 4 and digit_count >= alpha_count:
            count += 1
    return count


def is_person_like_label(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.isupper():
        return False
    if any(character.isdigit() for character in stripped):
        return False
    if "," in stripped or ":" in stripped:
        return False
    words = stripped.split()
    if len(words) < 1 or len(words) > 6:
        return False
    return all(re.match(r"^[A-Z][A-Za-z.'-]*$", word) for word in words)


def is_role_like_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped) > 120:
        return False
    if looks_like_sentence(stripped):
        return False
    words = stripped.split()
    if len(words) > 14:
        return False
    punctuation_hits = sum(token in stripped for token in [",", "&", "/", "(", ")"])
    acronym_hits = sum(1 for word in words if re.fullmatch(r"[A-Z]{2,}", word))
    lowercase_words = sum(1 for word in words if re.search(r"[a-z]", word))
    if stripped.istitle() and len(words) <= 3 and punctuation_hits == 0 and acronym_hits == 0:
        return False
    if looks_like_short_heading(stripped) and len(words) <= 4 and punctuation_hits == 0 and acronym_hits == 0:
        return False
    return punctuation_hits > 0 or acronym_hits > 0 or lowercase_words >= 2


def count_turn_openings(page_text: str, parent_title: str | None = None) -> int:
    lines = meaningful_lines(page_text)
    count = 0
    for index, line in enumerate(lines):
        if parent_title and norm_title(line) == norm_title(parent_title):
            continue
        if re.match(r"^[A-Z][A-Za-z.'\-\s]{1,60}:\s+\S", line):
            count += 1
            continue
        if is_person_like_label(line):
            next_line = lines[index + 1] if index + 1 < len(lines) else ""
            if is_role_like_line(next_line) or (next_line and looks_like_sentence(lines[index + 2]) if index + 2 < len(lines) else False):
                count += 1
    return count


def looks_like_short_heading(line: str) -> bool:
    tokens = [token for token in re.split(r"\s+", line.strip()) if token]
    if not tokens:
        return False
    cleaned_tokens = [re.sub(r"^[^A-Za-z0-9]+|[^A-Za-z0-9&/'()\-]+$", "", token) for token in tokens]
    cleaned_tokens = [token for token in cleaned_tokens if token]
    if not cleaned_tokens:
        return False
    if len(cleaned_tokens) == 1:
        return bool(re.match(r"^[A-Z][A-Za-z0-9&/'()\-]{2,}$", cleaned_tokens[0]))
    capitalized_tokens = sum(
        1
        for token in cleaned_tokens
        if re.match(r"^[A-Z][A-Za-z0-9&/'()\-]*$", token) or re.fullmatch(r"[A-Z&]{1,6}", token)
    )
    short_lowercase_tokens = sum(1 for token in cleaned_tokens if re.match(r"^[a-z&]{1,4}$", token))
    return capitalized_tokens >= max(2, len(cleaned_tokens) - 1) and short_lowercase_tokens <= 2


def looks_like_index_page(text: str) -> bool:
    lines = meaningful_lines(text)
    dot_leader_lines = sum(1 for line in lines if re.search(r"\.{2,}\s*\d+\s*$", line))
    short_index_lines = sum(1 for line in lines if len(line.split()) <= 8 and re.search(r"\d+\s*$", line))
    return dot_leader_lines >= 2 or (len(lines) <= 10 and short_index_lines >= 3)


def looks_like_cover_or_front_matter(text: str) -> bool:
    lines = meaningful_lines(text)
    if not lines:
        return False
    sentence_lines = count_sentence_like_lines(text)
    numeric_heavy_lines = count_numeric_heavy_lines(text)
    return sentence_lines <= 1 and numeric_heavy_lines >= 3


def should_skip_initial_node(title: str, text: str, start_page: int, end_page: int) -> bool:
    if start_page > 3:
        return False
    if looks_like_index_page(text):
        return True
    if start_page == 1 and count_numeric_heavy_lines(text) >= 2 and count_sentence_like_lines(text) <= 2:
        return True
    if end_page <= 2 and looks_like_cover_or_front_matter(text):
        return True
    if looks_like_roster(text):
        return False
    if count_turn_openings(text) >= 2:
        return False
    return False


def score_section_heading(line: str, position: int, next_line: str) -> int:
    normalized = re.sub(r"\s+", " ", line).strip()
    if not normalized:
        return -1
    if len(normalized) > 70 or len(normalized.split()) > 7:
        return -1
    if looks_like_sentence(normalized):
        return -1
    if "," in normalized or normalized.endswith(".") or ":" in normalized:
        return -1
    if re.search(r"https?://|www\.", normalized, flags=re.IGNORECASE):
        return -1
    if re.search(r"\d{4}", normalized):
        return -1
    if is_role_like_line(normalized):
        return -1

    score = 0
    if position == 0:
        score += 3
    elif position <= 2:
        score += 1

    if position == 0 and len(normalized.split()) >= 2:
        score += 1

    letters = [char for char in normalized if char.isalpha()]
    if letters:
        upper_ratio = sum(1 for char in letters if char.isupper()) / len(letters)
        if upper_ratio >= 0.75:
            score += 2

    if looks_like_short_heading(normalized):
        score += 3
    if normalized.isupper():
        score += 1
        if len(normalized.split()) == 1:
            score -= 3
    if len(normalized.split()) >= 2:
        score += 1
    if next_line.isupper() and not normalized.isupper():
        score += 1
    if is_person_like_label(normalized) and is_role_like_line(next_line):
        score -= 4
    if next_line and looks_like_sentence(next_line):
        score += 1

    return score


def infer_page_heading(page_text: str) -> str:
    lines = meaningful_lines(page_text)
    if not lines:
        return ""
    turn_count = count_turn_openings(page_text)
    first_line = re.sub(r"\s+", " ", lines[0]).strip()
    next_line = lines[1] if len(lines) > 1 else ""
    if (
        looks_like_short_heading(first_line)
        and not is_role_like_line(first_line)
        and not looks_like_sentence(next_line)
        and (not is_role_like_line(next_line) or next_line.isupper())
    ):
        return first_line
    best_heading = ""
    best_score = -1
    for index, line in enumerate(lines[:4]):
        next_line = lines[index + 1] if index + 1 < len(lines) else ""
        score = score_section_heading(line, index, next_line)
        if turn_count > 0 and index > 0:
            score -= 3
        if score > best_score:
            best_heading = re.sub(r"\s+", " ", line).strip()
            best_score = score
    if best_score < 3:
        return ""
    if turn_count > 0 and is_person_like_label(best_heading):
        return ""
    return best_heading


def collect_section_boundaries(
    pdf_path: str,
    total_pages: int,
    cache: dict[tuple[int, int], str],
) -> list[tuple[int, str]]:
    boundaries: list[tuple[int, str]] = []
    for page_number in range(1, total_pages + 1):
        page_text = get_clean_page_text(pdf_path, page_number, cache)
        heading = infer_page_heading(page_text)
        if not heading:
            continue
        if boundaries and norm_title(heading) == norm_title(boundaries[-1][1]):
            continue
        boundaries.append((page_number, heading))
    return boundaries


def choose_range_title(nodes: list[dict[str, Any]], start_page: int, end_page: int) -> str:
    for node in nodes:
        node_start = int(node.get("start_index") or node.get("page_index") or 0)
        node_end = int(node.get("end_index") or node_start)
        if node_start <= start_page and node_end >= end_page:
            return node.get("title") or f"Pages {start_page}-{end_page}"
    return f"Page {start_page}" if start_page == end_page else f"Pages {start_page}-{end_page}"


def looks_like_roster(section_text: str) -> bool:
    lines = meaningful_lines(section_text)
    if len(lines) < 6:
        return False
    short_lines = sum(1 for line in lines if len(line.split()) <= 6 and not looks_like_sentence(line))
    name_lines = sum(1 for line in lines if is_person_like_label(line))
    sentence_lines = sum(1 for line in lines if looks_like_sentence(line))
    return short_lines >= max(6, len(lines) // 2) and name_lines >= 3 and sentence_lines <= max(2, len(lines) // 6)


def title_case_heading(text: str) -> str:
    words = [word.lower() for word in text.split()]
    return " ".join(word.capitalize() for word in words)


def split_inline_tail_label(line: str) -> list[str]:
    person_token = r"(?:[A-Z][a-z]+(?:[.'-][A-Za-z]+)?|[A-Z]\.)"
    match = re.search(rf"^(.*?)({person_token}(?:\s+{person_token}){{1,3}})$", line.strip())
    if not match:
        return [line]
    prefix = match.group(1)
    suffix = match.group(2)
    if not prefix or prefix[-1].isspace():
        return [line]
    left = prefix.strip()
    right = suffix.strip()
    if not left or not right:
        return [line]
    return [left, right]


def expand_roster_lines(section_text: str) -> list[str]:
    expanded: list[str] = []
    for line in meaningful_lines(section_text):
        expanded.extend(split_inline_tail_label(line))

    return expanded


def split_roster_groups(section_text: str, start_page: int, end_page: int) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    current_title: str | None = None
    current_lines: list[str] = []

    def flush_group() -> None:
        nonlocal current_title, current_lines
        if not current_title or not current_lines:
            current_title = None
            current_lines = []
            return
        nodes.append(
            {
                "title": current_title,
                "start_index": start_page,
                "end_index": end_page,
                "page_index": start_page,
                "text": "\n".join(current_lines).strip(),
                "nodes": [],
            }
        )
        current_title = None
        current_lines = []

    for line in expand_roster_lines(section_text):
        if line.isupper() and len(line.split()) <= 4 and not is_person_like_label(line):
            flush_group()
            current_title = title_case_heading(line)
            continue
        if current_title:
            current_lines.append(line)

    flush_group()
    return nodes


def build_dialogue_nodes(
    pdf_path: str,
    start_page: int,
    end_page: int,
    parent_title: str,
    cache: dict[tuple[int, int], str],
) -> list[dict[str, Any]]:
    indexed_lines: list[tuple[int, str]] = []
    for page_number in range(start_page, end_page + 1):
        page_text = get_clean_page_text(pdf_path, page_number, cache)
        for line in meaningful_lines(page_text):
            indexed_lines.append((page_number, line))

    nodes: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    index = 0

    def flush_current() -> None:
        nonlocal current
        if not current:
            return
        content_lines = [line for line in current["content_lines"] if line.strip()]
        if content_lines:
            text_parts = [current["title"]]
            if current["descriptor"]:
                text_parts.append(current["descriptor"])
            text_parts.append("\n".join(content_lines).strip())
            nodes.append(
                {
                    "title": current["title"],
                    "start_index": current["start_page"],
                    "end_index": current["end_page"],
                    "page_index": current["start_page"],
                    "text": "\n".join(part for part in text_parts if part).strip(),
                    "nodes": [],
                }
            )
        current = None

    while index < len(indexed_lines):
        page_number, line = indexed_lines[index]
        if norm_title(line) == norm_title(parent_title):
            index += 1
            continue

        colon_match = re.match(r"^([A-Z][A-Za-z.'\-\s]{1,60}):\s+(.+)$", line)
        if colon_match:
            flush_current()
            current = {
                "title": re.sub(r"\s+", " ", colon_match.group(1)).strip(),
                "descriptor": "",
                "start_page": page_number,
                "end_page": page_number,
                "content_lines": [colon_match.group(2).strip()],
            }
            index += 1
            continue

        next_line = indexed_lines[index + 1][1] if index + 1 < len(indexed_lines) else ""
        if is_person_like_label(line) and is_role_like_line(next_line):
            flush_current()
            current = {
                "title": line,
                "descriptor": next_line,
                "start_page": page_number,
                "end_page": indexed_lines[index + 1][0] if index + 1 < len(indexed_lines) else page_number,
                "content_lines": [],
            }
            index += 2
            continue

        next_next_line = indexed_lines[index + 2][1] if index + 2 < len(indexed_lines) else ""
        if is_person_like_label(line) and looks_like_short_heading(next_line) and next_next_line and looks_like_sentence(next_next_line):
            flush_current()
            current = {
                "title": line,
                "descriptor": next_line,
                "start_page": page_number,
                "end_page": indexed_lines[index + 1][0] if index + 1 < len(indexed_lines) else page_number,
                "content_lines": [],
            }
            index += 2
            continue

        if is_person_like_label(line):
            following = next_line
            if following and looks_like_sentence(following):
                if looks_like_short_heading(line) and len(line.split()) >= 2:
                    index += 1
                    continue
                flush_current()
                current = {
                    "title": line,
                    "descriptor": "",
                    "start_page": page_number,
                    "end_page": page_number,
                    "content_lines": [],
                }
                index += 1
                continue

        if current is not None:
            current["content_lines"].append(line)
            current["end_page"] = page_number

        index += 1

    flush_current()
    return nodes


def looks_like_conversational_document(
    tree_result: list[dict[str, Any]],
    pdf_path: str,
    cache: dict[tuple[int, int], str],
) -> bool:
    total_pages = max(
        int(node.get("end_index") or node.get("start_index") or node.get("page_index") or 0)
        for node in tree_result
    )
    if total_pages <= 0:
        return False

    pages_with_turns = 0
    for page_number in range(1, min(total_pages, 10) + 1):
        page_text = get_clean_page_text(pdf_path, page_number, cache)
        if count_turn_openings(page_text) >= 2:
            pages_with_turns += 1
    return pages_with_turns >= 2


def rebuild_conversational_tree(
    tree_result: list[dict[str, Any]],
    pdf_path: str,
    cache: dict[tuple[int, int], str],
) -> list[dict[str, Any]]:
    total_pages = max(
        int(node.get("end_index") or node.get("start_index") or node.get("page_index") or 0)
        for node in tree_result
    )
    if total_pages <= 0:
        return []

    boundaries = collect_section_boundaries(pdf_path, total_pages, cache)
    if not boundaries:
        return []

    nodes: list[dict[str, Any]] = []
    if boundaries[0][0] > 1:
        initial_text = build_text_from_pages(pdf_path, 1, boundaries[0][0] - 1, cache)
        initial_title = choose_range_title(tree_result, 1, boundaries[0][0] - 1)
        if not should_skip_initial_node(initial_title, initial_text, 1, boundaries[0][0] - 1):
            nodes.append(
                {
                    "title": initial_title,
                    "start_index": 1,
                    "end_index": boundaries[0][0] - 1,
                    "page_index": 1,
                    "text": initial_text,
                    "nodes": [],
                }
            )

    for index, (start_page, title) in enumerate(boundaries):
        next_start = boundaries[index + 1][0] if index + 1 < len(boundaries) else total_pages + 1
        end_page = next_start - 1
        if end_page < start_page:
            continue

        section_text = build_text_from_pages(pdf_path, start_page, end_page, cache)
        if should_skip_initial_node(title, section_text, start_page, end_page):
            continue
        child_nodes: list[dict[str, Any]] = []

        if looks_like_roster(section_text):
            section_text = "\n".join(expand_roster_lines(section_text)).strip()
            child_nodes = split_roster_groups(section_text, start_page, end_page)
        else:
            dialogue_nodes = build_dialogue_nodes(pdf_path, start_page, end_page, title, cache)
            if len(dialogue_nodes) >= 2:
                child_nodes = dialogue_nodes

        nodes.append(
            {
                "title": title,
                "start_index": start_page,
                "end_index": end_page,
                "page_index": start_page,
                "text": section_text,
                "nodes": child_nodes,
            }
        )

    return nodes if len(nodes) >= 2 else []


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

    page_text = build_text_from_pages(pdf_path, start_page, end_page, text_cache)
    if looks_like_roster(page_text):
        roster_nodes = split_roster_groups(page_text, start_page, end_page)
        roster_nodes = dedupe_sections(roster_nodes, title, start_page, end_page, ancestor_titles or set())
        if roster_nodes:
            node["nodes"] = roster_nodes
            return

    dialogue_nodes = build_dialogue_nodes(pdf_path, start_page, end_page, title, text_cache)
    if len(dialogue_nodes) >= 2:
        node["nodes"] = dialogue_nodes
        return

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
    if tree_result and looks_like_conversational_document(tree_result, pdf_path, text_cache):
        rebuilt = rebuild_conversational_tree(tree_result, pdf_path, text_cache)
        if rebuilt:
            tree_result[:] = rebuilt
            cleaned = clean_tree_structure(tree_result, parent_title=None, depth=0, max_depth=3)
            tree_result[:] = cleaned
            write_node_id(tree_result, 0)
            return

    for node in tree_result:
        node.setdefault("nodes", [])
        maybe_split_node(node, pdf_path, depth=0, max_depth=3, seen=set(), text_cache=text_cache, ancestor_titles=set())
    cleaned = clean_tree_structure(tree_result, parent_title=None, depth=0, max_depth=3)
    tree_result[:] = cleaned
    write_node_id(tree_result, 0)
