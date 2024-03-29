let PRESS_COLOR = 'red';
// This is the local addres of the machine that i use to dev this, you'll need to change it
let WS_ADDRESS = '192.168.56.1' 

let websocket = false;

$(document).ready(function () {
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
    if (websocket == true) {
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
    if (typeof (ws) == 'undefined' || ws.readyState === undefined || ws.readyState > 1) {
        // websocket on same server with address /websocket
        ws = new WebSocket(`ws://${WS_ADDRESS}:8888/websocket`);

        ws.onopen = function () {
            // Web Socket is connected, send data using send()
            console.log("ws open");
            if (msg.length != 0) {
                ws_send(msg);
            }
        };

        ws.onmessage = function (evt) {
            msg = JSON.parse(evt.data);
            let pi = Math.PI
            console.log(`Receiving ${JSON.stringify(msg)}`);
            
            if (msg.event == "fdm") {
                let yaw = (msg.data.yaw) * 180 / pi;
                let pitch = (msg.data.pitch) * 180 / pi;
                let roll = (msg.data.roll) * 180 / pi;
                let azim = (msg.data.azimuth)
                att(yaw, pitch, roll);
                azimuth(azim)
                console.log("ok")

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
}


function att(yaw, pitch, roll) {	
    console.log(yaw + " " + pitch + " " + roll)
    document.querySelector("#Pitch").setAttribute("transform", "translate(" + yaw + "," + pitch + ")");
    document.querySelector("#Roll").setAttribute("transform", "rotate(" + roll + ", 256.0, 256.0)");
}

function azimuth(azim) {	
    azim = float(azim)  
    document.querySelector("#Card").setAttribute("transform", "rotate(" + azim + " 256.0 256.0 ) ");
    console.log(azim)
}

function altitude(alt) {
    resteC = alt % 1000;
    c = resteC * 90 / 250;
    resteM = alt % 10000;
    m = resteM * 90 / 2500;
    resteDM = alt % 100000;
    dm = resteDM * 90 / 25000;
    
    document.querySelector("#Cent").setAttribute("transform", "rotate(" + c + " 256.0 256.0 ) ");
    document.querySelector("#Mille").setAttribute("transform", "rotate(" + m + " 256.0 256.0 ) ");
    document.querySelector("#DixMille").setAttribute("transform", "rotate(" + dm + " 256.0 256.0 ) ");
    document.alt.alt.value = alt;
}

    
function demo() {	
    var r = document.attitude.roll.value;		
    var timer = setInterval(() => {
        r = parseFloat(document.attitude.step.value) + parseFloat(document.attitude.roll.value);
        att(document.attitude.yaw.value, document.attitude.pitch.value, r); 
        document.attitude.roll.value = r;
    }, 500);							
    setTimeout(() => { clearInterval(timer); alert("stop"); }, document.attitude.time.value * 1000);
}

function rollLeft(roll, step) {	
    r = parseFloat(step) + parseFloat(roll);
    att(document.attitude.yaw.value, document.attitude.pitch.value, r);
    document.attitude.roll.value = r;
}

function rollRight(roll, step) {
    r = parseFloat(roll) - parseFloat(step);
    att(document.attitude.yaw.value, document.attitude.pitch.value, r);
    document.attitude.roll.value = r;
}

function pitchDown(pitch, step) {
    p = parseFloat(pitch) - parseFloat(step);
    att(document.attitude.yaw.value, p, document.attitude.roll.value);
    document.attitude.pitch.value = p;
}

function pitchUp(pitch, step) {
    p = parseFloat(pitch) + parseFloat(step);
    att(document.attitude.yaw.value, p, document.attitude.roll.value);
    document.attitude.pitch.value = p;
}

function yawLeft(yaw, step) {
    y = parseFloat(step) + parseFloat(yaw);
    att(y, document.attitude.pitch.value, document.attitude.roll.value);
    document.attitude.yaw.value = y;
}

function yawRight(yaw, step) {
    y = parseFloat(yaw) - parseFloat(step);
    att(y, document.attitude.pitch.value, document.attitude.roll.value);
    document.attitude.yaw.value = y;
}


