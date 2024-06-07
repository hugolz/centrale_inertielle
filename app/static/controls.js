var mouse_position = { x: 0., y: 0. };

document.onmousemove = (event) => {
    var dot, eventDoc, doc, body, pageX, pageY;

    event = event || window.event; // IE-ism

    // If pageX/Y aren't vailable and clientX/Y are,
    // calculate pageX/Y - logic taken from jQuery.
    // (This is to support old IE)
    if (event.pageX == null && event.clientX != null) {
        eventDoc = (event.target && event.target.ownerDocument) || document;
        doc = eventDoc.documentElement;
        body = eventDoc.body;

        event.pageX = event.clientX +
            (doc && doc.scrollLeft || body && body.scrollLeft || 0) -
            (doc && doc.clientLeft || body && body.clientLeft || 0);
        event.pageY = event.clientY +
            (doc && doc.scrollTop || body && body.scrollTop || 0) -
            (doc && doc.clientTop || body && body.clientTop || 0);
    }

    mouse_position = {
        x: event.pageX,
        y: event.pageY
    };
}

// This creates some sort of enclosed environment, helps compartmentalize the code
(function () {
    var dragged = false;
    var drag_start_angle;

    var base_angle = calib

    var compass = document.querySelector("#Card")

    var rect = compass.getBoundingClientRect();
    let compass_rect = { x: rect.x, y: rect.y, w: rect.right - rect.left, h: rect.bottom - rect.top }

    let compass_center = {
        x: compass_rect.x + compass_rect.w / 2,
        y: compass_rect.y + compass_rect.h / 2
    }

    function two_points_angle(base, point) {
        return Math.atan2(point.y - base.y, point.x - base.x)
    }

    function update_compas() {
        if (!dragged) {
            base_angle = calib;
            return;
        }

        // When we drag the compass to the left ...
        // The compass rotates left
        let angle_delta = drag_start_angle - two_points_angle(compass_center, mouse_position) * (180 / Math.PI) + 90 
        // The compass rotates right (plane goes left)
        // let angle_delta = two_points_angle(compass_center, getMousePosition()) * (180 / Math.PI) - 90 - drag_start_angle 

        document.getElementById("myRange").value = base_angle +  angle_delta;
        calib = base_angle + angle_delta
        // azimuth(base_angle + angle_delta)
    }

    document.querySelector("#DG").addEventListener("mousedown", (event) => {
        dragged = true;
        // drag_start_angle = getMousePosition()
        drag_start_angle = two_points_angle(compass_center, mouse_position) * (180 / Math.PI) - 90

    });


    document.querySelector("#DG").addEventListener("mouseup", (event) => {
        dragged = false;
        console.log(mouse_position)
    });

    setInterval(update_compas, 1); // setInterval repeats every X ms

})()
