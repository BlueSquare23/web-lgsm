// Function to update the status indicator based on server status.
function updateStatusIndicator(serverId, status) {

  let statusColor = '#00FF11'; // default green

  if (status === false) {
    statusColor = 'red';
  } else if (status === null) {
    // keep grey if unknown / SSH failure
    return;
  }

  // Find the indicator using data attribute (safe & scalable)
  const indicator = $(`.status-indicator[data-server-id="${serverId}"]`);

  if (!indicator.length) return;

  indicator.css({
    'color': statusColor,
    'text-shadow':
      `${statusColor} 0px 0px 5px, ` +
      `${statusColor} 0px 0px 10px, ` +
      `${statusColor} 0px 0px 20px, ` +
      `${statusColor} 0px 0px 30px`
  });
}


// Function to fetch all server statuses
function getServerStatus() {

  $('.status-indicator').each(function () {

    const serverId = $(this).data('server-id');

    if (!serverId) return;

    $.getJSON(`/api/server-status/${serverId}`, function (data) {
      updateStatusIndicator(serverId, data.status);
    });

  });
}


// Initial load
getServerStatus();

// Refresh every 5 minutes
setInterval(getServerStatus, 300000);
