# PageIndex PDF RAG

This repository contains a PDF-first implementation of a reasoning-based Retrieval-Augmented Generation (RAG) pipeline built around the PageIndex approach.

The pipeline converts a PDF into a hierarchical tree, generates retrieval-oriented summaries for the tree nodes, retrieves the most relevant nodes for a query, and answers the query using only the selected evidence.

The repository contains a modular Python implementation under `src/` together with the checked-in `pageindex/` package used for tree construction.

## Pipeline Overview

1. **PDF loading**  
   Read the input document page by page with support for text extraction and image detection.

2. **Tree construction**  
   Build a hierarchical structure over the document content using table-of-contents detection or automatic structure inference.

3. **Tree refinement**  
   Clean the initial structure so the sections are more useful for retrieval, removing duplicates and generic sections.

4. **Node summarization**  
   Generate short retrieval-oriented summaries for tree nodes focusing on facts and workflows.

5. **Retrieval**  
   Select the 1-3 most relevant nodes for a query using LLM-based semantic search.

6. **Answer generation**  
   Generate the final answer from the retrieved evidence with source citations.

## Repository Structure

```text
.
|-- README.md               # This file
|-- requirements.txt        # Python dependencies
|-- .env.example            # Environment configuration template
|-- .gitignore
|-- run_pipeline.py         # CLI entry point
|-- src/                    # Core pipeline modules
|   |-- config.py           # Settings and configuration
|   |-- models.py           # Data models
|   |-- pipeline.py         # Main pipeline orchestrator
|   |-- pdf_loader.py       # PDF utilities
|   |-- tree_builder.py     # Tree construction wrapper
|   |-- tree_refiner.py     # Tree cleanup and refinement
|   |-- summarizer.py       # Summary generation
|   |-- retriever.py        # Tree search and evidence collection
|   |-- answer_generator.py # Answer generation from evidence
|   |-- io_utils.py         # I/O and formatting utilities
|   `-- __init__.py
|-- pageindex/              # PageIndex core package
|   |-- page_index.py       # Main page indexing logic
|   |-- utils.py            # LLM utilities and helpers
|   |-- config.yaml         # Default configuration
|   `-- __init__.py
|-- data/
|   |-- input/              # Place PDF files here
|   `-- output/             # Generated outputs
`-- logs/                   # JSON logs (auto-created)
```

## Setup

Recommended Python version: `3.11`(recommended) or `3.12`.
Tested locally with `Python 3.11.9`.

Using Python 3.11 or 3.12 is the safest choice here because some dependency combinations around PDF and LLM tooling can be less predictable on older or newer interpreter versions.

### 1. Create Virtual Environment

```bash
python -m venv .venv

# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and add your credentials:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Then edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=your-api-key
```

If you use an API gateway/proxy, also set:

```env
OPENAI_BASE_URL=https://your-gateway.example.com/v1
```

## Usage

### Command Line

Place your PDF in `data/input/` or any accessible location, then run:

```bash
python run_pipeline.py --pdf_path data/input/document.pdf
```

### Query Input (No Terminal `--query` Needed)

Set your query variables directly in `run_pipeline.py`:

```python
SINGLE_QUERY = "Your one query here"
BATCH_QUERIES = [
    "Your batch query 1",
    "Your batch query 2",
]
```

Then run only:

```bash
python run_pipeline.py --pdf_path data/input/document.pdf
```

#### Basic Examples

```bash
# Build index with default settings
python run_pipeline.py --pdf_path data/input/document.pdf

# Use a smaller model for lower cost
python run_pipeline.py --pdf_path data/input/document.pdf --model gpt-4o-mini

# Run specific queries from terminal (optional)
python run_pipeline.py \
  --pdf_path data/input/document.pdf \
  --query "What is the main purpose?" \
  --query "What are the key components?"

# Reduce tree complexity for faster processing
python run_pipeline.py \
  --pdf_path data/input/document.pdf \
  --max-pages-per-node 1 \
  --max-tokens-per-node 1000 \
  --toc-check-pages 10
```

