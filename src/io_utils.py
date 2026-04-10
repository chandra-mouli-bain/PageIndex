"""Shared utility functions for saving outputs and reporting tree statistics."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

from pageindex.utils import get_leaf_nodes, structure_to_list


def compact_text(text: str, max_chars: int = 10000) -> str:
    cleaned = re.sub(r"\s+", " ", (text or "").strip())
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars - 3] + "..."


def save_json(path: str | Path, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def print_tree_stats(tree_result: list[dict[str, Any]]) -> None:
    safe_tree = copy.deepcopy(tree_result)
    all_nodes = structure_to_list(safe_tree)
    leaf_nodes = get_leaf_nodes(safe_tree)
    spans = [int(node.get("end_index", 0)) - int(node.get("start_index", 0)) + 1 for node in leaf_nodes]
    average_pages = (sum(spans) / len(spans)) if spans else 0.0

    print("Index summary")
    print(f"- total nodes: {len(all_nodes)}")
    print(f"- leaf nodes: {len(leaf_nodes)}")
    print(f"- average pages per leaf: {average_pages:.2f}")
    print("- top-level sections:")
    for node in tree_result[:12]:
        print(f"  - {node['title']} ({node['start_index']}-{node['end_index']})")
