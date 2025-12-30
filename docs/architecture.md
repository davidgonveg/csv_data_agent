# Architecture Documentation

## System Overview

The CSV Data Agent is a Retrieval-Augmented Generation (RAG) style application that, instead of retrieving text, retrieves *schema information* to generate *executable code*.

### High-Level Data Flow

1.  **Ingestion**: User uploads a CSV. `csv_loader.py` handles parsing (auto-detecting separators/encodings).
2.  **Analysis**: `schema_analyzer.py` inspects the DataFrame to extract metadata (column names, types, sample values). This metadata forms the "Context".
3.  **Prompting**: `prompt_builder.py` combines the System Prompt (with Schema Context) and the User Question.
4.  **Generation**: `llm_client.py` sends the prompt to Groq (Llama 3.3 70B). The model returns Python code.
5.  **Execution**: `code_executor.py` runs the code in a restricted `exec()` environment where `df` is pre-loaded.
6.  **Visualization**: Streamlit renders the output (text, DataFrame, or Plotly figure).

## Core Modules

### `src.csv_loader`
- **Responsibility**: Load messy CSVs.
- **Key Logic**: Iterates through common encodings (`utf-8`, `latin-1`) and separators (`,`, `;`, `\t`) until a valid DataFrame is created.

### `src.schema_analyzer`
- **Responsibility**: Shrink the dataset into a text description for the LLM.
- **Key Logic**: It does *not* send the full CSV to the LLM. It sends a summary:
    - Row count
    - Column names & types
    - Min/Max values for numeric/date columns
    - Sample values for categorical columns

### `src.code_executor`
- **Responsibility**: Run untrusted code safely (locally).
- **Security**:
    - Whitelists libraries (`pandas`, `numpy`, `plotly`).
    - Blocks generated code from importing aggressive modules (like `os` or `subprocess`) via a restricted `globals` dict.
    - Captures `stdout` to avoid console clutter.

### `src.llm_client`
- **Responsibility**: Talk to Groq API.
- **Resilience**: Implements simple exponential backoff for Rate Limits (HTTP 429).
