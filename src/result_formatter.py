import pandas as pd
import plotly.graph_objects as go
from .code_executor import ExecutionResult

def format_result(execution_result: ExecutionResult) -> dict:
    """
    Formats the execution result for display in Streamlit.
    """
    if not execution_result.success:
        return {
            "type": "error",
            "value": execution_result.error
        }
    
    val = execution_result.result
    
    if isinstance(val, (go.Figure,)):
        return {
            "type": "plot",
            "value": val
        }
        
    if isinstance(val, pd.DataFrame):
        return {
            "type": "dataframe",
            "value": val, # Streamlit handles formatting
            "summary": f"DataFrame ({len(val)} rows)"
        }
        
    if isinstance(val, (int, float, str, bool, np.number)):
        return {
            "type": "text",
            "value": str(val)
        }
        
    if isinstance(val, list):
        return {
            "type": "text",
            "value": str(val)
        }
        
    # Default fallback
    return {
        "type": "text",
        "value": f"Result: {val}"
    }
