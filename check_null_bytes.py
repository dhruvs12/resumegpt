import os

def check_null_bytes(directory):
    files_with_null = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'rb') as f:
                        data = f.read()
                        if b'\x00' in data:
                            files_with_null.append(filepath)
                except Exception as e:
                    print(f"Failed to read {filepath}: {e}")
    return files_with_null

if __name__ == "__main__":
    directory_to_check = 'resumegpt'  # Adjust if your directory is named differently
    problematic_files = check_null_bytes(directory_to_check)
    if problematic_files:
        print("Files containing null bytes:")
        for file in problematic_files:
            print(f" - {file}")
    else:
        print("No null bytes found in Python files.")
