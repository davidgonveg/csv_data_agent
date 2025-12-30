# System Prompts Reference

This document tracks the prompt engineering strategies used in the agent.

## Main System Prompt

**Location**: `src/prompt_builder.py`

The system prompt is designed to turn the LLM into a "Pandas Code Generator". It enforces strict rules to ensure the output is directly executable.

### Key Instructions Given to LLM:
1.  **Role Persona**: Expert Data Analyst.
2.  **Output Format**: ONLY Python code. No markdown preamble/postscript if possible (though we clean it programmatically).
3.  **Environment**: 
    - `df` variable exists.
    - `result` variable is the target output.
    - `np`, `pd`, `px`, `go` are pre-imported.
4.  **Visualization**: Explicit instruction to use Plotly (`px`) for charts and assign the figure to `result`.

### Context Injection:
We inject the schema description dynamically:
```text
ESQUEMA DEL DATAFRAME:
DataFrame with 50 rows and 7 columns.
Columns:
- timestamp (datetime64[ns]), range: [2024-01-01 - 2024-01-02]
- ...
```

## User Prompt Strategy

We wrap the user's natural language question simply:
```text
Pregunta del usuario: {question}

Genera el código Python necesario:
```
This simplicity relies on the strong System Prompt to control the behavior.
