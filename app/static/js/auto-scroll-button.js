// Get the button element from the HTML.
const autoScrollButton = document.getElementById('auto-scroll-button');

// Get the outputTextArea element from the HTML.
const outputTextArea = document.getElementById('output-textarea');

// Initialize the auto-scrolling state to true.
let isAutoScrolling = true;

// Initialize the scrollInterval variable to null.
let scrollInterval = null;

// Function to kindly do the scrollful.
function doAnAutoScoll(isAutoScrolling){
  // If auto-scrolling is now enabled, start scrolling to the bottom.
  if (isAutoScrolling){
    // Use setInterval to scroll to the bottom every 100ms.
    scrollInterval = setInterval(function(){
      // Scroll to the bottom of the outputTextArea.
      outputTextArea.scrollTop = outputTextArea.scrollHeight;
    }, 100);
  }
  // Otherwise, stop auto-scrolling.
  else {
    clearInterval(scrollInterval);
  }
}

// Break auto scroll on mouse move.
// IE9, Chrome, Safari, Opera
outputTextArea.addEventListener("mousewheel", function(){
    isAutoScrolling = false;
    doAnAutoScoll(false);
  }, false);
// Firefox
outputTextArea.addEventListener("DOMMouseScroll", function(){
    isAutoScrolling = false;
    doAnAutoScoll(isAutoScrolling);
  }, false);

// Function to handle clicking the button.
autoScrollButton.onclick = function(){
  // Toggle the auto-scrolling state.
  isAutoScrolling = !isAutoScrolling;
  doAnAutoScoll(isAutoScrolling);
};

// Fox...
doAnAutoScoll(isAutoScrolling);
