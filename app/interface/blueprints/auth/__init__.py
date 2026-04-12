from flask import Blueprint

auth_bp = Blueprint("auth", __name__)

from . import edit_users, login, logout, setup, two_factor
