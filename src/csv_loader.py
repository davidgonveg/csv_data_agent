import pandas as pd
import io
import csv
from typing import Union

def load_csv(file: Union[str, io.BytesIO]) -> pd.DataFrame:
    """
    Load a CSV file with robust handling for:
    - Extra trailing commas/columns (misalignment)
    - Encoding detection
    - Date parsing
    """
    try:
        # 1. Determine Separation & Header Count
        # We need to peek at the first line to count headers
        if isinstance(file, str):
            with open(file, 'r', encoding='latin-1') as f:
                first_line = f.readline()
                file_obj = file
        else:
            file.seek(0)
            first_line = file.read().decode('latin-1').splitlines()[0]
            file.seek(0)
            file_obj = file
        
        # Simple detector for delimiter
        sep = ';' if ';' in first_line and first_line.count(';') > first_line.count(',') else ','
        
        # Count headers
        headers = first_line.split(sep)
        n_cols = len(headers)
        
        # 2. Load with strict column usage
        # usecols=range(n_cols) forces pandas to read only the first N columns, 
        # ignoring any trailing extra delimiters in the data rows.
        # index_col=False forces it NOT to use the first column as index even if counts mismatch.
        try:
           df = pd.read_csv(
               file_obj, 
               sep=sep, 
               encoding='utf-8', 
               usecols=range(n_cols),
               index_col=False,
               low_memory=False
           )
        except UnicodeDecodeError:
            if hasattr(file_obj, 'seek'): file_obj.seek(0)
            df = pd.read_csv(
               file_obj, 
               sep=sep, 
               encoding='latin-1', 
               usecols=range(n_cols),
               index_col=False,
               low_memory=False
           )
           
        # 3. Post-Process
        df = _convert_datetimes(df)
        
        return df

    except Exception as e:
        raise ValueError(f"Failed to load CSV: {str(e)}")

def _convert_datetimes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Attempts to convert object/string columns to datetime.
    """
    for col in df.columns:
        if df[col].dtype == 'object':
            # Heuristic: Check first non-null value
            first_valid = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
            if first_valid and isinstance(first_valid, str):
                # Check if looks like date
                # Very naive check: starts with 20xx
                if first_valid.strip().startswith('20') or '-' in first_valid or '/' in first_valid:
                    try:
                        # Attempt conversion
                        df[col] = pd.to_datetime(df[col], errors='ignore')
                    except:
                        pass
    return df
