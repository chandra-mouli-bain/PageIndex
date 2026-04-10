"""PDF utilities used by the pipeline."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pymupdf


def make_doc_id(pdf_path: str) -> str:
    digest = hashlib.md5(Path(pdf_path).resolve().as_posix().encode("utf-8")).hexdigest()[:12]
    return f"local-{digest}"


def annotate_image_presence(tree_result: list[dict[str, Any]], pdf_path: str) -> dict[int, int]:
    document = pymupdf.open(pdf_path)
    page_image_count: dict[int, int] = {}

    for index in range(len(document)):
        try:
            page_image_count[index + 1] = len(document[index].get_images(full=True))
        except Exception:
            page_image_count[index + 1] = 0
    document.close()

    def walk(nodes: list[dict[str, Any]]) -> None:
        for node in nodes:
            start_page = int(node.get("start_index") or node.get("page_index") or 0)
            end_page = int(node.get("end_index") or start_page)
            image_pages = [page for page in range(start_page, end_page + 1) if page_image_count.get(page, 0) > 0]
            node["has_images"] = bool(image_pages)
            if image_pages:
                node["image_pages"] = image_pages
            walk(node.get("nodes", []) or [])

    walk(tree_result)
    return page_image_count
