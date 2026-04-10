"""Tree construction helpers built on top of the PageIndex package."""

from __future__ import annotations

import time
from typing import Any

from pageindex.page_index import page_index_main
from pageindex.utils import ConfigLoader


def ensure_nodes_field(nodes: list[dict[str, Any]]) -> None:
    for node in nodes:
        node.setdefault("nodes", [])
        ensure_nodes_field(node["nodes"])


def convert_repo_tree_to_docs_style(repo_tree: dict[str, Any], doc_id: str) -> dict[str, Any]:
    def convert_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
        converted: list[dict[str, Any]] = []
        for node in nodes:
            item = {
                "title": node["title"],
                "node_id": node["node_id"],
                "page_index": node.get("start_index"),
                "start_index": node.get("start_index"),
                "end_index": node.get("end_index"),
                "text": node.get("text", ""),
                "nodes": convert_nodes(node.get("nodes", []) or []),
            }
            if "summary" in node:
                item["summary"] = node["summary"]
            converted.append(item)
        return converted

    result = convert_nodes(repo_tree["structure"])
    ensure_nodes_field(result)
    return {
        "doc_id": doc_id,
        "status": "completed",
        "doc_name": repo_tree.get("doc_name"),
        "result": result,
    }


def build_tree(
    pdf_path: str,
    model: str,
    toc_check_pages: int,
    max_pages_per_node: int,
    max_tokens_per_node: int,
) -> tuple[dict[str, Any], float]:
    user_options = {
        "model": model,
        "toc_check_page_num": toc_check_pages,
        "max_page_num_each_node": max_pages_per_node,
        "max_token_num_each_node": max_tokens_per_node,
        "if_add_node_id": "yes",
        "if_add_node_summary": "no",
        "if_add_doc_description": "no",
        "if_add_node_text": "yes",
    }
    options = ConfigLoader().load(user_options)
    start_time = time.perf_counter()
    repo_tree = page_index_main(pdf_path, options)
    elapsed = time.perf_counter() - start_time
    return repo_tree, elapsed