#### All Available Arguments

```
--pdf_path PATH                    PDF file path (required)
--model MODEL                      LLM model name (default: gpt-4o)
--toc-check-pages N                Pages to scan for TOC (default: 20)
--max-pages-per-node N             Max pages per tree node (default: 2)
--max-tokens-per-node N            Max tokens per node (default: 1500)
--top-k N                          Retrieved nodes per query (default: 3, max: 10)
--query TEXT                       Custom query (use multiple times for multiple queries)
--output-dir PATH                  Output directory (default: data/output)
```

## Output Format

The pipeline generates three JSON files in the output directory:

### 1. `{document}_tree.json`
Complete document tree structure with nodes, page ranges, and summaries:

```json
{
  "doc_id": "local-abc123def456",
  "doc_name": "document.pdf",
  "status": "completed",
  "result": [
    {
      "node_id": "node-001",
      "title": "Introduction",
      "start_index": 1,
      "end_index": 3,
      "summary": "Provides overview of document topic...",
      "has_images": false,
      "nodes": [
        { "node_id": "node-001-1", ... }
      ]
    }
  ]
}
```

### 2. `{document}_build_metrics.json`
Index construction metrics and settings:

```json
{
  "doc_id": "local-abc123def456",
  "pdf_path": "/full/path/to/document.pdf",
  "model": "gpt-4o",
  "settings": {
    "toc_check_pages": 20,
    "max_pages_per_node": 2,
    "max_tokens_per_node": 1500,
    "excluded_titles": ["contents", "functional requirements", ...]
  },
  "timing": {
    "tree_build_seconds": 45.3
  }
}
```

### 3. `{document}_qa_results.json`
Query execution results with retrieved nodes and generated answers:

```json
{
  "doc_id": "local-abc123def456",
  "results": [
    {
      "query": "What is the main purpose?",
      "selected_nodes": [
        {
          "node_id": "node-001",
          "title": "Introduction",
          "path": "Introduction > Overview",
          "start_index": 1,
          "end_index": 3,
          "has_images": false,
          "image_pages": []
        }
      ],
      "timing": {
        "retrieval_seconds": 2.1,
        "answer_seconds": 1.8,
        "total_seconds": 3.9
      },
      "answer": "The main purpose is to provide...",
      "tree_search": { "thinking": "...", "node_list": [...] }
    }
  ]
}
```

## Troubleshooting

### Configuration & Setup Issues

**Error: "OPENAI_API_KEY not found"**
- Ensure `.env` file exists in repository root
- Verify your API key is set: `OPENAI_API_KEY=...`
- Check you're not accidentally committing `.env` (add to `.gitignore`)

**Error: "Permission denied creating output directory"**
- Check write permissions on the output directory
- Run: `chmod u+w data/output` (Linux/macOS)
- Try specifying a different output directory: `--output-dir /tmp/outputs`

