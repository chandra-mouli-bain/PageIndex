"""Summary generation helpers for retrieval-oriented node summaries."""

from __future__ import annotations

import asyncio
from typing import Any

from pageindex.utils import llm_acompletion, structure_to_list

from .io_utils import compact_text


TREE_SUMMARY_PROMPT = """
You are helping build a PageIndex tree for reasoning-based retrieval.

You are given one section from a document. Write a compact retrieval-oriented summary for this node.
The summary must preserve section meaning and help later tree search.

Rules:
- Focus on concrete scope: workflows, validations, outputs, assumptions, definitions, tables, and UI states.
- Prefer dense factual phrasing over generic prose.
- Do not invent details.
- Do not mention page numbers.
- Keep it under 90 words.
- Return only the summary text.

Section title: {title}
Section path: {path}
Section text:
{text}
""".strip()


async def generate_retrieval_summaries(tree_result: list[dict[str, Any]], model: str) -> None:
    """Generate concise retrieval-oriented summaries for all tree nodes.
    
    Asynchronously processes all nodes in the tree and creates summaries optimized
    for tree search retrieval. Summaries focus on concrete facts, workflows, and outputs.
    
    Args:
        tree_result: Document tree from build_index().
        model: LLM model name (e.g., 'gpt-4o').
        
    Raises:
        ValueError: If tree_result is empty or model is invalid.
    """
    if not tree_result:
        raise ValueError("tree_result cannot be empty")
    if not model or not model.strip():
        raise ValueError("model cannot be empty")
    
    nodes = structure_to_list(tree_result)
    if not nodes:
        print("Warning: No nodes found in tree_result")
        return

    async def build_summary(node: dict[str, Any]) -> tuple[str, str]:
        """Build summary for a single node and return (node_id, summary)."""
        try:
            if not node.get("node_id"):
                print(f"Warning: Skipping node without node_id: {node.get('title', 'unknown')}")
                return node.get("node_id", "unknown"), ""
            
            prompt = TREE_SUMMARY_PROMPT.format(
                title=node["title"],
                path=node.get("path", node["title"]),
                text=compact_text(node.get("text", ""), max_chars=12000),
            )
            summary = await llm_acompletion(model, prompt)
            return node["node_id"], (summary or "").strip()
        except Exception as e:
            print(f"Error generating summary for node '{node.get('title', 'unknown')}': {str(e)}")
            return node.get("node_id", "unknown"), ""

    summaries = await asyncio.gather(*[build_summary(node) for node in nodes], return_exceptions=True)
    
    # Map summaries back to nodes
    summary_map = {}
    for result in summaries:
        if isinstance(result, tuple) and len(result) == 2:
            node_id, summary_text = result
            summary_map[node_id] = summary_text
        elif isinstance(result, Exception):
            print(f"Task failed with exception: {result}")
    
    for node in nodes:
        node["summary"] = summary_map.get(node.get("node_id"), "")
