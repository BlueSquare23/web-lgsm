// Function to update the status indicator based on server status.
function updateStatusIndicator(serverId, status) {
  // Default to green, set to red if explicitly false.
  let statusColor = 'green';
  if (status === false) {
     statusColor = 'red';
  } else if (status === null) { 
    // If explicitly null, stay grey. Aka problem with ssh conn.
    return;
  } 

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

// Refresh every 300000 milliseconds (aka 5 minutes).
setInterval(getServerStatus, 300000);

