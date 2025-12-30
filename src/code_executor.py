import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import io
import contextlib
import traceback

class ExecutionResult:
    def __init__(self, success: bool, result: any, error: str = None):
        self.success = success
        self.result = result
        self.error = error

def execute_code(code: str, df: pd.DataFrame) -> ExecutionResult:
    """
    Executes Python code in a restricted namespace.
    
    Args:
        code: The python code to execute.
        df: The pandas DataFrame available as 'df'.
        
    Returns:
        ExecutionResult: Object containing success status, result/figure, or error.
    """
    # 1. Prepare global namespace with allowed libraries
    allowed_globals = {
        "pd": pd,
        "np": np,
        "px": px,
        "go": go,
        "df": df,
        "result": None # Placeholder for output
    }
    
    # 2. Add restrictions (naive sandbox)
    # Removing builtins that are dangerous
    # This is NOT proof against malicious attackers, but prevents accidental mess-ups
    safe_builtins = {
        "len": len,
        "range": range,
        "print": print, # allowed but captured
        "str": str,
        "int": int,
        "float": float,
        "list": list,
        "dict": dict,
        "set": set,
        "tuple": tuple,
        "bool": bool,
        "enumerate": enumerate,
        "zip": zip,
        "min": min,
        "max": max,
        "sum": sum,
        "abs": abs,
        "round": round,
        "hasattr": hasattr,
        "isinstance": isinstance,
        "type": type,
    }
    
    allowed_globals["__builtins__"] = safe_builtins
    
    # Capture stdout just in case
    stdout_buffer = io.StringIO()
    
    try:


        
        with contextlib.redirect_stdout(stdout_buffer):
            # Execute
            exec(code, allowed_globals)
            
        # Extract 'result'
        result_value = allowed_globals.get("result")
        
        return ExecutionResult(success=True, result=result_value)
        
    except Exception:
        error_msg = traceback.format_exc()
        # Clean up traceback to hide internal path details if possible, or just return as is
        return ExecutionResult(success=False, result=None, error=error_msg)
