"""Generate final answers from retrieved evidence."""

from __future__ import annotations

import time

from pageindex.utils import llm_completion


ANSWER_PROMPT = """
Answer the user's question using only the evidence below.

Question:
{query}

Evidence:
{evidence}

Rules:
- Be precise and concise.
- Use only supported facts from the evidence.
- If the evidence is insufficient, say so.
- Do not repeat yourself.
- End with a short Sources line using node ids and page ranges.
""".strip()


def answer_from_evidence(query: str, evidence: str, model: str) -> tuple[str, float]:
    """Generate a final answer from retrieved evidence using an LLM.
    
    Takes a user query and supporting evidence text, then uses an LLM to generate
    a concise answer citing the evidence. Includes error handling and timing.
    
    Args:
        query: The original user question.
        evidence: Formatted evidence text from collect_evidence().
        model: LLM model name (e.g., 'gpt-4o').
        
    Returns:
        Tuple of (answer_text, elapsed_seconds). Answer includes source citations.
        
    Raises:
        ValueError: If query or model is invalid.
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
    if not model or not model.strip():
        raise ValueError("Model cannot be empty")
    
    try:
        prompt = ANSWER_PROMPT.format(query=query, evidence=evidence or "(No evidence provided)")
        start_time = time.perf_counter()
        answer = llm_completion(model, prompt)
        elapsed = time.perf_counter() - start_time
        
        if not answer:
            print("Warning: Empty answer from LLM")
            return "No answer could be generated from the available evidence.", elapsed
        
        return (answer or "").strip(), elapsed
    except Exception as e:
        print(f"Error generating answer for query '{query}': {str(e)}")
        raise
