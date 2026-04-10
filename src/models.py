from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class QueryTiming:
    retrieval_seconds: float
    answer_seconds: float
    total_seconds: float


@dataclass(slots=True)
class SelectedNode:
    node_id: str
    title: str
    path: str
    start_index: int
    end_index: int
    has_images: bool = False
    image_pages: list[int] = field(default_factory=list)


@dataclass(slots=True)
class QueryOutput:
    query: str
    tree_search: dict[str, Any]
    tree_search_raw: str
    selected_nodes: list[SelectedNode]
    timing: QueryTiming
    answer: str
