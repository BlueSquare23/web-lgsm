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
// Drop-in replacement for describeCron() in jobs.js.
// Supports: *, N, N,M, N-M, */S, N-M/S, N/S
// Examples:
//   */5 * * * *      -> Every 5 minutes
//   0 */12 * * *     -> Every 12 hours
//   0 0 * * 0        -> Every Sunday at midnight
//   30 18 * * 1-5    -> Every weekday at 6:30 PM
//   0 0 1 * *        -> At midnight on the 1st of every month
function describeCron(cronExpression) {
  const parts = String(cronExpression).trim().split(/\s+/);
  if (parts.length !== 5) return 'Invalid cron schedule';
  if (parts.some(p => /\/0+$/.test(p))) return 'Invalid cron schedule';

  const [min, hour, dom, month, dow] = parts;

  const MONTHS = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  const DAYS = [
    'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'
  ];

  // --- field shape checks ---
  const isAny     = f => f === '*';
  const isStep    = f => /^(\*|\d+-\d+|\d+)\/\d+$/.test(f);
  const isRange   = f => /^\d+-\d+$/.test(f);
  const isNumList = f => /^\d+(,\d+)*$/.test(f);

  // --- small helpers ---
  function ordinal(n) {
    const num = parseInt(n, 10);
    const suffix = ['th', 'st', 'nd', 'rd'];
    const v = num % 100;
    return num + (suffix[(v - 20) % 10] || suffix[v] || suffix[0]);
  }

  function joinList(items) {
    if (items.length <= 1) return items.join('');
    return items.slice(0, -1).join(', ') + ' and ' + items[items.length - 1];
  }

  const capitalize = s => s.charAt(0).toUpperCase() + s.slice(1);
  const monthName  = n => MONTHS[parseInt(n, 10) - 1] || n;
  const dayName    = n => DAYS[parseInt(n, 10) % 7] || n; // 7 == Sunday too

  // "0:00" -> midnight, "12:00" -> noon, otherwise 12-hour clock
  function timeLabel(h, m = 0) {
    let hourNum = parseInt(h, 10);
    const minuteNum = parseInt(m, 10);
    if (minuteNum === 0 && hourNum === 0) return 'midnight';
    if (minuteNum === 0 && hourNum === 12) return 'noon';
    const ampm = hourNum >= 12 ? 'PM' : 'AM';
    hourNum = hourNum % 12 || 12;
    return `${hourNum}:${minuteNum.toString().padStart(2, '0')} ${ampm}`;
  }

  // "*/5" -> "every 5 minutes", "10-30/5" -> "every 5 minutes from minute 10 through minute 30"
  function stepPhrase(field, noun, label, startPrep) {
    const [base, stepStr] = field.split('/');
    const step = parseInt(stepStr, 10);
    let text = step === 1 ? `every ${noun}` : `every ${step} ${noun}s`;

    if (isRange(base)) {
      const [a, b] = base.split('-');
      text += ` from ${label(a)} through ${label(b)}`;
    } else if (!isAny(base)) {
      text += ` ${startPrep} ${label(base)}`;
    }
    return text;
  }

  // "at 5 and 35 minutes past the hour" / "on the hour"
  function minutesPast(list) {
    const nums = list.map(n => parseInt(n, 10));
    if (nums.length === 1 && nums[0] === 0) return 'on the hour';
    const unit = nums.length === 1 && nums[0] === 1 ? 'minute' : 'minutes';
    return `at ${joinList(nums)} ${unit} past the hour`;
  }

  // --- time (minute + hour) ---
  const minList   = isNumList(min) ? min.split(',') : null;
  const minSingle = minList && minList.length === 1 ? parseInt(minList[0], 10) : null;

  // Phrase for the minute field when it's any / step / range
  function minuteFreq() {
    if (isAny(min)) return 'every minute';
    if (isStep(min)) return stepPhrase(min, 'minute', m => `minute ${m}`, 'starting at');
    if (isRange(min)) {
      const [a, b] = min.split('-');
      return `every minute from minute ${a} through minute ${b}`;
    }
    return `at minute ${min}`;
  }

  // Recurring schedules ("every 15 minutes between ...")
  function recurringTime() {
    if (isAny(hour)) {
      if (isAny(min)) return 'every minute';
      if (minList) return `every hour, ${minutesPast(minList)}`;
      if (isRange(min)) return `${minuteFreq()} of every hour`;
      return minuteFreq();
    }

    if (isStep(hour)) {
      const hourStep = stepPhrase(hour, 'hour', h => timeLabel(h, 0), 'starting at');
      if (min === '0') return hourStep;
      if (minList) return `${hourStep}, ${minutesPast(minList)}`;
      return `${minuteFreq()}, ${hourStep}`;
    }

    if (isRange(hour)) {
      const [a, b] = hour.split('-');
      if (min === '0') {
        return `every hour between ${timeLabel(a, 0)} and ${timeLabel(b, 0)}`;
      }
      if (minSingle !== null) {
        return `every hour between ${timeLabel(a, minSingle)} and ${timeLabel(b, minSingle)}`;
      }
      if (minList) {
        return `every hour between ${timeLabel(a, 0)} and ${timeLabel(b, 59)}, ${minutesPast(minList)}`;
      }
      return `${minuteFreq()} between ${timeLabel(a, 0)} and ${timeLabel(b, 59)}`;
    }

    if (isNumList(hour)) {
      const hrs = hour.split(',').map(h => timeLabel(h, 0));
      return `${minuteFreq()} during the ${joinList(hrs)} hour${hrs.length > 1 ? 's' : ''}`;
    }

    return `${minuteFreq()}, at hour ${hour}`;
  }

  // Exact times ("midnight", "6:30 PM and 9:00 PM")
  function exactTimes() {
    const times = [];
    hour.split(',').forEach(h => {
      min.split(',').forEach(m => times.push(timeLabel(h, m)));
    });
    return joinList(times);
  }

  // --- day of week ---
  // Returns { lead, on }: lead reads as "every Monday", on reads as "on Mondays"
  function describeDow() {
    if (isAny(dow)) return null;

    if (isNumList(dow)) {
      const days = [...new Set(dow.split(',').map(d => parseInt(d, 10) % 7))].sort((a, b) => a - b);
      const key = days.join(',');
      if (key === '1,2,3,4,5') return { lead: 'every weekday', on: 'on weekdays' };
      if (key === '0,6')       return { lead: 'every weekend', on: 'on weekends' };
      const names = days.map(d => DAYS[d]);
      return {
        lead: `every ${joinList(names)}`,
        on: `on ${joinList(names.map(n => n + 's'))}`
      };
    }

    if (isRange(dow)) {
      const [a, b] = dow.split('-');
      if (a === '1' && b === '5') return { lead: 'every weekday', on: 'on weekdays' };
      return {
        lead: `${dayName(a)} through ${dayName(b)}`,
        on: `from ${dayName(a)} through ${dayName(b)}`
      };
    }

    if (isStep(dow)) {
      return { lead: null, on: 'on ' + stepPhrase(dow, 'day of the week', dayName, 'starting on') };
    }

    return { lead: null, on: `on day-of-week ${dow}` };
  }

  // --- day of month (and the month, when it reads better together) ---
  function describeDom() {
    if (isAny(dom)) return '';
    if (isStep(dom)) return stepPhrase(dom, 'day', d => `the ${ordinal(d)}`, 'starting on');

    let base;
    let ords = null;
    if (isNumList(dom)) {
      ords = dom.split(',').map(ordinal);
      base = `on the ${joinList(ords)}`;
    } else if (isRange(dom)) {
      const [a, b] = dom.split('-');
      base = `from the ${ordinal(a)} through the ${ordinal(b)}`;
    } else {
      return `on day ${dom}`;
    }

    if (isAny(month)) return `${base} of every month`;
    if (isStep(month)) return base; // month clause adds "every 3 months"
    if (isNumList(month)) {
      const months = month.split(',');
      if (months.length === 1 && ords) return `on ${monthName(months[0])} ${joinList(ords)}`;
      return `${base} of ${joinList(months.map(monthName))}`;
    }
    if (isRange(month)) {
      const [a, b] = month.split('-');
      return `${base} of every month from ${monthName(a)} through ${monthName(b)}`;
    }
    return base;
  }

  // --- month (only when the day-of-month phrase didn't already cover it) ---
  function describeMonth() {
    if (isAny(month)) return '';
    const domCoversMonth = (isNumList(dom) || isRange(dom)) && !isStep(month);
    if (domCoversMonth) return '';

    if (isStep(month)) return stepPhrase(month, 'month', monthName, 'starting in');
    if (isRange(month)) {
      const [a, b] = month.split('-');
      return `from ${monthName(a)} through ${monthName(b)}`;
    }
    if (isNumList(month)) return `in ${joinList(month.split(',').map(monthName))}`;
    return `in month ${month}`;
  }

  // --- put it all together ---
  const dowInfo = describeDow();
  const hasDom  = !isAny(dom);
  const domText = describeDom();
  const monthText = describeMonth();
  const exact = isNumList(min) && isNumList(hour);

  // dow clause when it trails the sentence ("..., on weekdays" / "... and on Mondays")
  const dowTrail = dowInfo ? (hasDom ? `and ${dowInfo.on}` : dowInfo.on) : '';

  let sentence;

  if (exact) {
    const times = exactTimes();

    if (dowInfo && dowInfo.lead && !hasDom) {
      // "Every weekday at 6:30 PM"
      sentence = [`${capitalize(dowInfo.lead)} at ${times}`, monthText].filter(Boolean).join(' ');
    } else if (!dowInfo && !hasDom) {
      // "Every day at midnight"
      sentence = [`Every day at ${times}`, monthText].filter(Boolean).join(' ');
    } else {
      // "At midnight on the 1st of every month"
      sentence = [`At ${times}`, domText, dowTrail, monthText].filter(Boolean).join(' ');
    }
  } else {
    // "Every 15 minutes between 9:00 AM and 5:59 PM, on weekdays"
    sentence = [recurringTime(), domText, dowTrail, monthText].filter(Boolean).join(', ');
  }

  return capitalize(sentence);
}
