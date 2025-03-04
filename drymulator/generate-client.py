from fastapi.openapi.utils import get_openapi
from drymulator.server import app
import json
import subprocess

openapi_schema = get_openapi(
    title=app.title,
    version=app.version,
    routes=app.routes,
)

with open("openapi.json", "w") as f:
    json.dump(openapi_schema, f)

subprocess.run(
    "openapi-python-client generate --path openapi.json --config generate-client-config.yaml --meta=setup --overwrite",
    shell=True,
    check=True,
    capture_output=False,
)
