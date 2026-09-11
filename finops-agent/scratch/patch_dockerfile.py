import os

dockerfile_path = '../finops-rag-api/Dockerfile'

with open(dockerfile_path, 'r') as f:
    content = f.read()

target = "RUN pip install --no-cache-dir -r finops-rag-api/requirements.txt"
replacement = "RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu\nRUN pip install --no-cache-dir -r finops-rag-api/requirements.txt"

if target in content and "https://download.pytorch.org/whl/cpu" not in content:
    new_content = content.replace(target, replacement)
    with open(dockerfile_path, 'w') as f:
        f.write(new_content)
    print("Dockerfile patched successfully with CPU-only torch.")
else:
    print("Dockerfile already patched or target not found.")
