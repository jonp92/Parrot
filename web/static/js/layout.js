/*
    * layout.js - This file contains the JavaScript code for the layout of the website.
    * Currently this includes functionality to determine screen size and make the table scrollable on smaller screens automatically.
    * 
    * Author: Jonathan L Pressler
    * Date: 2024-04-15
    * Version: 1.0
    * 
    * Changelog:
    * 1.0 - Initial version
    * 
*/

// Global variables
let mobile; 

/*
    * isMobile - This function checks if the user is on a mobile device.
    * Depending on the user agent or screen size, the function returns true if the user is on a mobile device, otherwise it returns false.
    * For the user agent, it checks if the user is on an Android, iPhone, iPod, or iPad device.
    * For the screen size, it checks if the screen width is less than 1024 pixels.
    * If either of these conditions are met, the function returns true, otherwise it returns false.
    * 
    * @returns {boolean} - Returns true if the user is on a mobile device, otherwise returns false.
*/
function isMobile() {
    let userAgent = navigator.userAgent;
    let screenX = window.innerWidth;
    let screenY = window.innerHeight;
    if (userAgent.match(/Android/i) || userAgent.match(/iPhone/i) || userAgent.match(/iPod/i) || userAgent.match(/iPad/i) || screenX < 1024 ) {
        return true;
    } else {
        return false;
    }
}

// Check if the user is on a mobile device and add the scrollable class to the table if they are to make the table condense on smaller screens and be scrollable.
window.onresize = function() {
    mobile = isMobile();
    console.log(mobile);
    if (mobile === true) {
        table.classList.add('scrollable');
        expansionButton.textContent = '▼';
    } else if (mobile === false) {
        table.classList.remove('scrollable');
        expansionButton.textContent = '▲';
    }
}
