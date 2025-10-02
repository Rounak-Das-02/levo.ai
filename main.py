from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import yaml
import json
import sqlite3

app = FastAPI()



DB_FILE = "versions.db" ## Name of DB File
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS schemas (
    version INTEGER PRIMARY KEY AUTOINCREMENT,
    application TEXT NOT NULL,
    service TEXT,
    ext TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""") ## Creating a table in the sqlite database

conn.commit()
conn.close()

def validate_json_yaml(file, content):

    ext = Path(file.filename).suffix.lower() ## Getting the file extension

    if ext not in [".yaml", ".json"]:
        raise HTTPException(status_code=400, detail="Only [yaml|json] files allowed.")
    try:
        if ext == ".json":
            data = json.loads(content.decode())
        else:
            data = yaml.safe_load(content)
    except:
        raise HTTPException(status_code=400, detail="invalid json/yaml")
    
    ## We can put more checks in here if needed.
    return data, ext


@app.post("/api/upload")
async def upload_schema(application: str = Form(...), service: str = Form(""), file:UploadFile = Form(...)):
    content = await file.read()
    spec, ext = validate_json_yaml(file, content)
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("INSERT INTO schemas (application, service, ext) VALUES (?, ?, ?)",
              (application, service, ext))
    
    version_id = c.lastrowid

    file_name = f"{version_id}{ext}"

    storage_path = f"storage/{application}/{service}/"

    try:
        Path(f"{storage_path}").mkdir(parents=True, exist_ok=True) ## Creating the folders if they don't exist
    except:
        raise HTTPException(status_code=500)

    try:
        with open(f"{storage_path}/{file_name}", "w") as f:
            f.write(content.decode()) ## Writing the content to the file

        conn.commit()
        conn.close()
    except:
        raise HTTPException(status_code=500, detail="Error occured while saving the file. Please contact support, if it persists")

    return {"message" : "Upload successful", "version_id": version_id}



## Get Latest Version
@app.get("/api/latest")
def get_latest_schema(application: str = Form(...), service: str = Form("")):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
        SELECT version, ext  FROM schemas
        WHERE application=? AND service=?
        ORDER BY version DESC LIMIT 1
    """, (application, service))
    row = c.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="No schema found")

    schema_id, ext = row

    try:
        storage_path = f"storage/{application}/{service}/"
        filepath = f"{storage_path}/{schema_id}{ext}"
        print(filepath)
        content = Path(filepath).read_text()
    except Exception:
        raise HTTPException(status_code=500, detail="Schema file missing")

    return {"schema": content, "version": schema_id}


## Get all versions
@app.get("/api/get-versions")
def list_versions(application: str = Form(...), service: str = Form("")):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT version, created_at FROM schemas
        WHERE application=? AND service=?
        ORDER BY version DESC
    """, (application, service))
    rows = c.fetchall()
    conn.close()
    return {"versions": [{"version": r[0],"created_at": r[1]} for r in rows]}


## Get the file content of a specific version of a schema
@app.get("/api/get-version")
def list_versions(application: str = Form(...), service: str = Form(""), version: int = Form(...)):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT version, ext FROM schemas
        WHERE application=? AND service=? AND version=?
        ORDER BY version DESC
    """, (application, service, version))
    rows = c.fetchone()
    conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail="No schema found")

    schema_id, ext = rows

    try:
        storage_path = f"storage/{application}/{service}/"
        filepath = f"{storage_path}/{schema_id}{ext}"
        content = Path(filepath).read_text()
        if ext == ".json":
            content = json.loads(content)
        else:
            content = yaml.safe_load(content)
    except Exception:
        raise HTTPException(status_code=500, detail="Schema file missing")

    return JSONResponse(content={"schema": content, "version": schema_id})





