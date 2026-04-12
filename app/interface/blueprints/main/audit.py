from flask_login import login_required, current_user
from flask import render_template, request

from app.container import container

from . import main_bp

# TODO: This page needs a proper Flask-Wtform and input validation!!!
 
########## Audit Route #########

@main_bp.route("/audit", methods=["GET"])
@login_required
def audit():

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    user_id = request.args.get('user_id')
    search = request.args.get('search')

    use_case = container.list_audit_logs()

    all_audit_events, pagination = use_case.execute(
        page=page,
        per_page=per_page,
        user_id=user_id,
        search=search,
    )

#    all_users = User.query.order_by(User.username).all()
    all_users = container.list_users().execute()

    return render_template(
        'audit.html',
        user=current_user,
        pagination=pagination,
        all_audit_events=all_audit_events,
        all_users=all_users
    )

