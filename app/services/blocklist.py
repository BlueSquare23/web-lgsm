class Blocklist:
    """
    Singleton class for blocklist service. Keeps track of in mem list of
    blocked IPs for basic login page protection. Appends IPs to fail list when
    they fail login attempts. If failed > max_fail add to blocklist.
    """
    max_fail = 2
    allowlist = ['127.0.0.1', '::1']
    blocklist = []
    failed = []

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Blocklist, cls).__new__(cls)
        return cls.instance

    def is_blocked(self, ip):
        if ip in Blocklist.blocklist:
            return True
    
        return False

    def add_failed(self, ip):
        """
        Add's IPs to failed list and if failed > max_fail times, adds to blocklist.
        """
        # Trim lists.
        if len(Blocklist.failed) >= 10000:
            Blocklist.failed.popleft()
    
        if len(Blocklist.blocklist) >= 10000:
            Blocklist.blocklist.popleft()
    
        if ip in Blocklist.allowlist:
            return
    
        Blocklist.failed.append(ip)
    
        if Blocklist.failed.count(ip) > Blocklist.max_fail:
            Blocklist.blocklist.append(ip)

    def get_client_ip(self, request):
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

