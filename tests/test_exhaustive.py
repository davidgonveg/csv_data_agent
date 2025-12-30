import sys
import os
import pandas as pd
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.csv_loader import load_csv
from src.llm_client import LLMClient
from src.code_executor import execute_code
from src.schema_analyzer import generate_schema_description
from src.prompt_builder import build_system_prompt

# Load env variables
load_dotenv()

def run_tests():
    print("🚀 Starting Exhaustive Tests...")
    
    # 1. Load Data
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'detecciones_bruto.csv')
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        return

    try:
        df = load_csv(csv_path)
        print(f"✅ CSV Loaded: {len(df)} rows")
    except Exception as e:
        print(f"❌ Load Failed: {e}")
        return

    # 2. Setup LLM
    api_key = os.getenv("GROQ_API_KEY")
    mock_mode = False
    
    if not api_key:
        print("⚠️ No GROQ_API_KEY found. using MOCK mode.")
        mock_mode = True
    else:
        print("✅ API Key found. Using REAL LLM.")
        try:
            llm = LLMClient(api_key=api_key)
        except Exception as e:
             print(f"❌ Failed to init LLM: {e}")
             mock_mode = True

    # 3. Analyze Schema
    print("🔍 Analyzing schema...")
    schema_desc = generate_schema_description(df)
    system_prompt = build_system_prompt(schema_desc)
    
    # 4. Define Test Cases
    test_cases = [
        {
            "category": "Simple Query",
            "prompt": "Cuantas filas tiene el dataset?",
            "mock_code": "result = len(df)"
        },
        {
            "category": "Column Operation", 
            "prompt": "Calcula el promedio de la columna power",
            "mock_code": "result = df['power'].mean()"
        },
        {
            "category": "Filtering",
            "prompt": "Filtra las filas donde power sea mayor a -60",
            "mock_code": "result = df[df['power'] > -60]"
        },
        {
            "category": "Plotting",
            "prompt": "Genera un gráfico de dispersión de time vs power",
            "mock_code": "result = px.scatter(df, x='time', y='power')"
        }
    ]

    results_summary = []

    with open("test_report.txt", "w", encoding="utf-8") as f:
        f.write("Evaluation Report\n=================\n")
        
        for i, case in enumerate(test_cases):
            f.write(f"\n--- Test {i+1}: {case['category']} ---\n")
            f.write(f"Prompt: {case['prompt']}\n")
            
            # A. Generate Code
            if mock_mode:
                code = case['mock_code']
                f.write("Mode: Mock\n")
            else:
                try:
                    # Add a small delay to avoid rate limits if running fast
                    import time
                    time.sleep(1)
                    
                    raw_response = llm.query(case['prompt'], system=system_prompt)
                    code = raw_response.replace("```python", "").replace("```", "").strip()
                    f.write("Mode: LLM\n")
                except Exception as e:
                    f.write(f"LLM Error: {e}\n")
                    results_summary.append((case['category'], False, f"LLM Error: {e}"))
                    continue

            f.write(f"Code:\n{code}\n")

            # B. Execute Code
            try:
                exec_result = execute_code(code, df)
                if exec_result.success:
                    f.write("Execution: Success\n")
                    f.write(f"Result Type: {type(exec_result.result)}\n")
                    results_summary.append((case['category'], True, "Success"))
                else:
                    f.write(f"Execution Failed: {exec_result.error}\n")
                    results_summary.append((case['category'], False, "Exec Error"))
            except Exception as e:
                 f.write(f"System Error: {e}\n")
                 results_summary.append((case['category'], False, "System Error"))

        f.write("\n--- Summary ---\n")
        for cat, success, msg in results_summary:
            status = "PASS" if success else "FAIL"
            f.write(f"{status}: {cat} ({msg})\n")

if __name__ == "__main__":
    run_tests()
