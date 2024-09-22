// Track the last line processed.
let lastProcessedIndex = 0;

function updateTerminal(sName){
  return $.ajax({
    dataType: 'json',
    url: '/api/cmd-output',
    type: 'GET',
    data: {
      'server': sName
    },
    error: function(reqObj, textStatus, errorThrown) {
      // For debug.
      //console.log(textStatus + '\n' + errorThrown);
      // Send errors to the console.
      term.write(textStatus + '\n' + errorThrown);
    },
    success: function(respJSON, textStatus, reqObj) {
      var spinners = document.getElementById("spinners");
      var TerminalText = '';

      // Check for new lines.
      if (respJSON.stdout.length > lastProcessedIndex) {
        for (let i = lastProcessedIndex; i < respJSON.stdout.length; i++){
          let outputLine = respJSON.stdout[i];
          // Skip lines that are just a newline char.
          if (outputLine !== '\n'){
            TerminalText += outputLine + '\r';
          }
        }

        // Update the last processed index.
        lastProcessedIndex = respJSON.stdout.length;

        // Write the new content to the terminal.
        term.write(TerminalText);
      }

      if (respJSON.process_lock === true){
        spinners.style.display = "block";
      } else {
        spinners.style.display = "none";
        clearInterval(interval);
      }
    }
  });
}

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

/* If the variable is undefined or empty or null report no output */
if (typeof serverName === 'undefined' || serverName === null || !serverName){
  term.write('No Output Yet!\n\r');
} else {
  var interval = setInterval(function() {
    updateTerminal(serverName);
  }, 500);
}

