document.addEventListener('DOMContentLoaded', () => {
    // Fetch the JSON data
    fetch('/stats')
        .then(response => response.json())
        .then(data => {
            // Convert bytes to GB
            const bytesToGB = bytes => (bytes / (1024 ** 3)).toFixed(2);

            // Prepare data for charts
            const diskData = {
                labels: ['Used (GB)', 'Free (GB)'],
                datasets: [{
                    label: 'Disk Usage',
                    data: [
                        bytesToGB(data.disk.used),
                        bytesToGB(data.disk.free)
                    ],
                    backgroundColor: [usedColor, freeColor]
                }]
            };

            const cpuData = {
                labels: ['Usage (%)', 'Idle (%)'],
                datasets: [{
                    label: 'CPU Usage',
                    data: [
                        data.cpu.cpu_usage,
                        100 - data.cpu.cpu_usage
                    ],
                    backgroundColor: [usedColor, freeColor]
                }]
            };

            const loadAvgs = {
                labels: ['1 Min', '5 Min', '15 Min'],
                datasets: [{
                    label: 'Load Averages',
                    data: [
                        data.cpu.load1,
                        data.cpu.load5,
                        data.cpu.load15,
                    ],
                    backgroundColor: [usedColor, freeColor, usedColor]
                }]
            };

            const memData = {
                labels: ['Used (GB)', 'Free (GB)'],
                datasets: [{
                    label: 'Memory Usage',
                    data: [
                        bytesToGB(data.mem.used),
                        bytesToGB(data.mem.free)
                    ],
                    backgroundColor: [usedColor, freeColor]
                }]
            };

/*
            const networkData = {
                labels: ['Bytes Sent', 'Bytes Received'],
                datasets: [{
                    label: 'Network Usage',
                    data: [
                        data.network.bytes_sent_per_sec,
                        data.network.bytes_recv_per_sec,
                    ],
                    backgroundColor: [usedColor, freeColor]
                }]
            };
*/

            // Create the charts
            const ctxDisk = document.getElementById('diskChart').getContext('2d');
            const ctxCpu = document.getElementById('cpuChart').getContext('2d');
            const ctxLoad = document.getElementById('loadChart').getContext('2d');
            const ctxMem = document.getElementById('memChart').getContext('2d');
            const ctxNetwork = document.getElementById('networkChart').getContext('2d');

            new Chart(ctxDisk, {
                type: 'pie',
                data: diskData,
                options: {
                    responsive: true,
                }
            });

            new Chart(ctxCpu, {
                type: 'pie',
                data: cpuData,
                options: {
                    responsive: true,
                }
            });

            new Chart(ctxLoad, {
                type: 'bar',
                data: loadAvgs,
                options: {
                    responsive: true,
                }
            });

            new Chart(ctxMem, {
                type: 'pie',
                data: memData,
                options: {
                    responsive: true,
                }
            });

/*
            new Chart(ctxNetwork, {
                type: 'bar',
                data: networkData,
                options: {
                    responsive: true,
                }
            });
*/
        })
        .catch(error => console.error('Error fetching data:', error));
});

