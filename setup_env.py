import os
import shutil

def setup():
    # Ensure dirs exist
    dirs = ['src', 'tests/sample_data', 'docs']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"Verified directory: {d}")

    # Copy sample data
    src_file = 'eventos.csv'
    dst_file = os.path.join('tests', 'sample_data', 'test_sample.csv')
    
    if os.path.exists(src_file):
        shutil.copy2(src_file, dst_file)
        print(f"Copied {src_file} to {dst_file}")
    else:
        print(f"Warning: {src_file} not found in current directory.")

if __name__ == "__main__":
    setup()
