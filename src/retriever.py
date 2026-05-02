"""Tree-search retrieval helpers."""

from __future__ import annotations

import copy
import json
import time
from typing import Any

from pageindex.utils import extract_json, llm_completion, remove_fields


DEFAULT_EXCLUDED_TITLES: set[str] = set()

TREE_SEARCH_PROMPT = """
You are given a user question and a PageIndex tree of a document.
Each node contains a node id, title, page range, optional image flag, and a short retrieval summary.

Your task is to find the nodes that are most likely to contain the answer.
Prefer the most specific nodes that directly cover the question.
Avoid front-matter or generic sections unless the question is explicitly about them.
Return 1 to 3 node ids only.

Question: {query}

Document tree:
{tree_json}

Return JSON only in this format:
{{
  "thinking": "brief reasoning",
  "node_list": ["node_id_1", "node_id_2"]
}}
""".strip()


def build_node_map(tree_result: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Build a flat map of node_id -> node dict with path information.
    
    Walks the tree structure and creates a lookup dictionary. Each node's 'path'
    is set to its hierarchical breadcrumb (e.g., "Section 1 > Subsection 1.1").
    
    Args:
        tree_result: List of document tree nodes from build_index().
        
    Returns:
        Dictionary mapping node_id strings to node dictionaries with paths.
    """
    node_map: dict[str, dict[str, Any]] = {}

    def walk(nodes: list[dict[str, Any]], path: list[str]) -> None:
        for node in nodes:
            if not node.get("node_id"):
                print(f"Warning: Node missing node_id: {node.get('title', 'unknown')}")
                continue
            current_path = path + [node["title"]]
            node["path"] = " > ".join(current_path)
            node.setdefault("nodes", [])
            node_map[node["node_id"]] = node
            walk(node["nodes"], current_path)

    walk(tree_result, [])
    return node_map


def minimal_tree_for_search(tree_result: list[dict[str, Any]], exclude_titles: set[str]) -> list[dict[str, Any]]:
    """Build the reduced tree payload sent to the tree-search prompt."""
    tree = copy.deepcopy(tree_result)
    tree = [node for node in tree if node["title"].strip().lower() not in exclude_titles]
    tree = remove_fields(tree, fields=["text"])
    return tree



def run_tree_search(
    tree_result: list[dict[str, Any]],
    query: str,
    model: str,
    exclude_titles: set[str] | None = None,
) -> tuple[dict[str, Any], float, str]:
    """Search the document tree for nodes relevant to a query.
    
    Uses LLM to identify 1-3 most relevant nodes based on the query.
    Includes error handling for API failures and invalid responses.
    
    Args:
        tree_result: List of document tree nodes from build_index().
        query: Natural language query string.
        model: LLM model name (e.g., 'gpt-4o').
        exclude_titles: Set of section titles to exclude from search.
        
    Returns:
        Tuple of (search_result_dict, elapsed_time, raw_response).
        search_result_dict includes 'thinking' and 'node_list' keys.
        
    Raises:
        ValueError: If query is empty or tree_result is invalid.
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
    if not tree_result:
        raise ValueError("Tree result is empty")
    
    try:
        excluded = exclude_titles or DEFAULT_EXCLUDED_TITLES
        tree_json = json.dumps(
            minimal_tree_for_search(tree_result, excluded),
            indent=2,
            ensure_ascii=False
        )
        prompt = TREE_SEARCH_PROMPT.format(query=query, tree_json=tree_json)
        start_time = time.perf_counter()
        raw_response = llm_completion(model, prompt)
        elapsed = time.perf_counter() - start_time
        
        if not raw_response or not raw_response.strip():
            print(f"Warning: Empty response from LLM for query: {query}")
            return {"thinking": "", "node_list": []}, elapsed, raw_response or ""
        
        parsed = extract_json(raw_response or "") or {}
        if not isinstance(parsed, dict):
            print(f"Warning: Invalid JSON structure in response, using defaults")
            parsed = {}
        parsed.setdefault("thinking", "")
        parsed.setdefault("node_list", [])
        
        # Validate node_list is a list of strings
        if isinstance(parsed["node_list"], list):
            parsed["node_list"] = [str(nid) for nid in parsed["node_list"]]
        else:
            print(f"Warning: node_list is not a list, resetting to empty")
            parsed["node_list"] = []
            
        return parsed, elapsed, raw_response or ""
    except Exception as e:
        print(f"Error in tree search for query '{query}': {str(e)}")
        raise
        

def collect_evidence(
    node_map: dict[str, dict[str, Any]],
    node_ids: list[str],
    max_nodes: int = 3,
) -> tuple[str, list[dict[str, Any]]]:
    """Collect evidence text from selected nodes for answer generation.
    
    Retrieves the full text and metadata for specified nodes, formatting them
    for use in LLM answer generation. Handles missing nodes gracefully.
    
    Args:
        node_map: Node dictionary from build_node_map().
        node_ids: List of node_id strings to collect evidence from.
        max_nodes: Maximum number of nodes to include (default 3).
        
    Returns:
        Tuple of (formatted_evidence_text, selected_nodes_list).
    """
    selected_nodes: list[dict[str, Any]] = []
    chunks: list[str] = []
    seen_ids: set[str] = set()

    for node_id in node_ids[:max_nodes]:
        if not node_id:
            continue
        canonical_node_id = str(node_id)
        node = node_map.get(canonical_node_id)
        if not node or canonical_node_id in seen_ids:
            if not node:
                print(f"Warning: Node {node_id} not found in node_map")
            continue
        seen_ids.add(canonical_node_id)
        selected_nodes.append(node)
        pages = f"{node.get('start_index')}-{node.get('end_index')}"
        image_note = "contains images" if node.get("has_images") else "no images detected"
        node_text = node.get('text', '').strip()
        if not node_text:
            print(f"Warning: Node {node['node_id']} has no text content")
        chunks.append(
            f"[Node {node['node_id']}] {node.get('path', node['title'])} | pages {pages} | {image_note}\n"
            f"Summary: {node.get('summary', '')}\n"
            f"Text:\n{node_text}"
        )

    return "\n\n".join(chunks), selected_nodes
