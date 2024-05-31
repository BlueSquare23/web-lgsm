/* Grabs latest output json from the /output api route and slaps it
 * into the textarea. */
function updateTextArea(){
  return $.ajax({
    dataType: 'json',
    url: '/api/cmd-output',  // URL of output json api.
    type: 'GET',
    data: {
      'server': serverName
    },
    error: function(reqObj, textStatus, errorThrown) {
      console.log(textStatus + '\n' + errorThrown);
      // Send error to textarea.
      $('#output-textarea').val(textStatus + '\n' + errorThrown);
    },
    success: function(respJSON, textStatus, reqObj) {
      var spinners = document.getElementById("spinners");
      var textAreaText = '';
      if (respJSON.output_lines.length === 0 ||
         (respJSON.output_lines.length === 1 && respJSON.output_lines[0] == "")){
        textAreaText = 'No Output Yet!';
      }

      for (let i = 0; i < respJSON.output_lines.length; i++){
        outputLine = respJSON.output_lines[i];
        // Skip lines that are just a newline char.
        if (outputLine !== '\n'){
          textAreaText += outputLine;
        }
      }

      // Update the value of the textarea element with the updated content.
      $('#output-textarea').val(textAreaText);

      if (respJSON.process_lock === true){
        spinners.style.display = "block";
      } else {
        spinners.style.display = "none";
        clearInterval(interval);
      }

    }
  });
}

console.log("Server Name: " + serverName);

/* If the variable is undefined or empty or null report no output */
if (typeof serverName === 'undefined' || serverName === null || !serverName){
  $('#output-textarea').val('No Output Yet!');
} else {
  var interval = setInterval(function() {
    updateTextArea();
  }, 1000);
}
