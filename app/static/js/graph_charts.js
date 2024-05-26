$(document).ready(function() {
    function createLineChart(ctx, label, color) {
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
                                $.ajax({
                                    url: '/api/system-usage',
                                    method: 'GET',
                                    success: function(data) {
                                        const now = Date.now();
                                        if (chart.canvas.id === 'networkChart') {
                                            chart.data.datasets[0].data.push({
                                                x: now,
                                                y: data.network.bytes_sent_rate
                                            });
                                            chart.data.datasets[1].data.push({
                                                x: now,
                                                y: data.network.bytes_recv_rate
                                            });
                                        } else if (chart.canvas.id === 'cpuChart') {
                                            chart.data.datasets[0].data.push({
                                                x: now,
                                                y: data.cpu.cpu_usage
                                            });
                                        } else if (chart.canvas.id === 'memChart') {
                                            chart.data.datasets[0].data.push({
                                                x: now,
                                                y: data.mem.percent_used
                                            });
                                        } else if (chart.canvas.id === 'loadChart') {
                                            chart.data.datasets[0].data.push({
                                                x: now,
                                                y: data.cpu.load1
                                            });
                                            chart.data.datasets[1].data.push({
                                                x: now,
                                                y: data.cpu.load5
                                            });
                                            chart.data.datasets[2].data.push({
                                                x: now,
                                                y: data.cpu.load15
                                            });
                                        }
                                        chart.update('quiet');
                                    }
                                });
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
                            $.ajax({
                                url: '/api/system-usage',
                                method: 'GET',
                                success: function(data) {
                                    const now = Date.now();
                                    chart.data.datasets[0].data.push({
                                        x: now,
                                        y: data.network.bytes_sent_rate
                                    });
                                    chart.data.datasets[1].data.push({
                                        x: now,
                                        y: data.network.bytes_recv_rate
                                    });
                                    chart.update('quiet');
                                }
                            });
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
    createLineChart(cpuCtx, 'CPU Usage (%)', usedColor);

    const memCtx = document.getElementById('memChart').getContext('2d');
    createLineChart(memCtx, 'Memory Usage (%)', freeColor);

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
                            $.ajax({
                                url: '/api/system-usage',
                                method: 'GET',
                                success: function(data) {
                                    const now = Date.now();
                                    chart.data.datasets[0].data.push({
                                        x: now,
                                        y: data.cpu.load1
                                    });
                                    chart.data.datasets[1].data.push({
                                        x: now,
                                        y: data.cpu.load5
                                    });
                                    chart.data.datasets[2].data.push({
                                        x: now,
                                        y: data.cpu.load15
                                    });
                                    chart.update('quiet');
                                }
                            });
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
    const bytesToGB = bytes => (bytes / (1024 ** 3)).toFixed(2);

    setInterval(function() {
        $.ajax({
            url: '/api/system-usage',
            method: 'GET',
            success: function(data) {
                diskChart.data.datasets[0].data[0] = bytesToGB(data.disk.used);
                diskChart.data.datasets[0].data[1] = bytesToGB(data.disk.free);
                diskChart.update();
            }
        });
    }, 5000);
});
