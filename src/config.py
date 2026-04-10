from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(slots=True)
class PipelineSettings:
    """Configuration for the PDF pipeline processing.
    
    Attributes:
        model: LLM model identifier (for example 'gpt-4o' or 'gpt-4o-mini')
        toc_check_pages: Number of pages to scan for table of contents
        max_pages_per_node: Maximum pages to include in a single tree node
        max_tokens_per_node: Maximum token count per tree node
        top_k: Number of relevant nodes to retrieve for each query (1-10)
        output_dir: Directory path for saving pipeline outputs
    """
    model: str = "gpt-4o"
    toc_check_pages: int = 20
    max_pages_per_node: int = 2
    max_tokens_per_node: int = 1500
    top_k: int = 3
    output_dir: str = "data/output"
    
    def __post_init__(self) -> None:
        """Validate settings after initialization."""
        if not self.model or not self.model.strip():
            raise ValueError("model cannot be empty")
        if self.toc_check_pages < 1:
            raise ValueError("toc_check_pages must be at least 1")
        if self.max_pages_per_node < 1:
            raise ValueError("max_pages_per_node must be at least 1")
        if self.max_tokens_per_node < 100:
            raise ValueError("max_tokens_per_node must be at least 100")
        if self.top_k < 1 or self.top_k > 10:
            raise ValueError("top_k must be between 1 and 10")
        if not self.output_dir or not self.output_dir.strip():
            raise ValueError("output_dir cannot be empty")


ENV_CANDIDATES = [
    Path.cwd() / ".env",
    Path(__file__).resolve().parents[1] / ".env",
]


def load_environment() -> Path | None:
    """Load the first .env file found in expected local locations.
    
    Searches for .env files in the current working directory and parent directory.
    Also handles backward compatibility for CHATGPT_API_KEY -> OPENAI_API_KEY.
    
    Returns:
        Path to the loaded .env file, or None if no file was found.
    """
    for candidate in ENV_CANDIDATES:
        if candidate.exists():
            load_dotenv(candidate, override=False)
            break
    else:
        candidate = None

    if not os.getenv("OPENAI_API_KEY") and os.getenv("CHATGPT_API_KEY"):
        os.environ["OPENAI_API_KEY"] = os.getenv("CHATGPT_API_KEY")

    # Support gateway-style base URL env vars used in some notebook setups.
    if not os.getenv("OPENAI_BASE_URL") and os.getenv("CHATGPT_API_BASE_URL"):
        os.environ["OPENAI_BASE_URL"] = os.getenv("CHATGPT_API_BASE_URL")
    if not os.getenv("OPENAI_API_BASE") and os.getenv("OPENAI_BASE_URL"):
        os.environ["OPENAI_API_BASE"] = os.getenv("OPENAI_BASE_URL")
    if not os.getenv("OPENAI_API_BASE") and os.getenv("CHATGPT_API_BASE_URL"):
        os.environ["OPENAI_API_BASE"] = os.getenv("CHATGPT_API_BASE_URL")
    return candidate


def ensure_output_dir(path: str | Path) -> Path:
    """Ensure output directory exists, creating it if necessary.
    
    Creates parent directories as needed. Validates that the directory is writable.
    
    Args:
        path: Directory path to ensure exists.
        
    Returns:
        pathlib.Path object pointing to the output directory.
        
    Raises:
        PermissionError: If the directory cannot be created due to permissions.
    """
    output_path = Path(path)
    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise PermissionError(f"Permission denied creating output directory: {output_path}") from e
    except OSError as e:
        raise OSError(f"Error creating output directory: {output_path}") from e
    
    # Verify directory is writable
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(dir=output_path, delete=True):
            pass
    except (OSError, PermissionError) as e:
        raise PermissionError(f"Output directory is not writable: {output_path}") from e
    
    return output_path
