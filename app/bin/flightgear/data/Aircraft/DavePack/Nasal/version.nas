#
#
#  Converts the version string into a property of type "double".  This can then be easily
#  checked in an XML <condition> block.
#
#

var versionString = getprop("sim/version/flightgear");
var vArray = split(".", versionString);
var version = num(vArray[0])*100 + num(vArray[1])*10 + num(vArray[2]);
setprop("sim/version/fgversion", version);
