$(document).ready(function() {
    // Define global variables to store the data
    let networkBytesSentRate = 0;
    let networkBytesRecvRate = 0;
    let cpuUsage = 0;
    let memPercentUsed = 0;
    let load1 = 0;
    let load5 = 0;
    let load15 = 0;

    function createLineChart(ctx, label, color, dataKey) {
        return new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [
                    {
                        label: label,
                        borderColor: color,
                        borderWidth: 1,
                        fill: false,
                        data: []
                    }
                ]
            },
            options: {
                scales: {
                    x: {
                        type: 'realtime',
                        realtime: {
                            delay: 2000,
                            onRefresh: function(chart) {
                                const now = Date.now();
                                chart.data.datasets[0].data.push({
                                    x: now,
                                    y: typeof dataKey === 'function' ? dataKey() : dataKey
                                });
                                chart.update('quiet');
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: label
                        }
                    }
                }
            }
        });
    }

    function createPieChart(ctx) {
        return new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Used (GB)', 'Free (GB)'],
                datasets: [{
                    data: [0, 0],
                    backgroundColor: [usedColor, freeColor],
                }]
            },
            options: {
                responsive: true,
            }
        });
    }

    const networkCtx = document.getElementById('networkChart').getContext('2d');
    const networkChart = new Chart(networkCtx, {
        type: 'line',
        data: {
            datasets: [
                {
                    label: 'Bytes Sent per Second',
                    borderColor: usedColor,
                    borderWidth: 1,
                    fill: false,
                    data: []
                },
                {
                    label: 'Bytes Received per Second',
                    borderColor: freeColor,
                    borderWidth: 1,
                    fill: false,
                    data: []
                }
            ]
        },
        options: {
            scales: {
                x: {
                    type: 'realtime',
                    realtime: {
                        delay: 2000,
                        onRefresh: function(chart) {
                            const now = Date.now();
                            chart.data.datasets[0].data.push({
                                x: now,
                                y: networkBytesSentRate
                            });
                            chart.data.datasets[1].data.push({
                                x: now,
                                y: networkBytesRecvRate
                            });
                            chart.update('quiet');
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Bytes per Second'
                    }
                }
            }
        }
    });

    const cpuCtx = document.getElementById('cpuChart').getContext('2d');
    const cpuChart = createLineChart(cpuCtx, 'CPU Usage (%)', usedColor, () => cpuUsage);

    const memCtx = document.getElementById('memChart').getContext('2d');
    const memChart = createLineChart(memCtx, 'Memory Usage (%)', freeColor, () => memPercentUsed);

    const loadCtx = document.getElementById('loadChart').getContext('2d');
    const loadChart = new Chart(loadCtx, {
        type: 'line',
        data: {
            datasets: [
                {
                    label: '1 Minute Load Average',
                    borderColor: userColor,
                    borderWidth: 1,
                    fill: false,
                    data: []
                },
                {
                    label: '5 Minutes Load Average',
                    borderColor: usedColor,
                    borderWidth: 1,
                    fill: false,
                    data: []
                },
                {
                    label: '15 Minutes Load Average',
                    borderColor: freeColor,
                    borderWidth: 1,
                    fill: false,
                    data: []
                }
            ]
        },
        options: {
            scales: {
                x: {
                    type: 'realtime',
                    realtime: {
                        delay: 2000,
                        onRefresh: function(chart) {
                            const now = Date.now();
                            chart.data.datasets[0].data.push({
                                x: now,
                                y: load1
                            });
                            chart.data.datasets[1].data.push({
                                x: now,
                                y: load5
                            });
                            chart.data.datasets[2].data.push({
                                x: now,
                                y: load15
                            });
                            chart.update('quiet');
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Load Averages'
                    }
                }
            }
        }
    });

    const diskCtx = document.getElementById('diskChart').getContext('2d');
    const diskChart = createPieChart(diskCtx);

    function updateCharts(data) {
        const now = Date.now();

        networkBytesSentRate = data.network.bytes_sent_rate;
        networkBytesRecvRate = data.network.bytes_recv_rate;
        cpuUsage = data.cpu.cpu_usage;
        memPercentUsed = data.mem.percent_used;
        load1 = data.cpu.load1;
        load5 = data.cpu.load5;
        load15 = data.cpu.load15;

        diskChart.data.datasets[0].data[0] = bytesToGB(data.disk.used);
        diskChart.data.datasets[0].data[1] = bytesToGB(data.disk.free);
        diskChart.update();
    }

    function fetchData() {
        $.ajax({
            url: '/api/system-usage',
            method: 'GET',
            success: function(data) {
                updateCharts(data);
            }
        });
    }

    fetchData();
    setInterval(fetchData, 1000);

    function bytesToGB(bytes) {
        return (bytes / (1024 ** 3)).toFixed(2);
    }
});

