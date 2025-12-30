# CSV Data Agent - Walkthrough

## Overview
This agent allows you to load CSV files and ask questions in natural language. It uses Llama 3 via Groq to generate Python code (Pandas/Plotly) and executes it to provide answers and charts.

## Implementation Details
- **Core**: Python 3.10+
- **UI**: Streamlit
- **LLM**: Groq API (Llama 3.1 70B Versatile)
- **Viz**: Plotly
- **Security**: Restricted `exec()` environment

## How to Run

### 1. Requirements
Ensure you have the virtual environment set up and activated:
```bash
cd csv_data_agent
venv\Scripts\activate
```

### 2. Configure API Key
The app will ask for your Groq API Key in the sidebar if not set in `.env`.
If you want to set it permanently:
1. Create a `.env` file (copy from `.env.example` if exists, or just create new).
2. Add: `GROQ_API_KEY=gsk_...`

### 3. Launch the App
```bash
streamlit run app.py
```
The application will open in your browser at `http://localhost:8501`.

## Features
- **Smart CSV Load**: Auto-detects separators and encodings.
- **Schema Analysis**: Automatically extracts metadata to help the LLM understand your data.
- **Interactive Charts**: Ask for "plots" or "graphs" to see interactive Plotly visualizations.
- **Code Inspection**: Expand the "Ver código" block in the chat to see exactly what Python code was generated.

## Verification
We have included a test script to verify the core logic works without the UI:
```bash
python tests/test_core_logic.py
```
This script loads the sample `eventos.csv` (truncated), analyzes the schema, and prints a preview.
