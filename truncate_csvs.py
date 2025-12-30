import os

files = ['detecciones_bruto.csv', 'detecciones_vivas.csv', 'eventos.csv']
for f in files:
    try:
        if os.path.exists(f):
            # Read first 50 lines
            with open(f, 'r', encoding='utf-8', errors='replace') as fin:
                lines = [fin.readline() for _ in range(50)]
            
            # Write back
            with open(f, 'w', encoding='utf-8') as fout:
                fout.writelines(lines)
            print(f"Truncated {f} to {len(lines)} lines.")
        else:
            print(f"File not found: {f}")
    except Exception as e:
        print(f"Error processing {f}: {e}")
