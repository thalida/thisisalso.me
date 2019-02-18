var socket = io('http://0.0.0.0:5002');
socket.on('post_update', function() {
    console.log(arguments)
});

// websocket = new WebSocket("ws://0.0.0.0:5678/");
// websocket.onmessage = function (event) {
//     data = JSON.parse(event.data);
//     console.log(data)
//     switch (data.type) {
//         case 'state':
//             value.textContent = data.value;
//             break;
//         case 'users':
//             users.textContent = (
//                 data.count.toString() + " user" +
//                 (data.count == 1 ? "" : "s"));
//             break;
//         default:
//             console.error(
//                 "unsupported event", data);
//     }
// };
