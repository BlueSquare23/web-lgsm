import os
import json

from app.services import SystemMetrics

class TestSystemMetrics:

    def test_get_network_stats(self):
        mon_service = SystemMetrics()
        stats = mon_service.get_network_stats()
    
        assert isinstance(stats, dict)
        assert "bytes_sent_rate" in stats
        assert "bytes_recv_rate" in stats
        assert isinstance(stats["bytes_sent_rate"], float)
        assert isinstance(stats["bytes_recv_rate"], float)
    
    
    def test_get_host_stats(self):
        mon_service = SystemMetrics()
        stats = mon_service.get_host_stats()
    
        assert isinstance(stats, dict)
        assert "disk" in stats
        assert "cpu" in stats
        assert "mem" in stats
        assert "network" in stats
    
        assert isinstance(stats["disk"], dict)
        assert isinstance(stats["cpu"], dict)
        assert isinstance(stats["mem"], dict)
        assert isinstance(stats["network"], dict)
    
        # Check types of values in 'disk' dictionary
        disk = stats["disk"]
        assert isinstance(disk["total"], int)
        assert isinstance(disk["used"], int)
        assert isinstance(disk["free"], int)
        assert isinstance(disk["percent_used"], float)
    
        # Check types of values in 'cpu' dictionary, excluding 'cpu_usage'
        cpu = stats["cpu"]
        assert isinstance(cpu["load1"], float)
        assert isinstance(cpu["load5"], float)
        assert isinstance(cpu["load15"], float)
    
        # Check type of 'cpu_usage'
        assert isinstance(cpu["cpu_usage"], float)
    
        # Check types of values in 'mem' dictionary
        mem = stats["mem"]
        assert isinstance(mem["total"], int)
        assert isinstance(mem["used"], int)
        assert isinstance(mem["free"], int)
        assert isinstance(mem["percent_used"], float)
    
        # Check types of values in 'network' dictionary
        network = stats["network"]
        assert isinstance(network["bytes_sent_rate"], float)
        assert isinstance(network["bytes_recv_rate"], float)
    
        # Ensure the result can be serialized to JSON
        json_string = json.dumps(stats)
        assert isinstance(json_string, str)
    
