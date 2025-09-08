# List of blocked IPs for basic login page protection.

allowlist = ['127.0.0.1', '::1']
blocklist = []
failed = []

def is_blocked(ip):
    if ip in blocklist:
        return True

    return False


def add_failed(ip):
    """
    Add's IPs to failed list and if failed > 2 times, adds to blocklist.
    """
    # Trim lists.
    if len(failed) >= 10000:
        failed.popleft()

    if len(blocklist) >= 10000:
        blocklist.popleft()

    if ip in allowlist:
        return

    failed.append(ip)

    if failed.count(ip) > 2:
        blocklist.append(ip)


def get_client_ip(request):
    """  
    Get the real client IP address even when behind a reverse proxy
    """
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For can contain multiple IPs, the first one is the client.
        return request.headers['X-Forwarded-For'].split(',')[0].strip()

    if request.headers.get('X-Real-IP'):
        return request.headers['X-Real-IP']

    # Fallback to the direct connection IP.
    return request.remote_addr


