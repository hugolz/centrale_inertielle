let PRESS_COLOR = 'red';
// This is the local addres of the machine that i use to dev this, you'll need to change it
let WS_ADDRESS = '192.168.56.1' 

let websocket = false;

function isMobile() {
  try{ document.createEvent("TouchEvent"); return true; }
  catch(e){ return false; }
}

$(document).ready(function () {
    if ("WebSocket" in window){
        websocket = true;
    }else{
        // no web socket support
        websocket = false;
    }

    var msg = { event: 'register', };
    ws_send(msg);
});

function ws_send(msg){
    if( websocket == true ){
        // if ws is not open call open_ws, which will call ws_send back
        if( typeof(ws) == 'undefined' || ws.readyState === undefined || ws.readyState > 1){
            open_ws(msg);
        }else{
            ws.send( JSON.stringify(msg) );
            console.log(`Sending ${msg}`);
        }
    }
}

function open_ws(msg){
    if( typeof(ws) == 'undefined' || ws.readyState === undefined || ws.readyState > 1){
        // websocket on same server with address /websocket
        ws = new WebSocket(`ws://${WS_ADDRESS}:8888/websocket`);

        ws.onopen = function(){
            // Web Socket is connected, send data using send()
            console.log("ws open");
            if( msg.length != 0 ){
                ws_send(msg);
            }
        };

        ws.onmessage = function (evt){
            msg = JSON.parse(evt.data)
            console.log(`Receiving ${msg}`);
            
            if( msg.event == "direction_press" ){
                let button_id = direction_to_button_id(msg.data);
                if (button_id != ''){
                    direction_trigger(button_id, 'press')
                }else{
                    console.log(`Could not find the right id for given button ${msg.data}`)
                }
            }else if( msg.event == "direction_release" ){
                let button_id = direction_to_button_id(msg.data);
                if (button_id != ''){
                    direction_trigger(button_id, 'release')
                }else{
                    console.log(`Could not find the right id for given button ${msg.data}`)
                }
            }else{
                console.log('Could not understand reveived message')
            }
        };

        ws.onclose = function(){ 
            // websocket is closed, re-open
            console.log("Connection is closed... reopen");
            var msg = { event: 'register', };
            setTimeout( function(){ws_send(msg);}, 1000 );
        };
   }
}

function button_id_to_direction(id){
    let direction = '';
    switch (id){
    case 'button_up':
        direction = 'Up';
        break
    case 'button_left':
        direction = 'Left';
        break
    case 'button_down':
        direction = 'Down';
        break
    case 'button_right':
        direction = 'Right';
        break
    }
    return direction
}

function direction_to_button_id(dir){
    let id = '';
    switch (dir){
    case 'Up':
        id = 'button_up';
        break
    case 'Left':
        id = 'button_left';
        break
    case 'Down':
        id = 'button_down';
        break
    case 'Right':
        id = 'button_right';
        break
    }
    return id
}

function direction_trigger(id, state){
    let color = '';
    if (state == 'press'){
        color = PRESS_COLOR
    }
    document.getElementById(id).style.backgroundColor = color
    if (state == 'press'){
        console.log(`${id} pressed`)
    }else if (state == 'release'){
        console.log(`${id} released`)
    }else{
        console.log(`state '${state}' could not be understood`)
    }
    
}

function button_press(id, ev){
    let direction = button_id_to_direction(id);
    if (direction == ''){
        console.log(`Could not translate button id: ${id} to an understandable direction`)
        return 1
    }
    ws_send({event: "direction_press", data: direction, button_event: ev})
    direction_trigger(id, 'press')

}
function button_release(id, ev){
    let direction = button_id_to_direction(id);
    if (direction == ''){
        console.log(`Could not translate button id: ${id} to an understandable direction`)
        return 1
    }
    ws_send({event: "direction_release", data: direction, button_event: ev})
    direction_trigger(id, 'release')
}

/// sets an event listener func for each event for each elements
function AddMultiEventListener(arg_elements, arg_events, func){
    arg_elements.split(' ').forEach(el => arg_events.split(' ').forEach(ev => document.getElementById(el).addEventListener(ev, function() {
        func(el, ev)
    })))
}

if (isMobile()){
    AddMultiEventListener('button_up button_left button_down button_right', 'touchstart', button_press)
    AddMultiEventListener('button_up button_left button_down button_right', 'touchend', button_release)
}else{
    AddMultiEventListener('button_up button_left button_down button_right', 'mousedown', button_press)
    AddMultiEventListener('button_up button_left button_down button_right', 'mouseup mouseleave', button_release)
}


