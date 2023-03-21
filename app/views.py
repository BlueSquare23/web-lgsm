from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .models import User, GameServer
from . import db

views = Blueprint("views", __name__)

######### Home Page #########

@views.route("/", methods=['GET'])
@views.route("/home", methods=['GET'])
@login_required
def home():
    installed_servers = []
    return render_template("home.html", user=current_user, installed_servers=installed_servers)

######### Install Page #########

@views.route("/install", methods=['GET'])
@login_required
def install():
    return render_template("install.html", user=current_user)

######### Add Page #########

@views.route("/add", methods=['GET'])
@login_required
def add():
    return render_template("add.html", user=current_user)
