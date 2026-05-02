"""Pipeline orchestration for the PDF-first PageIndex workflow."""

from __future__ import annotations

import asyncio
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .answer_generator import answer_from_evidence
from .config import PipelineSettings, ensure_output_dir
from .models import QueryOutput, QueryTiming, SelectedNode
from .pdf_loader import annotate_image_presence, make_doc_id
from .retriever import DEFAULT_EXCLUDED_TITLES, build_node_map, collect_evidence, run_tree_search
from .summarizer import generate_retrieval_summaries
from .tree_builder import build_tree, convert_repo_tree_to_docs_style
from .tree_refiner import refine_tree_hierarchy
from .io_utils import print_tree_stats, save_json


class PageIndexPdfPipeline:
    """Run index construction, retrieval, answer generation, and output persistence."""
    def __init__(self, settings: PipelineSettings) -> None:
        """Initialize the pipeline with runtime settings."""
        self.settings = settings
        self.output_dir = ensure_output_dir(settings.output_dir)

    def build_index(self, pdf_path: str) -> tuple[dict[str, Any], dict[str, Any]]:
        """Build the PageIndex tree and prepare retrieval metadata.
        
        This constructs a hierarchical document tree from a PDF, refines it, annotates
        images, and generates retrieval-oriented summaries. Uses asyncio.run() for
        proper event loop management across multiple invocations.
        
        Args:
            pdf_path: Path to the PDF file to process.
            
        Returns:
            Tuple of (tree_doc, metrics) where tree_doc contains the indexed structure
            and metrics contains build statistics and timing information.
            
        Raises:
            FileNotFoundError: If the PDF file is not found.
            ValueError: If the PDF is invalid or corrupted.
        """
        doc_id = make_doc_id(pdf_path)
        repo_tree, tree_build_time = build_tree(
            pdf_path=pdf_path,
            model=self.settings.model,
            toc_check_pages=self.settings.toc_check_pages,
            max_pages_per_node=self.settings.max_pages_per_node,
            max_tokens_per_node=self.settings.max_tokens_per_node,
        )

        tree_doc = convert_repo_tree_to_docs_style(repo_tree, doc_id)
        refine_tree_hierarchy(tree_doc["result"], pdf_path)
        annotate_image_presence(tree_doc["result"], pdf_path)
        build_node_map(tree_doc["result"])

        # Use asyncio.run() for proper event loop management across multiple calls
        asyncio.run(generate_retrieval_summaries(tree_doc["result"], self.settings.model))

        metrics = {
            "doc_id": doc_id,
            "pdf_path": str(Path(pdf_path).resolve()),
            "model": self.settings.model,
            "settings": {
                "toc_check_pages": self.settings.toc_check_pages,
                "max_pages_per_node": self.settings.max_pages_per_node,
                "max_tokens_per_node": self.settings.max_tokens_per_node,
            },
            "timing": {
                "tree_build_seconds": round(tree_build_time, 3),
            },
        }
        return tree_doc, metrics

    def run_queries(self, tree_doc: dict[str, Any], queries: list[str]) -> list[QueryOutput]:
        """Run retrieval and answer generation for each query.
        
        For each query, executes tree search to locate relevant nodes, collects evidence,
        and generates an answer using the retrieved context.
        
        Args:
            tree_doc: The indexed document tree from build_index().
            queries: List of natural language queries to answer.
            
        Returns:
            List of QueryOutput objects containing retrieval results, selected nodes,
            timing info, and generated answers.
            
        Raises:
            ValueError: If queries list is empty or tree_doc is invalid.
        """
        if not queries:
            return []
            
        tree_result = tree_doc["result"]
        node_map = build_node_map(tree_result)
        outputs: list[QueryOutput] = []

        for query in queries:
            try:
                retrieval_result, retrieval_time, raw_search = run_tree_search(
                    tree_result=tree_result,
                    query=query,
                    model=self.settings.model,
                    exclude_titles=DEFAULT_EXCLUDED_TITLES,
                )
                evidence, selected_nodes = collect_evidence(node_map, retrieval_result.get("node_list", []), max_nodes=self.settings.top_k)
                answer, answer_time = answer_from_evidence(query, evidence, self.settings.model)
                total_time = retrieval_time + answer_time

                output = QueryOutput(
                    query=query,
                    tree_search=retrieval_result,
                    tree_search_raw=raw_search,
                    selected_nodes=[
                        SelectedNode(
                            node_id=node["node_id"],
                            title=node["title"],
                            path=node["path"],
                            start_index=node["start_index"],
                            end_index=node["end_index"],
                            has_images=node.get("has_images", False),
                            image_pages=node.get("image_pages", []),
                        )
                        for node in selected_nodes
                    ],
                    timing=QueryTiming(
                        retrieval_seconds=round(retrieval_time, 3),
                        answer_seconds=round(answer_time, 3),
                        total_seconds=round(total_time, 3),
                    ),
                    answer=answer,
                )
                outputs.append(output)
            except Exception as e:
                print(f"Error processing query '{query}': {str(e)}")
                # Create a failed output to maintain structure
                output = QueryOutput(
                    query=query,
                    tree_search={"error": str(e)},
                    tree_search_raw="",
                    selected_nodes=[],
                    timing=QueryTiming(retrieval_seconds=0, answer_seconds=0, total_seconds=0),
                    answer=f"Error: {str(e)}",
                )
                outputs.append(output)
        return outputs

    def save_outputs(self, pdf_path: str, tree_doc: dict[str, Any], metrics: dict[str, Any], query_outputs: list[QueryOutput]) -> None:
        """Write tree, metrics, and query outputs to disk.
        
        Saves three JSON files to the output directory:
        - {base_name}_tree.json: The indexed document structure
        - {base_name}_build_metrics.json: Build timing and settings
        - {base_name}_qa_results.json: Query results and answers (if queries were run)
        
        Args:
            pdf_path: Original PDF file path (used to determine output filename).
            tree_doc: The indexed document tree.
            metrics: Build metrics and timing information.
            query_outputs: List of query outputs from run_queries().
            
        Raises:
            OSError: If output directory is not writable.
            IOError: If write operations fail.
        """
        base_name = Path(pdf_path).stem
        save_json(self.output_dir / f"{base_name}_tree.json", tree_doc)
        save_json(self.output_dir / f"{base_name}_build_metrics.json", metrics)
        if query_outputs:
            save_json(
                self.output_dir / f"{base_name}_qa_results.json",
                {
                    "doc_id": tree_doc["doc_id"],
                    "results": [
                        {
                            "query": item.query,
                            "tree_search": item.tree_search,
                            "tree_search_raw": item.tree_search_raw,
                            "selected_nodes": [asdict(node) for node in item.selected_nodes],
                            "timing": asdict(item.timing),
                            "answer": item.answer,
                        }
                        for item in query_outputs
                    ],
                },
            )

    def print_run_summary(self, tree_doc: dict[str, Any], query_outputs: list[QueryOutput]) -> None:
        """Print a concise run summary to the console.
        
        Displays tree statistics and per-query results with timing information.
        
        Args:
            tree_doc: The indexed document tree.
            query_outputs: List of query outputs from run_queries().
        """
        print_tree_stats(tree_doc["result"])
        for item in query_outputs:
            print("\n=== Query ===")
            print(item.query)
            print(f"Selected nodes: {[node.node_id for node in item.selected_nodes]}")
            for node in item.selected_nodes:
                print(
                    f"- {node.node_id} | {node.path} | pages {node.start_index}-{node.end_index} | has_images={node.has_images}"
                )
            print(f"Retrieval time: {item.timing.retrieval_seconds:.2f}s")
            print(f"Answer time: {item.timing.answer_seconds:.2f}s")
            print(f"Total time: {item.timing.total_seconds:.2f}s")
            print("Answer:")
            print(item.answer)
