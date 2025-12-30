import pandas as pd
import io

def analyze_schema(df: pd.DataFrame) -> dict:
    """
    Analyze the structure of the DataFrame to provide context for the LLM.
    
    Returns:
        dict: valid JSON-serializable dictionary with schema info.
    """
    columns_info = []
    
    for col in df.columns:
        dtype = str(df[col].dtype)
        null_count = int(df[col].isnull().sum())
        # Safe unique count (limit simple types)
        try:
            nunique = df[col].nunique()
        except:
            nunique = 0
            
        col_info = {
            "name": col,
            "dtype": dtype,
            "null_count": null_count,
            "unique_count": nunique
        }
        
        # Add sample values and range for context
        try:
            non_null = df[col].dropna()
            if not non_null.empty:
                # Samples
                samples = non_null.head(5).tolist()
                col_info["samples"] = samples
                
                # Min/Max for numeric/datetime dates
                if pd.api.types.is_numeric_dtype(df[col]) or pd.api.types.is_datetime64_any_dtype(df[col]):
                    col_info["min"] = str(non_null.min())
                    col_info["max"] = str(non_null.max())
        except Exception:
            pass
            
        columns_info.append(col_info)
        
    return {
        "columns": columns_info,
        "row_count": len(df),
        "column_count": len(df.columns)
    }

def generate_schema_description(df: pd.DataFrame) -> str:
    """
    Generate a text description of the schema for the LLM system prompt.
    """
    schema = analyze_schema(df)
    
    desc = [f"DataFrame with {schema['row_count']} rows and {schema['column_count']} columns."]
    desc.append("Columns:")
    
    for col in schema['columns']:
        line = f"- {col['name']} ({col['dtype']})"
        if 'min' in col and 'max' in col:
            line += f", range: [{col['min']} - {col['max']}]"
        if 'samples' in col:
            samples_str = ", ".join(map(str, col['samples'][:3]))
            line += f", examples: {samples_str}..."
        desc.append(line)
        
    return "\n".join(desc)
