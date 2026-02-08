import os
import time
import psutil
import shutil

class SystemMetrics:
    # Network stats class vars.
    prev_bytes_sent = psutil.net_io_counters().bytes_sent
    prev_bytes_recv = psutil.net_io_counters().bytes_recv
    prev_time = time.time()

    def __init__(self):
        pass

    def get_network_stats(self):
        """
        Gets bytes in/out per second. Stores last got values in globals. Used by
        get_host_stats() to collect network status for /api/system-usage route.
    
        Returns:
            dict: Dictionary containing bytes_sent_rate & bytes_recv_rate.
        """
        # Get current counters and timestamp.
        net_io = psutil.net_io_counters()
        current_bytes_sent = net_io.bytes_sent
        current_bytes_recv = net_io.bytes_recv
        current_time = time.time()
    
        # Calculate the rate of bytes sent and received per second.
        bytes_sent_rate = (current_bytes_sent - SystemMetrics.prev_bytes_sent) / (
            current_time - SystemMetrics.prev_time
        )
        bytes_recv_rate = (current_bytes_recv - SystemMetrics.prev_bytes_recv) / (
            current_time - SystemMetrics.prev_time
        )
    
        # Update previous counters and timestamp.
        SystemMetrics.prev_bytes_sent = current_bytes_sent
        SystemMetrics.prev_bytes_recv = current_bytes_recv
        SystemMetrics.prev_time = current_time
    
        return {"bytes_sent_rate": bytes_sent_rate, "bytes_recv_rate": bytes_recv_rate}
    
    
    def get_host_stats(self):
        """
        Returns disk, cpu, mem, and network stats which are later turned into json
        for the /api/system-usage route which is used by home page resource usage
        stats charts.
    
        Returns:
            dict: Dictionary containing disk, cpu, mem, and network usage
                  statistics.
        """
        stats = dict()
    
        # Disk
        total, used, free = shutil.disk_usage("/")
        # Add ~4% for ext4 filesystem metadata usage.
        percent_used = (((total * 0.04) + used) / total) * 100
        stats["disk"] = {
            "total": total,
            "used": used,
            "free": free,
            "percent_used": percent_used,
        }
    
        # CPU
        load1, load5, load15 = psutil.getloadavg()
        cpu_usage = (load1 / os.cpu_count()) * 100
        stats["cpu"] = {
            "load1": load1,
            "load5": load5,
            "load15": load15,
            "cpu_usage": cpu_usage,
        }
    
        # Mem
        mem = psutil.virtual_memory()
        # Total, used, available, percent_used.
        stats["mem"] = {
            "total": mem[0],
            "used": mem[3],
            "free": mem[1],
            "percent_used": mem[2],
        }
    
        # Network
        stats["network"] = self.get_network_stats()
    
        return stats

