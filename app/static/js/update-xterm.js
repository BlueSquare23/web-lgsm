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
      if (respJSON.output_lines.length > lastProcessedIndex) {
        for (let i = lastProcessedIndex; i < respJSON.output_lines.length; i++){
          let outputLine = respJSON.output_lines[i];
          // Skip lines that are just a newline char.
          if (outputLine !== '\n'){
            TerminalText += outputLine + '\r';
          }
        }

        // Update the last processed index.
        lastProcessedIndex = respJSON.output_lines.length;

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

//console.log("Server Name: " + serverName);

var term = new Terminal();
term.open(document.getElementById('terminal'));

var fitAddon = new FitAddon.FitAddon();

term.loadAddon(fitAddon);
term.open(document.getElementById('terminal'));
fitAddon.fit(); // Fit the terminal to the container

term.write('\r\x1B[32mWelcome to the web-lgsm!\x1B[0m\n\r');

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
  }, 1000);
}

