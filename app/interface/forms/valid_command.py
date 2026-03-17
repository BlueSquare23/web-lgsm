# TODO/NOTE: This can stay for now, but its on the chopping block. This
# validation should now be handled by flask-wtf/wtforms classes. Once I get
# this fixed up in the controls route, this can go.
def valid_command(ctrl, server, current_user):
    """
    Validates short commands from controls route form for game server. Some
    game servers may have specific game server command exemptions. This
    function basically just checks if supplied cmd is in list of accepted cmds
    from get_controls().

    Args:
        ctrl (str): Short ctrl string to validate.
        server (GameServer): Game server to check command against.
        current_user (LocalProxy): Currently logged in flask user object.

    Returns:
        bool: True if cmd is valid for user & game server, False otherwise.
    """

    from app.container import container
    controls = container.list_controls().execute(server, current_user)
    for control in controls:
        # Aka is valid control.
        if ctrl == control.short_ctrl:
            return True

    return False

