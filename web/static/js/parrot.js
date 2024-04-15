/*
    * parrot.js - This file is responsible for connecting to multiple SSEs and updating the "radio display" with the latest activity and logging it to the table.
    *
    * Author: Jonathan L. Pressler
    * Date: 2024-04-04
    * Version: 1.5
    *
    * Changelog:
    * 1.0 - Initial version
    * 1.5 - Added a second EventSource object to watch for YSFGateway logs and display the reflector/room in the reflector element. Additionally, added a
    * clear log button to clear the log table and an expansion button to toggle the scrollable and sticky-header classes on the table.
    * 
*/

/* global variables */
const serverIP = document.getElementById("server_ip").value || "localhost"; // get the server IP from the hidden input element or if it is not set, use localhost
var eventSource = new EventSource(`http://${serverIP}:8001/watch_log`); // create a new EventSource object with the server IP and port 8001
var eventSource2 = new EventSource(`http://${serverIP}:8001/watch_log?log_override=YSFGateway`); // create a new EventSource object with the server IP and port 8001
const callsignLine = document.getElementById("callsign");
const dateLine = document.getElementById("date");
const sourceLine = document.getElementById("source");
const callsignRegex = /\b[A-Z0-9]{1,2}[0-9]{1}[A-Z]{1,3}\b/g; // regex matches callsigns with 1-2 numbers, 1 number, and 1-3 letters
const rfOrNetworkRegex = /\bRF\b|\bnetwork\b/g; // regex matches RF or network strings
const endOfTxRegex = /\bend of transmission\b/g; // regex matches end of transmission strings
const dateRegex = /\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\b/g; // regex matches date strings in the format YYYY-MM-DD HH:MM:SS.SSS
const myCallsign = document.getElementById("my_callsign").textContent;
const tableBody = document.getElementById("log_table");
const table = document.getElementById("call_log");
const indicator = document.getElementById("indicator");
const reflector = document.getElementById("reflector");
const clearLogButton = document.getElementById("clear_log");
const expansionButton = document.getElementById("expansion_button");
let blinking = false;
let endOfMessage = false;
let lastLine;
let queue = [];

/* event listeners */
/*
    * eventSource.onmessage - This event listener listens for incoming messages from the server and parses the data to find the callsign, source, and date. It then
    * pushes the data to the queue.
    * 
    * eventSource.onerror - This event listener listens for errors from the server and logs them to the console.
    *
    * eventSource2.onmessage - This event listener listens for incoming messages from the server and parses the data to find the reflector/room. 
    * It then sets the text content of the reflector element to the reflector/room.
    * 
    * eventSource2.onerror - This event listener listens for errors from the server and logs them to the console.
    * 
    * clearLogButton.addEventListener - This event listener listens for a click on the clear log button and clears the log table.
    * 
    * expansionButton.addEventListener - This event listener listens for a click on the expansion button and toggles the scrollable and
    * sticky-header classes on the table.
    * 
*/
eventSource.onmessage = function(event) {
    const callsignMatch = event.data.match(callsignRegex);
    const rfOrNetworkMatch = event.data.match(rfOrNetworkRegex);
    const dateMatch = event.data.match(dateRegex);
    const endOfTxMatch = event.data.match(endOfTxRegex);
    let formattedDate = new Date(dateMatch[0]+'Z').toLocaleString();
    if (callsignMatch) {
        if (rfOrNetworkMatch.includes('RF')) {
            queue.push(`Time: ${formattedDate} Source: RF: Callsign: ${callsignMatch[0]}`);
        }
        else if (rfOrNetworkMatch.includes('network')) {
            queue.push(`Time: ${formattedDate} Source: Network: Callsign: ${callsignMatch[0]}`);
        } else {
            queue.push(`Time: ${formattedDate} Source: Unknown: Callsign: ${callsignMatch[0]}`);
        }
    }
    if (endOfTxMatch) {
        endOfMessage = true;
    } else {
        endOfMessage = false;
    }
};

eventSource.onerror = function(error) {
    console.error("Failed to connect to SSE at: ", eventSource.url, "with error: ", error);
    console.error("This event source is for MMDVMHost logs and used to identify the callsign and source.");
};

