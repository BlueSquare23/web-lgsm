// Apply CodeMirror CSS to textarea.
var editor = CodeMirror.fromTextArea(document.getElementById('edit-text-area'), {
  lineNumbers: true,
  mode: 'text/x-perl',
  theme: 'cobalt',
});

// Set editor textarea height.
editor.setSize(null, 500);

