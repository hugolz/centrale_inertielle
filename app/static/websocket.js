// Address of the server
let WS_ADDRESS = '172.22.96.1'

let websocket = false;

document.addEventListener("DOMContentLoaded", function (event) {
    if ("WebSocket" in window) {
        websocket = true;
    } else {
        // no web socket support
        websocket = false;
    }

    var msg = { event: 'register', };
    ws_send(msg);
});

function ws_send(msg) {
    if (websocket) {
        // if ws is not open call open_ws, which will call ws_send back
        if (typeof (ws) == 'undefined' || ws.readyState === undefined || ws.readyState > 1) {
            open_ws(msg);
        } else {
            ws.send(JSON.stringify(msg));
            console.log(`Sending ${msg}`);
        }
    }
}

function open_ws(msg) {
    if (typeof (ws) != 'undefined' && ws.stateState !== undefined && ws.readyState <= 1) {
        return;
    }
    // websocket on same server with address /websocket
    ws = new WebSocket(`ws://${WS_ADDRESS}:8888/websocket`);
    // /websocket

    ws.onopen = function () {
        // Web Socket is connected, send data using send()
        console.log("ws open");
        if (msg.length != 0) {
            ws_send(msg);
        }
    };

    ws.onmessage = function (evt) {
        msg = JSON.parse(evt.data);
        console.log(`Receiving ${JSON.stringify(msg)}`);
            
        if (msg.event == "fdm") {
            let yaw = msg.data.yaw * 180 / Math.PI;
            let pitch = msg.data.pitch * 180 / Math.PI;
            let roll = msg.data.roll * 180 / Math.PI;
            let azimuth = msg.data.azimuth
            let svg = document.getElementById("instrument_wrapper");


            if (document.getElementById("pitchDisplay") != null) {
                update_artificial_horizon(yaw, pitch, roll);
            }

            if (svg != null) {
                console.log(`${yaw}, ${pitch}, ${roll}`)
                update_artificial_horizon2(yaw, pitch, roll);
                update_compass(azimuth)
                // console.log("ok")
            }

        } else {
            console.log('Unknown event: ' + msg.event)
        }
    };

    ws.onclose = function () { 
        // websocket is closed, re-open
        console.log("Connection is closed... reopen");
        var msg = { event: 'register', };
        setTimeout(function () { ws_send(msg); }, 1000);
    };
}