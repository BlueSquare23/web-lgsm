// Function to update the status indicator based on server status.
function updateStatusIndicator(serverId, status) {
  // Green if the server is on, red if off.
  const statusColor = status ? 'green' : 'red';
  const indicator = $(`#${serverId}`);

  // Set the style of the status indicator.
  indicator.css({
    'color': statusColor,
    'text-shadow': `${statusColor} 0px 0px 5px, ` +
                   `${statusColor} 0px 0px 10px, ` +
                   `${statusColor} 0px 0px 20px, ` +
                   `${statusColor} 0px 0px 30px`
  });
}

// Function to get the server status via the API and update the indicator.
function getServerStatus() {
  $('.status-indicator').each(function() {
    // Get the server id from the span element.
    const serverId = $(this).attr('id');

    // Make an API request to get the server status.
    $.getJSON(`/api/server-status?id=${serverId}`, function(data) {
      // Update the indicator based on the status.
      updateStatusIndicator(serverId, data.status);
    });
  });
}

// Initial call to update the indicators when the page loads.
getServerStatus();

// Set an interval to refresh the status every 60 seconds (60000 milliseconds).
setInterval(getServerStatus, 60000);

