from __future__ import annotations

import argparse
from pathlib import Path

from src.config import PipelineSettings, load_environment


# -------------------------------------------
# Query Configuration (edit these directly)
# -------------------------------------------
# If set, this one query will run.
# SINGLE_QUERY: str | None = None
SINGLE_QUERY = "What are the main discussion themes?"
# Add multiple queries here for batch runs.
BATCH_QUERIES: list[str] = []


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the PDF pipeline."""
    parser = argparse.ArgumentParser(description="Run the PDF-first PageIndex pipeline locally")
    parser.add_argument("--pdf_path", required=True, help="Path to the input PDF file")
    parser.add_argument("--model", default="gpt-4o", help="LLM model used across indexing, retrieval, and answer generation")
    parser.add_argument("--toc-check-pages", type=int, default=20)
    parser.add_argument("--max-pages-per-node", type=int, default=2)
    parser.add_argument("--max-tokens-per-node", type=int, default=1500)
    parser.add_argument("--top-k", type=int, default=3, help="Maximum number of retrieved nodes to send into answer generation")
    parser.add_argument("--query", action="append", default=[], help="Custom query. Use the flag multiple times for multiple questions.")
    parser.add_argument("--output-dir", default="data/output")
    return parser.parse_args()


def main() -> None:
    """Run the pipeline from the command line.
    
    Validates input PDF, loads environment, builds index, runs queries,
    and saves outputs. Includes comprehensive error handling and reporting.
    """
    args = parse_args()
    env_path = load_environment()
    from src.pipeline import PageIndexPdfPipeline

    pdf_path = Path(args.pdf_path)
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    if not pdf_path.suffix.lower() == ".pdf":
        raise ValueError(f"File must be a PDF: {pdf_path}")

    try:
        settings = PipelineSettings(
            model=args.model,
            toc_check_pages=args.toc_check_pages,
            max_pages_per_node=args.max_pages_per_node,
            max_tokens_per_node=args.max_tokens_per_node,
            top_k=args.top_k,
            output_dir=args.output_dir,
        )
    except ValueError as e:
        print(f"Configuration error: {e}")
        raise

    pipeline = PageIndexPdfPipeline(settings)

    print("Building PageIndex tree...")
    if env_path:
        print(f"Loaded environment from: {env_path}")
    
    try:
        tree_doc, metrics = pipeline.build_index(str(pdf_path))
    except Exception as e:
        print(f"Error building index: {e}")
        raise

    queries: list[str] = []

    if SINGLE_QUERY and SINGLE_QUERY.strip():
        queries.append(SINGLE_QUERY.strip())

    if BATCH_QUERIES:
        queries.extend([q.strip() for q in BATCH_QUERIES if q and q.strip()])

    # CLI queries still work and are appended last.
    queries.extend(args.query or [])

    # De-duplicate while preserving order.
    queries = list(dict.fromkeys(queries))

    if not queries:
        print("No queries configured. Set SINGLE_QUERY or BATCH_QUERIES in run_pipeline.py, or pass --query.")

    query_outputs = pipeline.run_queries(tree_doc, queries) if queries else []
    
    try:
        pipeline.save_outputs(str(pdf_path), tree_doc, metrics, query_outputs)
    except (OSError, IOError) as e:
        print(f"Error saving outputs: {e}")
        raise
    
    pipeline.print_run_summary(tree_doc, query_outputs)

    print(f"\nSaved outputs to: {Path(settings.output_dir).resolve()}")


if __name__ == "__main__":
    main()
