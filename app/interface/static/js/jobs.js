document.addEventListener('DOMContentLoaded', function() {
  // Update cron schedule when any field changes
  const cronInputs = ['minutes', 'hours', 'dayOfMonth', 'month', 'dayOfWeek'];
  cronInputs.forEach(id => {
    document.getElementById(id).addEventListener('change', updateCronExpression);
  });
  updateCronExpression();

  // Event handler for showing custom-cmd field.
  document.getElementById('command').addEventListener('change', function() {
    const customCmdDiv = document.getElementById('custom-cmd');
    if (this.value === 'custom' || this.value === 'send') {
      customCmdDiv.style.display = 'block';
    } else {
      customCmdDiv.style.display = 'none';
    }
  });

  // Edit button handlers
  document.querySelectorAll('.edit-cron').forEach(btn => {
    btn.addEventListener('click', function() {
      const server_id = this.getAttribute('data-uuid');
      const job_id = this.getAttribute('data-uid');
      // Fetch job data and populate form
      fetch(`/api/cron/${server_id}/${job_id}`)
        .then(response => response.json())
        .then(job => {
          document.getElementById('server_id').value = job.server_id;
          document.getElementById('job_id').value = job.job_id;
          document.getElementById('comment').value = job.comment;
          document.getElementById('command').value = job.command.split(" ")[1];
          document.getElementById('custom').value = job.custom;
          
          // Parse cron schedule 
          const parts = job.schedule.split(' ');
          document.getElementById('minutes').value = parts[0];
          document.getElementById('hours').value = parts[1];
          document.getElementById('dayOfMonth').value = parts[2];
          document.getElementById('month').value = parts[3];
          document.getElementById('dayOfWeek').value = parts[4];
          
          updateCronExpression();
          
          // Show modal
          const modal = new bootstrap.Modal(document.getElementById('addCronModal'));
          modal.show();
      });
    });
  });

  // Save button handler
  document.getElementById('saveCron').addEventListener('click', function() {
    const cronModal = document.getElementById('addCronModal');
    const bootstrapModal = bootstrap.Modal.getInstance(cronModal);
    if (bootstrapModal) {
      bootstrapModal.hide();
    }
    showSpinners();
    window.scrollTo(0,0); 
  });

  // Delete button handler
  document.querySelectorAll('.delete-cron').forEach(btn => {
    btn.addEventListener('click', handleDeleteCron);
  });
});

function handleDeleteCron() {
  const serverId = this.getAttribute('data-uuid');
  const jobId = this.getAttribute('data-uid');
  
  if (confirm('Are you sure you want to delete this cron job?')) {
    showSpinners();
    window.scrollTo(0,0); 

    fetch(`/api/cron/${serverId}/${jobId}`, {
      method: 'DELETE'
    })
    .then(response => {
      if (response.status === 204) {
        this.closest('.job-item').remove();
        
        showAlert('Cron job deleted successfully', 'success');
        hideSpinners();
      } 
      else if (response.status === 500) {
        throw new Error('Server error while deleting cron job');
      }
      else {
        throw new Error(`Unexpected response status: ${response.status}`);
      }
    })
    .catch(error => {
      console.error('Error deleting cron job:', error);
      showAlert('Failed to delete cron job', 'danger');
      hideSpinners();
    });
  }
}

function updateCronExpression() {
  const minutes = document.getElementById('minutes').value;
  const hours = document.getElementById('hours').value;
  const dayOfMonth = document.getElementById('dayOfMonth').value;
  const month = document.getElementById('month').value;
  const dayOfWeek = document.getElementById('dayOfWeek').value;
  
  const cronExpression = `${minutes} ${hours} ${dayOfMonth} ${month} ${dayOfWeek}`;
  document.getElementById('cronExpression').value = cronExpression;
  
  // Update human-readable description
  document.getElementById('cronDescription').textContent = describeCron(cronExpression);
  
  // Also update all human-readable descriptions in the list
  document.querySelectorAll('.cron-human-readable').forEach(el => {
    el.textContent = describeCron(el.getAttribute('data-cron'));
  });
}

function describeCron(cronExpression) {
  const parts = cronExpression.split(' ');
  if (parts.length !== 5) return 'Invalid cron schedule';

  const [min, hour, dom, month, dow] = parts;

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const days = [
    'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'
  ];

  function formatTime(hour, min) {
    if (hour === '*' && min === '*') return 'every minute';

    if (hour === '*') return `at minute ${min} past every hour`;

    if (min === '*') return `every minute past ${formatHour(hour)}`;

    return `at ${formatHour(hour, min)}`;
  }

  function formatHour(h, m = '00') {
    let hourNum = parseInt(h, 10);
    const minuteNum = parseInt(m, 10);

    const ampm = hourNum >= 12 ? 'PM' : 'AM';
    hourNum = hourNum % 12 || 12;

    const minuteStr = minuteNum.toString().padStart(2, '0');
    return `${hourNum}:${minuteStr} ${ampm}`;
  }

  function formatDayOfWeek(dow) {
    if (dow === '*') return '';

    if (dow.includes(',')) {
      const names = dow.split(',').map(d => days[parseInt(d)]);
      return `on ${names.join(', ')}`;
    }

    return `on ${days[parseInt(dow)]}s`;
  }

  function formatDayOfMonth(dom) {
    if (dom === '*') return '';
    return `on the ${ordinal(dom)} day of the month`;
  }

  function formatMonth(month) {
    if (month === '*') return '';
    return `in ${months[parseInt(month) - 1]}`;
  }

  function ordinal(n) {
    const num = parseInt(n, 10);
    const suffix = ['th', 'st', 'nd', 'rd'];
    const v = num % 100;
    return num + (suffix[(v - 20) % 10] || suffix[v] || suffix[0]);
  }

  const timePart = formatTime(hour, min);
  const monthPart = formatMonth(month);
  const domPart = formatDayOfMonth(dom);
  const dowPart = formatDayOfWeek(dow);

  const partsList = [timePart, dowPart, domPart, monthPart].filter(Boolean);

  return partsList.length
    ? partsList.join(' ')
    : 'Runs every minute';
}
