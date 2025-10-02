import pytest
import requests

BASE_URL = "http://127.0.0.1:8000"

# --- Sample valid schemas ---
valid_json = """
{
  "openapi": "3.0.0",
  "info": {"title": "Test API", "version": "1.0.0"},
  "paths": {"/test": {}}
}
"""

valid_yaml = """
openapi: "3.0.0"
info:
  title: Test API
  version: "1.0.0"
paths:
  /test: {}
"""

#### Sample invalid schemas / wrong files ####
invalid_json = "{ invalid json }"
invalid_yaml = "openapi: 3.0.0\ninfo\ntitle: Missing colons"
wrong_file_content = "Just a plain text file."


#### Positive Tests ####


def upload_schema(app, service, file_name, content, mime):
    resp = requests.post(
        f"{BASE_URL}/api/upload",
        data={"application": app, "service": service},
        files={"file": (file_name, content, mime)}
    )
    assert resp.status_code == 200
    return resp.json()["version_id"]

def get_latest_version(app, service):
    resp = requests.get(
        f"{BASE_URL}/api/latest",
        data={"application": app, "service": service}
    )
    assert resp.status_code == 200
    data = resp.json()
    return data["version"], data["schema"]

def test_upload_and_get_latest():
    app, service = "app1", "service1"

    v1 = upload_schema(app, service, "openapi.json", valid_json, "application/json")
    latest_v, schema = get_latest_version(app, service)
    assert latest_v == v1
    assert "/test" in schema

    v2 = upload_schema(app, service, "openapi.yaml", valid_yaml, "application/x-yaml")
    latest_v2, schema2 = get_latest_version(app, service)
    assert latest_v2 == v2
    assert "/test" in schema2
    assert latest_v2 > latest_v

def test_independent_app_versions():
    # Upload to app1/auth
    v1 = upload_schema("app1", "auth", "openapi.json", valid_json, "application/json")
    # Upload to app2/payment
    v2 = upload_schema("app2", "payment", "openapi.yaml", valid_yaml, "application/x-yaml")

    latest_v1, _ = get_latest_version("app1", "auth")
    latest_v2, _ = get_latest_version("app2", "payment")

    assert latest_v1 == v1
    assert latest_v2 == v2
    assert latest_v1 != latest_v2  # just to confirm they are independent

# ---------------------------
# Negative Tests
# ---------------------------

def test_upload_invalid_json():
    resp = requests.post(
        f"{BASE_URL}/api/upload",
        data={"application": "app1", "service": "auth"},
        files={"file": ("invalid.json", invalid_json, "application/json")}
    )
    assert resp.status_code == 400
    assert "invalid" in resp.json()["detail"].lower()

def test_upload_invalid_yaml():
    resp = requests.post(
        f"{BASE_URL}/api/upload",
        data={"application": "app1", "service": "auth"},
        files={"file": ("invalid.yaml", invalid_yaml, "application/x-yaml")}
    )
    assert resp.status_code == 400
    assert "invalid" in resp.json()["detail"].lower()
    

def test_upload_wrong_file_type():
    resp = requests.post(
        f"{BASE_URL}/api/upload",
        data={"application": "app1", "service": "auth"},
        files={"file": ("test.txt", wrong_file_content, "text/plain")}
    )
    assert resp.status_code == 400
    assert "only" in resp.json()["detail"].lower()