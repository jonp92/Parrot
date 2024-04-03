var eventSource = new EventSource("http://localhost:8001/watch_log");
const callsignLine = document.getElementById("callsign");
const dateLine = document.getElementById("date");
const sourceLine = document.getElementById("source");
const callsignRegex = /\b[A-Z0-9]{1,2}[0-9]{1}[A-Z]{1,3}\b/g;
const rfOrNetworkRegex = /\bRF\b|\bnetwork\b/g;
const dateRegex = /\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\b/g;
const myCallsign = document.getElementById("my_callsign").textContent;
let lastLine;
let queue = [];

eventSource.onmessage = function(event) {
    const callsignMatch = event.data.match(callsignRegex);
    const rfOrNetworkMatch = event.data.match(rfOrNetworkRegex);
    const dateMatch = event.data.match(dateRegex);
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
};

eventSource.onerror = function(error) {
    console.error("Failed to connect to SSE", error);
};

function updateLog() {
    if (queue.length === 0) {
        return;
    }

    const line = queue.shift();
    if (line === lastLine) {
        callsignLine.style.color = "#0f0";
        return;
    }

    lastLine = line;
    callsignLine.style.color = "red";
    callsignLine.textContent = line.split("Callsign: ")[1];
    dateLine.textContent = line.split("Time: ")[1].split(" Source: ")[0];
    sourceLine.textContent = line.split("Source: ")[1].split(" Callsign: ")[0];
}

setInterval(updateLog, 1000);