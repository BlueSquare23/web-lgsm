class BlocklistService:
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
            cls.instance = super(BlocklistService, cls).__new__(cls)
        return cls.instance

    def is_blocked(self, ip):
        if ip in BlocklistService.blocklist:
            return True
    
        return False

    def add_failed(self, ip):
        """
        Add's IPs to failed list and if failed > max_fail times, adds to blocklist.
        """
        # Trim lists.
        if len(BlocklistService.failed) >= 10000:
            BlocklistService.failed.popleft()
    
        if len(BlocklistService.blocklist) >= 10000:
            BlocklistService.blocklist.popleft()
    
        if ip in BlocklistService.allowlist:
            return
    
        BlocklistService.failed.append(ip)
    
        if BlocklistService.failed.count(ip) > BlocklistService.max_fail:
            BlocklistService.blocklist.append(ip)

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

