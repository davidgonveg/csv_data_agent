import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.csv_loader import load_csv
from src.schema_analyzer import analyze_schema, generate_schema_description

def test_loader_and_analyzer():
    csv_path = os.path.join('tests', 'sample_data', 'test_sample.csv')
    
    print(f"Testing with {csv_path}...")
    
    # 1. Test Loader
    try:
        df = load_csv(csv_path)
        print("✅ Load CSV Success")
        print(f"   Rows: {len(df)}, Cols: {len(df.columns)}")
    except Exception as e:
        print(f"❌ Load CSV Failed: {e}")
        return

    # 2. Test Analyzer
    try:
        schema = analyze_schema(df)
        print("✅ Analyze Schema Success")
        print(f"   Detected Columns: {[c['name'] for c in schema['columns']]}")
    except Exception as e:
        print(f"❌ Analyze Schema Failed: {e}")
        return

    # 3. Test Description Generation
    try:
        desc = generate_schema_description(df)
        print("✅ Generate Description Success")
        print("   --- Description Preview ---")
        print(desc[:300] + "...")
    except Exception as e:
        print(f"❌ Generate Description Failed: {e}")

if __name__ == "__main__":
    test_loader_and_analyzer()
