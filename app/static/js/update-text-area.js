/* Grabs latest output json from the /output api route and slaps it
 * into the textarea */
function updateTextArea(){
  return $.ajax({
    dataType: 'json',
    url: '/output',  // URL of output json api.
    error: function(reqObj, textStatus, errorThrown) {
      console.log(textStatus + '\n' + errorThrown);
      // Send error to textarea.
      $('#outputTextArea').val(textStatus + '\n' + errorThrown);
    },
    success: function(respJSON, textStatus, reqObj) {
      var spinners = document.getElementById("spinners");
      var textAreaText = '';
      if (respJSON.output_lines.length === 0){
        textAreaText = 'No Output Yet!';
      }

      for (let i = 0; i < respJSON.output_lines.length; i++){
        outputLine = respJSON.output_lines[i];
        if (outputLine  !== '\n'){
          textAreaText += outputLine;
        }
      }

      // Update the value of the textarea element with the updated content.
      $('#outputTextArea').val(textAreaText);
      
      if (respJSON.process_lock === true){
        spinners.style.display = "block";
      } else {
        spinners.style.display = "none";
        clearInterval(interval);
      }

    }
  });
}

var interval = setInterval(function() {
  updateTextArea();
}, 1000);
