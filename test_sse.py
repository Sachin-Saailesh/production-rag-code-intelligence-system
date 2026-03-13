import requests
import json

url = "http://localhost:8000/api/ingest"
data = {"repo_url": "https://github.com/tiangolo/fastapi.git", "repo_name": "tiangolo/fastapi", "force_reindex": True}

response = requests.post(url, json=data, stream=True)
for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
