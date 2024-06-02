#!/usr/bin/env python3
# Standalone cli script for changing web-lgsm login password.

import os
try:
    os.environ["VIRTUAL_ENV"]
except KeyError:
    exit(" [!] Not in virtual env!\n" +
         "Run the following, then re-run this script.\n" +
         "\tsource venv/bin/activate")
import sys
# App path up above scripts dir.
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/..')
import string
import getpass
from werkzeug.security import generate_password_hash
from app import db, main
from app.models import User
from app.utils import contains_bad_chars

def validate_password(username, password1, password2):
    # Make sure required form items are supplied.
    for form_item in (username, password1, password2):
        if form_item is None or form_item == "":
            return False, "Missing required form field(s)!"

        # Check input lengths.
        if len(form_item) > 150:
            return False, "Form field too long!"

    # Setup rudimentary password strength counter.
    lower_alpha_count = 0
    upper_alpha_count = 0
    number_count = 0
    special_char_count = 0

    # Adjust password strength values.
    for char in list(password1):
        if char in string.ascii_lowercase:
            lower_alpha_count += 1
        elif char in string.ascii_uppercase:
            upper_alpha_count += 1
        elif char in string.digits:
            number_count += 1
        else:
            special_char_count += 1

    # Verify password passes basic strength tests.
    if upper_alpha_count < 1 and number_count < 1 and special_char_count < 1:
        return False, "Password doesn't meet criteria! Must contain: an upper case character, a number, and a special character"

    # To try to nip xss & template injection in the bud.
    if contains_bad_chars(username):
        return False, "Username contains illegal character(s)"

    if password1 != password2:
        return False, "Passwords don't match!"

    if len(password1) < 12:
        return False, "Password is too short!"

    return True, ""

def change_password():
    """Change the password for a given user."""

    username = input("Enter username: ")
    password1 = getpass.getpass("Enter new password: ")
    password2 = getpass.getpass("Confirm new password: ")

    # Validate the new password
    is_valid, message = validate_password(username, password1, password2)

    if not is_valid:
        print(f"Error: {message}")
        return

    # Find the user in the database
    user = User.query.filter_by(username=username).first()

    if user is None:
        print("Error: User not found!")
        return

    # Update the user's password hash
    user.password = generate_password_hash(password1, method='pbkdf2:sha256')
    db.session.commit()

    print("Password updated successfully!")

if __name__ == '__main__':
    # Technically, needs to import flask app.
    app = main()
    with app.app_context():
        change_password()

