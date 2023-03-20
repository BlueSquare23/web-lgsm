from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .models import User
from . import db

views = Blueprint("views", __name__)

######### Home Page #########

@views.route("/", methods=['GET'])
@views.route("/home", methods=['GET'])
@login_required
def home():

    return render_template("home.html", user=current_user)

