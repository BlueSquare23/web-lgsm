// jobs.js
document.addEventListener('DOMContentLoaded', function() {

  // ----------------------------
  // Cron Inputs Handling
  // ----------------------------
  const cronInputs = ['minutes', 'hours', 'dayOfMonth', 'month', 'dayOfWeek'];

  cronInputs.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('change', updateCronExpression);
    }
  });

  updateCronExpression();

  // ----------------------------
  // Command Selector
  // ----------------------------
  const commandSelect = document.getElementById('command');
  if (commandSelect) {
    commandSelect.addEventListener('change', toggleCustomCommand);
  }

  function toggleCustomCommand() {
    const customCmdDiv = document.getElementById('custom-cmd');
    if (!customCmdDiv) return;

    if (commandSelect.value === 'custom' || commandSelect.value === 'send') {
      customCmdDiv.style.display = 'block';
    } else {
      customCmdDiv.style.display = 'none';
    }
  }

  // ----------------------------
  // Edit Cron Job
  // ----------------------------
  document.querySelectorAll('.edit-cron').forEach(btn => {
    btn.addEventListener('click', function() {

      const server_id = this.getAttribute('data-uuid');
      const job_id = this.getAttribute('data-uid');

      fetch(`/api/cron/${server_id}/${job_id}`)
        .then(response => response.json())
        .then(job => {

          // Populate form safely
          setValue('server_id', job.server_id);
          setValue('job_id', job.job_id);
          setValue('comment', job.comment);

          const cmd = job.command.split(" ")[1];
          setValue('command', cmd);
          setValue('custom', job.custom);

          // Trigger command toggle manually
          toggleCustomCommand();

          // Parse cron schedule
          const parts = job.schedule.split(' ');
          setValue('minutes', parts[0]);
          setValue('hours', parts[1]);
          setValue('dayOfMonth', parts[2]);
          setValue('month', parts[3]);
          setValue('dayOfWeek', parts[4]);

          updateCronExpression();

          // Show modal
          const modalEl = document.getElementById('addCronModal');
          if (modalEl) {
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
          }
        });
    });
  });

  // ----------------------------
  // Save Button
  // ----------------------------
  const saveBtn = document.getElementById('saveCron');
  if (saveBtn) {
    saveBtn.addEventListener('click', function() {
      const modalEl = document.getElementById('addCronModal');
      const modal = bootstrap.Modal.getInstance(modalEl);

      if (modal) modal.hide();

      showSpinners();
      window.scrollTo(0, 0);
    });
  }

  // ----------------------------
  // Delete Cron Job
  // ----------------------------
  document.querySelectorAll('.delete-cron').forEach(btn => {
    btn.addEventListener('click', handleDeleteCron);
  });

});


// ----------------------------
// Helpers
// ----------------------------
function setValue(id, value) {
  const el = document.getElementById(id);
  if (el) el.value = value || '';
}


// ----------------------------
// Delete Handler (UPDATED)
// ----------------------------
function handleDeleteCron() {
  const serverId = this.getAttribute('data-uuid');
  const jobId = this.getAttribute('data-uid');

  if (!confirm('Are you sure you want to delete this cron job?')) return;

  showSpinners();
  window.scrollTo(0, 0);

  fetch(`/api/cron/${serverId}/${jobId}`, {
    method: 'DELETE'
  })
  .then(response => {
    if (response.status === 204) {

      // 🔥 FIX: remove card instead of .job-item
      const card = this.closest('.col-md-6, .col-lg-4, .card');
      if (card) {
        card.remove();
      }

      showAlert('Cron job deleted successfully', 'success');
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
  })
  .finally(() => {
    hideSpinners();
  });
}


// ----------------------------
// Cron Expression Builder
// ----------------------------
function updateCronExpression() {

  const minutes = getVal('minutes');
  const hours = getVal('hours');
  const dayOfMonth = getVal('dayOfMonth');
  const month = getVal('month');
  const dayOfWeek = getVal('dayOfWeek');

  const cronExpression = `${minutes} ${hours} ${dayOfMonth} ${month} ${dayOfWeek}`;

  const cronField = document.getElementById('cronExpression');
  if (cronField) cronField.value = cronExpression;

  const descEl = document.getElementById('cronDescription');
  if (descEl) descEl.textContent = describeCron(cronExpression);

  document.querySelectorAll('.cron-human-readable').forEach(el => {
    el.textContent = describeCron(el.getAttribute('data-cron'));
  });
}

function getVal(id) {
  const el = document.getElementById(id);
  return el ? el.value : '*';
}


// ----------------------------
// Human Readable Cron
// ----------------------------
function describeCron(cronExpression) {
  const parts = cronExpression.split(' ');
  if (parts.length !== 5) return 'Invalid cron schedule';

  const [min, hour, dom, month, dow] = parts;

  const months = [
    'January','February','March','April','May','June',
    'July','August','September','October','November','December'
  ];

  const days = [
    'Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'
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

    return `${hourNum}:${minuteNum.toString().padStart(2, '0')} ${ampm}`;
  }

  function formatDayOfWeek(dow) {
    if (dow === '*') return '';
    if (dow.includes(',')) {
      return `on ${dow.split(',').map(d => days[parseInt(d)]).join(', ')}`;
    }
    return `on ${days[parseInt(dow)]}s`;
  }

  function formatDayOfMonth(dom) {
    if (dom === '*') return '';
    return `on the ${ordinal(dom)} day`;
  }

  function formatMonth(month) {
    if (month === '*') return '';
    return `in ${months[parseInt(month) - 1]}`;
  }

  function ordinal(n) {
    const num = parseInt(n, 10);
    const suffix = ['th','st','nd','rd'];
    const v = num % 100;
    return num + (suffix[(v - 20) % 10] || suffix[v] || suffix[0]);
  }

  const partsList = [
    formatTime(hour, min),
    formatDayOfWeek(dow),
    formatDayOfMonth(dom),
    formatMonth(month)
  ].filter(Boolean);

  return partsList.length ? partsList.join(' ') : 'Runs every minute';
}
