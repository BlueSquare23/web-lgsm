from collections import deque

from app.domain.repositories.blocklist_repo import BlocklistRepository

class InMemBlocklistRepository(BlocklistRepository):
    """
    Singleton class for blocklist service. Keeps track of in mem double ended
    queue of blocked IPs for basic login page protection. Appends IPs to fail list
    when they fail login attempts. If failed > max_fail add to blocklist.
    """
    max_fail = 2
    allowlist = ['127.0.0.1', '::1']
    blocklist = deque()
    failed = deque()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(InMemBlocklistRepository, cls).__new__(cls)
        return cls.instance

    def add(self, ip):
        """
        Add's IPs to failed list and if failed > max_fail times, adds to blocklist.
        """
        # Trim lists.
        if len(InMemBlocklistRepository.failed) >= 10000:
            InMemBlocklistRepository.failed.popleft()
    
        if len(InMemBlocklistRepository.blocklist) >= 10000:
            InMemBlocklistRepository.blocklist.popleft()
    
        if ip in InMemBlocklistRepository.allowlist:
            return
    
        InMemBlocklistRepository.failed.append(ip)
    
        if InMemBlocklistRepository.failed.count(ip) > InMemBlocklistRepository.max_fail:
            InMemBlocklistRepository.blocklist.append(ip)

    def check(self, ip):
        if ip in InMemBlocklistRepository.blocklist:
            return True
    
        return False

