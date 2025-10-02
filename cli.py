import argparse
import requests
from pathlib import Path
import yaml
import json




def validate_json_yaml(file, content):
    ext = Path(file).suffix.lower()

    if ext not in [".yaml", ".json"]:
        raise Exception("Only [yaml|json] files allowed.")
    
    try:
        if ext == ".json":
            data = json.loads(content)
        else:
            data = yaml.safe_load(content)
    except:
        raise Exception("invalid json/yaml")
    
    ## We can put more checks in here if needed.

    return data, ext


parser = argparse.ArgumentParser(description="Upload OpenAPI schema file to FastAPI backend")
parser.add_argument("--spec", required=True, help="Path to OpenAPI spec file (json|yaml)")
parser.add_argument("--application", required=True, help="Application name")
parser.add_argument("--service", default="", help="Service name (optional)")
parser.add_argument("--server", default="http://127.0.0.1:8000", help="Backend server URL")
args = parser.parse_args()

spec_path = Path(args.spec)

if not spec_path.exists():
    print(f"Error: File {args.spec} not found")
    exit(1)

# Prepare multipart form
files = {
    "file": (spec_path.name, open(spec_path, "rb"), "application/octet-stream")
}
data = {
    "application": args.application,
    "service": args.service
}

## Validate json/yaml before upload
try:
    with open(spec_path, "r") as f:
        content = f.read()
    validate_json_yaml(spec_path, content)
except Exception as e:
    print("Error:", e)
    exit(1)

try:
    response = requests.post(f"{args.server}/api/upload", files=files, data=data)
    response.raise_for_status()
    result = response.json()
    print(f"Schema uploaded successfully! Version: {result['version_id']}")
except requests.RequestException as e:
    print("Upload failed:", e)