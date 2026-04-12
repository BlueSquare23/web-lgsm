from flask import Blueprint

main_bp = Blueprint("main", __name__)

from . import home, controls, settings, install, add, edit
from . import about, changelog, jobs, audit, spec
