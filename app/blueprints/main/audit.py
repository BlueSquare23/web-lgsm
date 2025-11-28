from flask_login import login_required, current_user
from flask import render_template, request

from app.models import Audit
from app.processes_global import *

from . import main_bp

######### Audit Route #########

@main_bp.route("/audit", methods=["GET"])
@login_required
def audit():
    # NOTE: We don't care about CSRF protection for this page since its
    # readonly. 

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    user_id = request.args.get('user_id')
    search = request.args.get('search')

    query = Audit.query.order_by(Audit.date_created.desc())

    if user_id:
        query = query.filter(Audit.user_id == user_id)

    if search:
        query = query.filter(Audit.message.ilike(f'%{search}%'))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    all_audit_events = pagination.items

    # Get all users for the dropdown.
    all_users = User.query.order_by(User.username).all()

    return render_template(
        'audit.html', 
        user=current_user,
        pagination=pagination,
        all_audit_events=all_audit_events,
        all_users=all_users
    )


