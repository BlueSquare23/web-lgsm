// Get the button element from the HTML.
const autoScrollButton = document.getElementById('auto-scroll-button');

// Initialize the auto-scrolling state to true.
let isAutoScrolling = true;

// Initialize the scrollInterval variable to null.
let scrollInterval = null;

// Function to kindly do the scroll.
function doAnAutoScoll(isAutoScrolling){
  // If auto-scrolling is now enabled, start scrolling to the bottom
  if (isAutoScrolling){
    // Use setInterval to scroll to the bottom every 100ms
    scrollInterval = setInterval(function(){
      // Scroll to the bottom
      window.scrollTo(0, 100000);
    }, 100);
  }
  // Otherwise, stop auto-scrolling.
  else {
    clearInterval(scrollInterval);
  }
}

// Function to handle clicking the button.
autoScrollButton.onclick = function(){
  // Toggle the auto-scrolling state
  isAutoScrolling = !isAutoScrolling;
  doAnAutoScoll(isAutoScrolling);
};

doAnAutoScoll(isAutoScrolling);

