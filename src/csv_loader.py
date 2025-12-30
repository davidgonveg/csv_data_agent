import pandas as pd
import io
from typing import Union

def load_csv(file: Union[str, io.BytesIO]) -> pd.DataFrame:
    """
    Load a CSV file from a path or BytesIO object into a pandas DataFrame.
    
    Args:
        file: File path (str) or BytesIO object.
        
    Returns:
        pd.DataFrame: Loaded data.
        
    Raises:
        ValueError: If file cannot be read.
    """
    try:
        # Try default encoding/separator first
        # We use low_memory=False to avoid mixed type warnings on large files, 
        # though for this agent we expect manageable sizes or use chunking conceptually.
        # Here we just load fully as per requirements.
        
        # Helper to read with different encodings if utf-8 fails
        encodings = ['utf-8', 'latin-1', 'cp1252']
        separators = [',', ';', '\t']
        
        for encoding in encodings:
            for sep in separators:
                try:
                    if isinstance(file, (str, io.BytesIO)):
                        # If it's BytesIO, we need to reset pointer for retries, 
                        # but pandas read_csv usually handles the stream. 
                        # However, resetting is safer if we reuse the object.
                        if hasattr(file, 'seek'):
                            file.seek(0)
                            
                    df = pd.read_csv(file, sep=sep, encoding=encoding, low_memory=False)
                    
                    # Basic heuristic: if we have 1 column but arguably should have more, 
                    # maybe the separator is wrong. 
                    # But single column CSVs exist. 
                    # We'll assume if it parses without error, it's "valid" enough for now.
                    # A stricter check could be: if len(df.columns) == 1 and sep == ',', try ';'
                    
                    if len(df.columns) > 1:
                        return df
                    
                    # If 1 column, store it as a fallback but keep trying other separators
                    # actually, sticking to the first successful parse is standard unless we define strict validation.
                    # Let's return only if it looks "good" (e.g. >1 column), otherwise continue search.
                    # If we run out of options, we return the 1-column version.
                    
                except UnicodeDecodeError:
                    continue
                except pd.errors.ParserError:
                    continue
                except Exception:
                    continue
        
        # If we are here, we might have skipped a 1-column valid CSV or failed completely.
        # Let's try one last robust attempt with default settings and raise if fails.
        if hasattr(file, 'seek'):
            file.seek(0)
        return pd.read_csv(file, encoding='latin-1') # Fallback to latin-1 which is permissive

    except Exception as e:
        raise ValueError(f"Failed to load CSV: {str(e)}")
