var shiftMode = false;

function resetFields () {
	var guavaSamples = document.getElementById("guavaSamples");
	var manualFields = document.getElementById("manualFields");
	var sessionID =    document.getElementById("sessionID");
	var email =        document.getElementById("email");
	var sampleVolume = document.getElementById("sampleVolume");
	var numEvents =    document.getElementById("numEvents");
	var timeLimit =    document.getElementById("timeLimit");
	var speed = 	   document.getElementById("speed");
	var rowColumn =    document.getElementById("rowColumn");

	guavaSamples.value = "Samples\n(Can be randomized)\n\n\nDon't use dash use underscore...\n\nAll other special characters won't work!";
	manualFields.value = "INSTRUCTIONS\n\n1) Enter controls on far left box\n2) Enter sample names in the middle box\n3) Select/enter machine parameters\n4) Click populate\n5) Click Update FROM table\n6) Click submit";
	sessionID.value = "";
	email.value = "";

	sampleVolume.value = "10";
	numEvents.value = "5000";
	timeLimit.value = "600";
	speed.value = "1";
	rowColumn.value = "1";

	for (var count = 1; count <= 96; count++) {
		document.getElementById(count).value = "";
		document.getElementById(count).onkeydown = checkKey;
		document.getElementById(count).onkeyup = keyUp;
		}
	}

// To understand events, please refer to http://www.quirksmode.org/js/events_tradmod.html
function checkKey (e) {
	if (!e) var e = window.event;			// Cross-platform event handling

	if (e.keyCode == 8) { return e.keyCode; }						// Allow backspace
	if (e.keyCode == 16) { shiftMode = true; }						// Track the shift key
	if ((e.keyCode >= 48) && (e.keyCode <= 57) && (shiftMode)) { return false; }		// Shift on 0-9 gives special characters we don't want
	if ((e.keyCode >= 48) && (e.keyCode <= 57) && (!shiftMode)) { return e.keyCode; }	// Actual numbers should be allowed
	if ((e.keyCode >= 65) && (e.keyCode <= 90) ) { return e.keyCode; }			// Both upper case and lower case letters are allowed
	else { return false; }
	}

// This is used to detect if the shift key is being used
function keyUp (e) {
	if (!e) var e = window.event;
	if (e.keyCode == 16) { shiftMode = false; }
	}

function populateTable () {

	var guavaSamples = document.getElementById("guavaSamples");
	var manualFields = document.getElementById("manualFields");

	if(guavaSamples.value.match(/^Samples/)) { guavaSamples.value = ""; }

	// Disallow anything other than letters and numbers
	if (guavaSamples.value.match(/[^a-zA-Z0-9_\n]+/)) { window.alert("Please enter only letters and numbers (no spaces please!)"); return; }

	var sampleArray = guavaSamples.value.split("\n");

	// Clear the current contents of the table
	for (var count = 1; count <= 96; count++) { document.getElementById(count).value = ""; }

	// Randomize the samples if the user has selected this option
	if (document.getElementById("randomize").checked) { sampleArray.sort(randOrd); }

	// Add the samples which may or may not have been randomized
	for (var count = 1; count < sampleArray.length + 1; count++) {
		document.getElementById(count).value = sampleArray[count-1];
		}
	}

// Generate random numbers for the purpose of randomizing an array
function randOrd() { 	return (Math.round(Math.random())-0.5); } 

function dumpTable() {
	var sampleVolume = document.getElementById("sampleVolume");
	var numEvents = document.getElementById("numEvents");
	var timeLimit = document.getElementById("timeLimit");
	var sessionID = document.getElementById("sessionID");
	var email = document.getElementById("email");
	var manualFields = document.getElementById("manualFields");
	var speed = document.getElementById("speed");
	
	// Sample volume must be an integer (Default: 10)
	if(!sampleVolume.value.match(/^[1-9][0-9]{0,6}$/)) { window.alert("You must specify an integer for sample volume"); return; }

	// The number of events must be an integer (Default: 5000)
	if(!numEvents.value.match(/^[1-9][0-9]{0,5}$/)) { window.alert("You must specify an integer for the number of events (1-999999)"); return; }
	
	// Time limit must be an integer (Default: 600)
	if(!timeLimit.value.match(/^[1-9][0-9]{0,3}$/)) { window.alert("You must specify an integer for time limit (1-9999)"); return; }

	// sessionID must be alphanumeric, 3-20 characters
	if(!sessionID.value.match(/^[a-zA-Z0-9]{3,20}$/)) { window.alert("ExperimentID must be alphanumeric, 3-20 characters."); return; }

	// email must be a valid email
	if(!email.value.match(/^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+.[a-zA-Z]{2,4}$/)) { window.alert("You must provide a valid email address."); return; }

	manualFields.value = "";

	var velocity = "UNSPECIFIED";
	if(speed.value == 1) { velocity = "High"; }
	else if (speed.value == 2) { velocity = "Medium"; }
	else if (speed.value == 3) { velocity = "Low"; }

	for (var count = 1; count <= 96; count++) {
		var rowLetter;
		var rowIndex = count % 12;
		if (rowIndex == 0) { rowIndex = 12; }
		if (rowIndex <= 9) { rowIndex = "0" + rowIndex; }

		if (Math.ceil(count/12) == 1) { rowLetter = "A"; }	else if (Math.ceil(count/12) == 2) { rowLetter = "B"; }
		else if (Math.ceil(count/12) == 3) { rowLetter = "C"; }	else if (Math.ceil(count/12) == 4) { rowLetter = "D"; }
		else if (Math.ceil(count/12) == 5) { rowLetter = "E"; }	else if (Math.ceil(count/12) == 6) { rowLetter = "F"; }
		else if (Math.ceil(count/12) == 7) { rowLetter = "G"; }	else if (Math.ceil(count/12) == 8) { rowLetter = "H"; }

		var well = rowLetter + rowIndex;

		// Now get the contents of the pertinent cell...
		var sampleName = "";
		if (document.getElementById(count).value != "") { sampleName = document.getElementById(count).value; }
		manualFields.value = manualFields.value + sampleName + ", " + well + ", " + sampleVolume.value + ", 1.00, " + numEvents.value + ", 600, No, Yes, 3, " + velocity + "\n";
		}

	return;
	}

window.onload = resetFields;