**Error: "Module not found"**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Or specific package
pip install litellm python-dotenv pymupdf pyyaml
```

### PDF Processing Issues

**Error: "PDF file not found"**
- Verify the file path is correct and accessible
- Check file permissions: `ls -la data/input/`
- Use absolute paths if relative paths have issues

**Error: "PDF parsing failed" or "Invalid PDF structure"**
- Ensure the PDF is not corrupted: try opening in a PDF reader
- Try a smaller portion first using a different PDF
- The PDF might use image-based text; OCR is not currently supported

**Error: "No table of contents found"**
- The pipeline automatically falls back to structural analysis
- Results may be less optimal; consider manually adding section breakpoints
- Try increasing `--toc-check-pages` (e.g., 50)

### LLM & API Issues

**Error: "Rate limit exceeded" or "429 Too Many Requests"**
- The pipeline has built-in retry logic with exponential backoff
- Error will be logged; check `logs/*.json` for details
- Wait a few minutes before retrying
- Reduce `--top-k` and `--max-pages-per-node` to speed up processing

**Error: "Model not found"**
- Verify model name is correct: `gpt-4o`, `gpt-4o-mini`, or another model available in your account
- Check you have access in your OpenAI account settings

**Empty or poor quality answers**
- The LLM may not have found sufficient evidence
- Try increasing `--max-pages-per-node` or `--max-tokens-per-node`
- Check that the answer text is actually in the PDF
- Try rephrasing the query with more specific terminology

### Memory & Performance Issues

**Error: "MemoryError" or process killed**
- Large PDFs (500+ pages) can use significant memory
- Reduce `--max-pages-per-node` and `--toc-check-pages`
- Process PDFs in smaller chunks (split files)
- Increase available system memory/swap

**Slow processing**
- Processing speed depends on PDF size and LLM API latency
- Typical speed: 1-3 pages/second during indexing
- Queries add 2-5 seconds each (LLM call overhead)
- Try `gpt-4o-mini`: faster and lower cost than `gpt-4o`
- Reduce `--toc-check-pages` if TOC detection is slow

### Debugging

**Enable verbose logging:**
The pipeline automatically generates `logs/*.json` files with detailed execution info:

```bash
# View latest log file
cat logs/*.json | head -200
```

**Check output files exist:**
```bash
ls -lah data/output/
```

**Validate JSON output:**
```bash
python -m json.tool data/output/document_tree.json | head -50
```

## Known Limitations

1. **OCR Not Supported**: PDFs with images (no selectable text) cannot be processed
2. **Language**: Currently optimized for English documents
3. **Structure**: Works best with well-structured PDFs; unexpected layouts may cause issues
4. **Large Files**: PDFs with 1000+ pages may hit token/API limits
5. **Real-time**: Not suitable for live/streaming document processing

## Error Handling

The pipeline includes comprehensive error handling:

- **Configuration Validation**: Settings are validated on startup
- **PDF Validation**: File existence and format checked before processing
- **LLM Retries**: Automatic retry with exponential backoff (max 10 attempts)
- **Partial Failures**: Single query failures don't crash the pipeline
- **Output Validation**: Directory writeability verified before saving

Errors are logged with full context in `logs/*.json` for debugging.

## Performance Tuning

| Use Case | Recommended Settings |
|----------|---------------------|
| **Fast turnaround** | `--max-pages-per-node 1 --toc-check-pages 5 --top-k 1` |
| **Balanced** | `--max-pages-per-node 2 --toc-check-pages 20 --top-k 3` |
| **High quality** | `--max-pages-per-node 3 --toc-check-pages 50 --top-k 5` |
| **Large documents** | `--max-pages-per-node 2 --max-tokens-per-node 1000 --toc-check-pages 10` |

## Technical Details

### Tree Building
- Detects table of contents (first 20 pages)
- Extracts structure with manual fallback to automatic parsing
- Validates page indices against actual document length
- Handles missing/invalid sections gracefully

### Summarization
- Async concurrent processing of all nodes
- Optimized for retrieval (45-90 words, concrete language)
- Preserves section meaning for accurate search

### Retrieval
- LLM-based tree search with 1-3 node selection
- Excludes generic sections (contents, requirements, etc.)
- Collects full text + metadata for answer generation

### Answer Generation
- Concatenates node evidence with metadata
- Forces citation of node IDs and page ranges
- Single LLM call per query for simplicity

## Development

### Adding Custom Queries

Edit query inputs directly in `run_pipeline.py`:

```python
SINGLE_QUERY = "Your custom question?"
BATCH_QUERIES = [
    "Your custom question 1?",
    "Your custom question 2?",
]
```

### Extending the Pipeline

- **Custom retrievers**: Modify `retriever.py::run_tree_search()`
- **Better summaries**: Update `TREE_SUMMARY_PROMPT` in `summarizer.py`
- **New LLM models**: Handled transparently by `litellm` library
