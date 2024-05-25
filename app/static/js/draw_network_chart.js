$(document).ready(function() {
    const ctx = document.getElementById('networkChart').getContext('2d');
    const networkChart = new Chart(ctx, {
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
                                url: '/stats/network-usage',
                                method: 'GET',
                                success: function(data) {
                                    const now = Date.now();
                                    chart.data.datasets[0].data.push({
                                        x: now,
                                        y: data.bytes_sent_rate
                                    });
                                    chart.data.datasets[1].data.push({
                                        x: now,
                                        y: data.bytes_recv_rate
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
});

