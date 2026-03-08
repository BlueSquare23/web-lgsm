
class ProcInfoRepository:

    def add(self, server_id, proc_info):
        raise NotImplementedError

    def list(self):
        raise NotImplementedError

    def get(self, server_id, create=False):
        raise NotImplementedError

    def remove(self, server_id):
        raise NotImplementedError