eventSource2.onmessage = function(event) {
    if (event.data.includes('Linked to')) {
        reflector.textContent = event.data.split('Linked to ')[1];
    }
    else if (event.data.includes('Disconnect by remote command')) {
        reflector.textContent = '';
    }
};

eventSource2.onerror = function(error) {
    console.error("Failed to connect to SSE at: ", eventSource.url, "with error: ", error);
    console.error("This event source is for YSFGateway logs and used to identify the reflector/room.");
};

clearLogButton.addEventListener('click', () => {
    while (tableBody.firstChild) {
        tableBody.removeChild(tableBody.firstChild);
    }
});

expansionButton.addEventListener('click', () => {
    let text = expansionButton.textContent;
    console.log(text);
    if (text === '▼') {
        expansionButton.textContent = '◄';
    } else if (text === '◄') {
        expansionButton.textContent = '▼';
    }
    table.classList.toggle('scrollable');
    table.classList.toggle('sticky-header');
});

/*
    * updateLog - This function updates the "radio display" with the latest activity and logs it to the table.
    *
    * using the queue, the function checks if the queue is empty and if it is, it returns. If the queue is not empty, it shifts the first element from the queue
    * and checks if the line is the same as the last line. If it is, it changes the color of the callsign line to green and returns. If the line is not the same
    * as the last line, it sets the last line to the current line, changes the color of the callsign line to red, and sets the text content of the callsign line
    * to the callsign. It then sets the text content of the date line to the date and the source line to the source. It then calls the createLogRow function with
    * the date, source, and callsign as arguments.
    * 
*/
function updateLog() {
    if (queue.length === 0) {
        return;
    }
    const line = queue.shift();
    if (line === lastLine) {
        return;
    }
    if (blinking === false) {
        toggleIndicator();
    }
    lastLine = line;
    callsignLine.style.color = "red";
    callsignLine.textContent = line.split("Callsign: ")[1];
    dateLine.textContent = line.split("Time: ")[1].split(" Source: ")[0];
    sourceLine.textContent = line.split("Source: ")[1].split(" Callsign: ")[0];
    createLogRow(dateLine.textContent, sourceLine.textContent, callsignLine.textContent);
    if (endOfMessage === true && blinking === true) {
        toggleIndicator();
    }   
}

/*
    * createLogRow - This function creates a new row in the table with the date, source, and callsign as the content.
    *
    * @param {string} date - The date of the log entry.
    * @param {string} source - The source of the log entry.
    * @param {string} callsign - The callsign of the log entry.
    * 
*/
function createLogRow(date, source, callsign) {
    var newRow = tableBody.insertRow();
    newRow.insertCell().textContent = date;
    newRow.insertCell().textContent = source;
    newRow.insertCell().textContent = callsign;
    if (table.classList.contains('scrollable')) {
        table.scrollTop = tableBody.scrollHeight; // scroll to the bottom of the table
    }
}

/*
    * toggleIndicator - This function toggles the indicator between a filled circle and an empty circle.
    *
    * if the indicator has the class of blink, it removes the class. If it does not have the class, it adds the class.
    * 
    * if the indicator is blinking, it clears the interval and sets the text content of the indicator to an empty circle. 
    * If the indicator is not blinking, it sets the interval to toggle the text content between a filled circle and an empty circle.
    * 
    * @param {boolean} blinking - A boolean to determine if the indicator is blinking or not.
    * @param {number} blinkInterval - An interval to toggle the text content of the indicator.
    * 
    * @returns {void}
    *
*/
function toggleIndicator() {
    /* if (indicator.classList.contains('blink')) {
        indicator.classList.remove('blink');
    } else {
        indicator.classList.add('blink');
    } */
    if (blinking === true) {
        console.log("Turning off blinking");
        blinking = false;
        clearInterval(blinkInterval)
        indicator.textContent = '○';
    } else if (blinking === false){
        console.log("Turning on blinking");
        blinking = true;
        blinkInterval = setInterval(() => {
            if (indicator.textContent === '●') {
                indicator.textContent = '○';
            } else if (indicator.textContent === '○'){
                indicator.textContent = '●';
            }
        }, 500);
    }
}

/* on eventSource connect, set interval to update the "radio display" and log table from SSE queue providing Callsign/Source info */
eventSource.onopen = function() {
    updateLogInterval = setInterval(updateLog, 100);
}