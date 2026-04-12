class GetHostStats:

    def __init__(self, system_metrics):
        self.system_metrics = system_metrics

    def execute(self):
        return self.system_metrics.get_host_stats()


