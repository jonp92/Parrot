/*
    * watch_log.js - This file is responsible for connecting to SSE and updating the "radio display" with the latest activity and logging it to the table.
    *
    * Author: Jonathan L. Pressler
    * Date: 2024-04-04
    * Version: 1.0
    * License: MIT
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
const indicator = document.getElementById("indicator");
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
*/
eventSource.onmessage = function(event) {
    const callsignMatch = event.data.match(callsignRegex);
    const rfOrNetworkMatch = event.data.match(rfOrNetworkRegex);
    const dateMatch = event.data.match(dateRegex);
    const endOfTxMatch = event.data.match(endOfTxRegex);
    if (callsignMatch) {
        if (rfOrNetworkMatch.includes('RF')) {
            queue.push(`Time: ${dateMatch[0]} Source: RF: Callsign: ${callsignMatch[0]}`);
        }
        else if (rfOrNetworkMatch.includes('network')) {
            queue.push(`Time: ${dateMatch[0]} Source: Network Callsign: ${callsignMatch[0]}`);
        } else {
            queue.push(`Unknown: ${callsignMatch[0]}`);
        }
    }
    if (endOfTxMatch) {
        endOfMessage = true;
    } else {
        endOfMessage = false;
    }
};

eventSource.onerror = function(error) {
    console.error("Failed to connect to SSE", error);
};

eventSource2.onmessage = function(event) {
    console.log(event.data);
};

eventSource2.onerror = function(error) {
    console.error("Failed to connect to SSE_2", error);
};

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
        callsignLine.style.color = "#0f0";
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
}

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

/* on eventSource connect, set interval to update the "radio display" and log table from SSE queue */
eventSource.onopen = function() {
    updateLogInterval = setInterval(updateLog, 100);
}
//setInterval(updateLog, 100);