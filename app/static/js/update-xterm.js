// Track the last line processed.
//let lastProcessedIndex = 0;
// Keep track of last pulled output as source of truth.
let previousStdOutput = [];
let previousStdErrput = [];

var spinners = document.getElementById("spinners");

var term = new Terminal({
  theme: {
    foreground: textColor,
    background: '#212529',
  },
  fontFamily: 'Fira Code, monospace',
  fontSize: 14,
  lineHeight: 1.2,
  cursorStyle: 'block',
  cursorBlink: false,
});

term.open(document.getElementById('terminal'));

var fitAddon = new FitAddon.FitAddon();
term.loadAddon(fitAddon);
fitAddon.fit();

term.write('\rWelcome to the web-lgsm!\n\r');

// Handle window resize.
window.addEventListener('resize', function() {
    fitAddon.fit();
});

function refreshOutput(sId) {
  return $.ajax({
    url: '/api/update-console',
    type: 'POST',
    data: { 'server_id': sId },
    error: function(reqObj, textStatus, errorThrown) {
      // Send errors to the console.
      term.write(textStatus + '\n' + errorThrown);
      clearInterval(interval);
    }
  });
}

function updateTerminal(sId){
  return $.ajax({
    dataType: 'json',
    url: '/api/cmd-output',
    type: 'GET',
    data: {
      'server_id': sId
    },
    error: function(reqObj, textStatus, errorThrown) {
      // Send errors to the console.
      term.write(textStatus + '\n' + errorThrown);
    },
    success: function(respJSON, textStatus, reqObj) {

      // Extract stdout array from the JSON response.
      const currentStdOutput = respJSON.stdout || [];

      // Find new lines by comparing with previousStdOutput.
      const newOutLines = currentStdOutput.slice(previousStdOutput.length);

      if (newOutLines.length > 0) {
        newOutLines.forEach(line => {
          if (line.trim() !== '') {
            term.write(`\r${line}`);
          }
        });

        // Update the previously processed output to the current output.
        previousStdOutput = currentStdOutput;
      }

      if ( showStderr ) {
        // Extract stderr array from the JSON response.
        const currentStdErrput = respJSON.stderr || [];

        // Find new lines by comparing with previousStdErrput.
        const newErrLines = currentStdErrput.slice(previousStdErrput.length);

        if (newErrLines.length > 0) {
          newErrLines.forEach(line => {
            if (line.trim() !== '') {
              // Print "STDERR" red bold, before stderr text.
              term.write(`\r\x1b[1m\x1b[31mSTDERR:\x1b[0m ${line}`);
            }
          });

          // Update the previously processed err output to the current output.
          previousStdErrput = currentStdErrput;
        }
      }

      // If not in console mode, display none spinners after proc finishes.
      if (!sConsole) {
        if (respJSON.process_lock === true){
          spinners.style.display = "block";
        } else {
          spinners.style.display = "none";
          clearInterval(interval);
        }
      }
    }
  });
}

// If the variable is undefined, empty, or null, report no output.
if (typeof serverId === 'undefined' || serverId === null || !serverId) {
  term.write('No Output Yet!\n\r');
} else if (typeof sConsole !== 'undefined' && sConsole) {
  // If live console output mode is enabled, start the loop.
  spinners.style.display = "block";
  var interval = setInterval(function() {
    refreshOutput(serverId).then(function() {
      return updateTerminal(serverId);
    });
  }, 5000);
} else {
  var interval = setInterval(function() {
    updateTerminal(serverId);
  }, 500);
}
