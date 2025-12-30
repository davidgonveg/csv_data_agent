# API Reference

## src.llm_client

### `LLMClient`
Wrapper around the Groq API.
- `__init__(api_key, model="llama-3.3-70b-versatile")`: Initializes client.
- `query(prompt, system=None) -> str`: Sends a chat completion request. Returns the content string.

## src.code_executor

### `execute_code(code: str, df: pd.DataFrame) -> ExecutionResult`
Executes Python code string against a DataFrame context.
- **Args**:
  - `code`: Valid Python string.
  - `df`: Pandas DataFrame.
- **Returns**: `ExecutionResult` object containing `success` (bool), `result` (any), and `error` (str).

## src.csv_loader

### `load_csv(file) -> pd.DataFrame`
Smart loader that handles encoding/separator detection.
- **Args**: File path string or BytesIO object.
- **Returns**: Cleaned Pandas DataFrame.

## src.schema_analyzer

### `generate_schema_description(df) -> str`
Creates one-line-per-column text summary.
- **Format**: `Column Name (Type), Range: [min-max], Samples: a, b, c`

## src.report_generator

### `generate_html_report(messages: list) -> str`
Generates a standalone HTML string from the conversation history.
- **Args**: `messages` list (from `st.session_state.messages`).
- **Features**: Embeds code blocks, tables, and renders Plotly figures as interactive HTML divs.
- **Returns**: HTML string ready for download.
