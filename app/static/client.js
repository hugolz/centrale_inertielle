
let calib = 0;

// Modify calib depending on slider
(function(){
    let slider = document.getElementById("myRange");
    if (slider == null){
        return
    }
    calib = slider.value/10 ; // Display the default slider value

    // Update the current slider value (each time you drag the slider handle)
    slider.oninput = function() {
      calib = parseFloat(this.value);
    }
})()

// Move from the main select menu
async function changeState(requested_state) {
    console.log(`Requesting new status: ${requested_state}`);
    try {
      const response = await fetch("#", {
        method: "POST", 
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
            state : requested_state
        }),
      });
  
      const result = await response.text();
      console.log("New status success: ", result);
    } catch (error) {
      console.error("Couldn't change state due to:", error);
    }
    location.reload();
}

function update_compass(azimuth){
    let compass =  document.querySelector("#Card");
    if (compass == null){
        console.log("Cannot update compass, compass is null");
        return;
    }
    azimuth += calib

    compass.setAttribute("transform", "rotate(" + -azimuth + " 256.0 256.0 ) ");
    if (azimuth <=0) {
        azimuth += 360.
    }
    document.getElementById("headingDisplay").innerHTML = "<br>" + Math.round(azimuth) + '°';
}


function update_artificial_horizon(yaw, pitch, roll) {	
    // console.log(yaw + " " + pitch + " " + roll)
    document.getElementById("pitchDisplay").innerHTML = "<br>" + pitch
    document.getElementById("rollDisplay").innerHTML = "<br>" + roll

    document.querySelector("#Pitch").setAttribute("transform", "translate(" + yaw + "," + pitch + ")");
    document.querySelector("#Roll").setAttribute("transform", "rotate(" + roll + ", 256.0, 256.0)");
}

// function azimuth(azim) {
//     // calib < 0 ? azim -=(-calib): azim+= calib ?????????
//     azim += calib
//     document.querySelector("#Card").setAttribute("transform", "rotate(" + -azim + " 256.0 256.0 ) ");
//     azim <= 0 ? azim += 360: azim = azim
//     document.getElementById("headingDisplay").innerHTML = "<br>" + azim + '°';
// }

function update_altitude(alt) {
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


// Unused **for now**
// function demo() {	
//     var r = document.attitude.roll.value;		
//     var timer = setInterval(() => {
//         r = parseFloat(document.attitude.step.value) + parseFloat(document.attitude.roll.value);
//         update_artificial_horizon(document.attitude.yaw.value, document.attitude.pitch.value, r); 
//         document.attitude.roll.value = r;
//     }, 500);							
//     setTimeout(() => { clearInterval(timer); alert("stop"); }, document.attitude.time.value * 1000);
// }
// function rollLeft(roll, step) {	
//     r = parseFloat(step) + parseFloat(roll);
//     update_artificial_horizon(document.attitude.yaw.value, document.attitude.pitch.value, r);
//     document.attitude.roll.value = r;
// }
// function rollRight(roll, step) {
//     r = parseFloat(roll) - parseFloat(step);
//     update_artificial_horizon(document.attitude.yaw.value, document.attitude.pitch.value, r);
//     document.attitude.roll.value = r;
// }
// function pitchDown(pitch, step) {
//     p = parseFloat(pitch) - parseFloat(step);
//     update_artificial_horizon(document.attitude.yaw.value, p, document.attitude.roll.value);
//     document.attitude.pitch.value = p;
// }
// function pitchUp(pitch, step) {
//     p = parseFloat(pitch) + parseFloat(step);
//     update_artificial_horizon(document.attitude.yaw.value, p, document.attitude.roll.value);
//     document.attitude.pitch.value = p;
// }
// function yawLeft(yaw, step) {
//     y = parseFloat(step) + parseFloat(yaw);
//     update_artificial_horizon(y, document.attitude.pitch.value, document.attitude.roll.value);
//     document.attitude.yaw.value = y;
// }
// function yawRight(yaw, step) {
//     y = parseFloat(yaw) - parseFloat(step);
//     update_artificial_horizon(y, document.attitude.pitch.value, document.attitude.roll.value);
//     document.attitude.yaw.value = y;
// }