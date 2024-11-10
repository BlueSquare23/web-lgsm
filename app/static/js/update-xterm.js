// Track the last line processed.
//let lastProcessedIndex = 0;
// Keep track of last pulled output as source of truth.
let previousOutput = [];

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

function refreshOutput(sName) {
  return $.ajax({
    url: '/api/update-console',
    type: 'POST',
    data: { 'server': serverName },
    error: function(reqObj, textStatus, errorThrown) {
      // Send errors to the console.
      term.write(textStatus + '\n' + errorThrown);
      clearInterval(interval);
    }
  });
}

function updateTerminal(sName){
  return $.ajax({
    dataType: 'json',
    url: '/api/cmd-output',
    type: 'GET',
    data: {
      'server': sName
    },
    error: function(reqObj, textStatus, errorThrown) {
      // Send errors to the console.
      term.write(textStatus + '\n' + errorThrown);
    },
    success: function(respJSON, textStatus, reqObj) {
      console.log("respJSON.stdout: ");
      console.log(respJSON.stdout);

      console.log("previousOutput: ");
      console.log(previousOutput);

      // Extract stdout array from the JSON response.
      const currentOutput = respJSON.stdout || [];
      console.log("currentOutput: ");
      console.log(currentOutput);

      // Find new lines by comparing with previousOutput.
      const newLines = currentOutput.slice(previousOutput.length);
      console.log("newLines: ");
      console.log(newLines);

      console.log('--------------------------------------------------------');

      if (newLines.length > 0) {
        newLines.forEach(line => {
          if (line.trim() !== '') {
            term.write(line + '\r');
          }
        });

        // Update the previously processed output to the current output.
        previousOutput = currentOutput;
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
if (typeof serverName === 'undefined' || serverName === null || !serverName) {
  term.write('No Output Yet!\n\r');
} else if (typeof sConsole !== 'undefined' && sConsole) {
  // If live console output mode is enabled, start the loop.
  spinners.style.display = "block";
  var interval = setInterval(function() {
    refreshOutput(serverName).then(function() {
      return updateTerminal(serverName);
    });
  }, 5000);
} else {
  var interval = setInterval(function() {
    console.log(sConsole);
    updateTerminal(serverName);
  }, 500);
}
