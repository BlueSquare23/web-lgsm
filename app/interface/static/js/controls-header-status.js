function updateHeaderStatus(status) {
  const badge = $('#server-status-badge');

  if (status === true) {
    badge
      .removeClass('bg-danger bg-secondary')
      .addClass('bg-success')
      .text('Status: Running');
  } else if (status === false) {
    badge
      .removeClass('bg-success bg-secondary')
      .addClass('bg-danger')
      .text('Status: Stopped');
  } else {
    // null or error state
    badge
      .removeClass('bg-success bg-danger')
      .addClass('bg-secondary')
      .text('Status: Unknown');
  }
}

function getServerStatusHeader() {
  $.getJSON(`/api/server-status/${serverId}`, function(data) {
    updateHeaderStatus(data.status);
  }).fail(function() {
    updateHeaderStatus(null);
  });
}

// Run on page load
getServerStatusHeader();

// Optional: refresh every 30s (faster than homepage since it's a detail view)
setInterval(getServerStatusHeader, 30000);

