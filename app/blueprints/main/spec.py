import os
import yaml

from flask_login import login_required, current_user
from flask import request

from . import main_bp

######### Swagger API Docs #########

@main_bp.route("/api/spec")
@login_required
def get_spec():
    spec_path = os.path.join(os.path.dirname(__file__), "specs", "api_spec.yaml")
    with open(spec_path, "r") as f:
        spec = yaml.safe_load(f)

    base_url = request.host_url.rstrip("/")
    api_url = f"{base_url}/api"

    spec["servers"] = [{"url": api_url, "description": "Current host"}]

    return spec


