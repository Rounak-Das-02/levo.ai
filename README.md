# Schema Versioning API

### A lightweight mimic of Levo.ai's `levo import` functionality

> **TODO:** Create a Docker version of this API.

This service is written using **FastAPI**.  
It could be written in Flask, but FastAPI provides **fast development, async support, and automatic API docs**.

---

## Requirements

- Python 3.10+  
- Recommended: use a virtual environment  

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the API
### Start the FastAPI server:

``` 
uvicorn main:app --reload
```


## Using the CLI

You can upload schemas using the included CLI:

```
python3 cli.py --spec <path/to/yaml/json file> --application <application name> --service <service name>
```

- --spec → path to your OpenAPI JSON/YAML file
- --application → application name
- --service → optional service name


## Running Tests
Run unit tests to ensure functionality:

```
python3 test.py
```

Tests cover:
- Uploading JSON/YAML schemas
- Retrieving the latest schema version
- Checking independent versioning for multiple applications/services
- Negative tests for invalid formats or wrong file types



## Filesystem Structure: 

```
storage/
└── <application-name>/
    └── <service-name>/
        ├── 1.yaml
        ├── 2.json
    ├── 3.json       # service-name not specified
    └── 4.yaml       # service-name not specified

```




## API Endpoints

### Upload a schema : 

```
curl -X POST "<BASE_URL>/api/upload" \     
  -F "application=<app-name>" \
  -F "service=<service-name>" \
  -F "file=@<path/to/json|yaml/file>"
```

Eg: 
```
curl -X POST "http://127.0.0.1:8000/api/upload" \     
  -F "application=myapp" \
  -F "service=auth" \
  -F "file=@./openapi.yaml"
```


### Get latest version of schema : 

```
curl -X GET "<BASE_URL>/api/latest" \     
  -F "application=<app-name>" \
  -F "service=<service-name>"
```

Eg: 
```
curl -X GET "http://127.0.0.1:8000/api/latest" \      
  -F "application=myapp" \
  -F "service=auth"
```



### Get all versions of a schema for a particular application/service : 
```
curl -X GET "<BASE_URL>/api/get-versions" \
  -F "application=<application-name>" \
  -F "service=<service-name>(optional)"
```

Eg: 
```
curl -X GET "http://127.0.0.1:8000/api/get-versions" \
  -F "application=app1" \ 
  -F "service=auth"
```


### Get the schema for a particular application/service version : 
```
curl -X GET "<BASE_URL>/api/get-version" \
  -F "application=<application-name>" \
  -F "service=<service-name>(optional)" \
  -F "version=<version number>"

```

Eg: 
```
curl -X GET "http://127.0.0.1:8000/api/get-version" \
  -F "application=app1" \ 
  -F "service=auth" \
  -F "version=1"
```

