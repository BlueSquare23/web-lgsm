def get_client_ip(request):
    """
    Get's client IP from request object.
    """
    if request.headers.get("X-Forwarded-For"):
        return request.headers["X-Forwarded-For"].split(",")[0].strip()

    if request.headers.get("X-Real-IP"):
        return request.headers["X-Real-IP"]

    return request.remote_addr
