import sys
import os
import pandas as pd
import plotly.express as px

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.report_generator import generate_html_report

def test_report():
    # Mock data
    df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    fig = px.bar(df, x='a', y='b')
    
    messages = [
        {"role": "user", "content": "Hola"},
        {"role": "assistant", "content": "Tabla:", "dataframe": df},
        {"role": "assistant", "content": "Grafico:", "image": fig, "code": "px.bar(...)"}
    ]
    
    html = generate_html_report(messages)
    
    # Validation
    assert "Hola" in html
    assert "<table" in html
    assert "plotly" in html.lower()
    assert "px.bar(...)" in html
    
    with open("test_report.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    print("HTML Generated successfully at test_report.html")

if __name__ == "__main__":
    test_report()
