from flask import current_app, flash

def validation_errors(form):
    """
    Flashes messages for validation errors if there are any.

    Args:
        form (FlaskForm): Flask form object to check.

    Returns:
        dict: Returns dictionary of errors and fields.
    """
    form_name = type(form).__name__
    current_app.logger.info(f"{form_name} submission invalid!")
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                current_app.logger.debug(f"{field}: {error}")
                flash(f"{field}: {error}", "error")

