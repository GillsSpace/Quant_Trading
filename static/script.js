// Initialize the socket connection
const socket = io();

// Listen for 'time' event from the server
socket.on('time_update', function(data) {
    document.getElementById('time').textContent = data.date + " - " + data.time;
});


