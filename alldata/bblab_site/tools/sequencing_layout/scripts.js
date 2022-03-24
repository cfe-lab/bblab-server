	function validateForm() {
		var userName = document.getElementById("userName").value;
		var plateID = document.getElementById("plateID").value;
		var emailAddress = document.getElementById("emailAddress").value;
		var machine = document.getElementById("sequencingMachine");

		if (machine[machine.selectedIndex].value == "A") { alert("Please specify a sequencing machine"); return false; }

		var regExpression = /^[a-zA-Z0-9]{3,8}$/;

		if (!userName.match(regExpression)) {
			alert("Username must be alphanumeric, with 3-8 characters.");
			return false;
			}
		if (!plateID.match(regExpression)) {
			alert("plateID must be alphanumeric, with 3-8 characters.");
			return false;
			}

		var regExpression2 = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+.[a-zA-Z]{2,4}$/; 

		if (!emailAddress.match(regExpression2)) {
			alert("Please enter a valid email");
			return false;
			}

		var manualFields = document.getElementById("manualFields").value;
		regExpression = /[!@#$%^&*()=`~;':"<>,./? ]/;
		if (manualFields.match(regExpression)) {
			alert("No special characters allowed.\nThat includes the space character.");
			return false;
			}
		return true;
		}

	function restrictInput(e) {
		if(this.value.length >= 12) { event.preventDefault(); }		// Only allow primer and sample names up to 12 characters

		var key = e.keyCode || e.which;
		if ((key >= 65) && (key <= 90)) { }		// A-Z (65 to 90)
		else if ((key >= 95) && (key <= 122)) { }	// Underscore (95) and a-z (96 to 122)
		else if ((key >= 48) && (key <= 57)) { }	// 0-9 (48-57)
		else { event.preventDefault(); }		// Block keypress event
		}

	function clearFields() {
		var sampleEntry = document.getElementById("sampleEntry");
		var primerEntry = document.getElementById("primerEntry");
		var manualFields = document.getElementById("manualFields");
		var userName = document.getElementById("userName");		userName.value = "";
		var plateID = document.getElementById("plateID");		plateID.value = "";

		sampleEntry.value = 	"GUIDELINES: Samples\n\nNumbers, letters, or underscore.\n\nDon't use dash, the space character, or any other special characters.";
		primerEntry.value = 	"GUIDELINES: Primers\n\nNumbers, letters, or underscore.\n\nDon't use dash, the space character, or any other special characters.";

		manualFields.value = 	"INSTRUCTIONS\n\n" +
					"1) Enter primers and samples.\n   (Do NOT use the space character!)\n\n" +
					"2) Select the layout method. Check for multi-pipetting sanity.\n\n" +
					"3) 'Update FROM table' - generate ABI file contents.\n\n4) 'Submit' - generate PLT and HTML files.";

		for (var count = 1; count <= 96; count++) {
			document.getElementById(count+"_a").value = "";	document.getElementById(count+"_a").addEventListener("keypress", restrictInput, false);
			document.getElementById(count+"_b").value = "";	document.getElementById(count+"_b").addEventListener("keypress", restrictInput, false);
			}
		}

	function populatePrimersOnRows() {
		for (var count = 1; count <= 96; count++) {				// Clear the existing fields
			document.getElementById(count+"_a").value = "";
			document.getElementById(count+"_b").value = "";
			}
		var primerInput = document.getElementById("primerEntry").value;		// Get the primers and samples (Newline delimited)
		var sampleInput = document.getElementById("sampleEntry").value;
		var primerArray = primerInput.split("\n");				// Extract out individual primers and samples
		var sampleArray = sampleInput.split("\n");
		var currPosition = 1;							// We start in well 1

		var i, j;

		for(i = 0; i < primerArray.length; i++) {
			if(primerArray[i].length==0) continue;				// The split function is imperfect: this is a bug fix
											// For empty lines
			for(j = 0; j < sampleArray.length; j++) {
				if(sampleArray[j].length==0 || currPosition > 96) continue;
				document.getElementById(currPosition+"_a").value = sampleArray[j];	// Write the sample into the layout field
				document.getElementById(currPosition+"_b").value = primerArray[i];	// Write the primer into the layout field

				if(sampleArray[j] == "X" || primerArray[i] == "X") {
					document.getElementById(currPosition+"_a").value = "X";
					document.getElementById(currPosition+"_b").value = "X";
					}
				currPosition++;
				}
			}
		}

        function populatePrimersOnRowsB() {
                for (var count = 1; count <= 96; count++) {                             // Clear the existing fields
                        document.getElementById(count+"_a").value = "";
                        document.getElementById(count+"_b").value = "";
                        }
                var primerInput = document.getElementById("primerEntry").value;         // Get the primers and samples (Newline delimited)
                var sampleInput = document.getElementById("sampleEntry").value;
                var primerArray = primerInput.split("\n");                              // Extract out individual primers and samples
                var sampleArray = sampleInput.split("\n");
                var currPosition = 1;                                                   // We start in well 1

		var i, j;

                for(i = 0; i < sampleArray.length; i++) {
                        if(sampleArray[i].length==0) continue;                          // The split function is imperfect: this is a bug fix
                                                                                        // For empty lines
                        for(j = 0; j < primerArray.length; j++) {
                                if(primerArray[j].length==0 || currPosition > 96) continue;
                                document.getElementById(currPosition+"_a").value = sampleArray[i];      // Write the sample into the layout field
                                document.getElementById(currPosition+"_b").value = primerArray[j];      // Write the primer into the layout field

				if(sampleArray[i] == "X" || primerArray[j] == "X") {
					document.getElementById(currPosition+"_a").value = "X";
					document.getElementById(currPosition+"_b").value = "X";
					}
                                currPosition++;
                                }
                        }
                }


	function populatePrimersOnCollumns() {

		for (var count = 1; count <= 96; count++) {                             // Clear the existing fields
                        document.getElementById(count+"_a").value = "";
                        document.getElementById(count+"_b").value = "";
                        }
                var primerInput = document.getElementById("primerEntry").value;         // Get the primers and samples (Newline delimited)
                var sampleInput = document.getElementById("sampleEntry").value;
                var primerArray = primerInput.split("\n");                              // Extract out individual primers and samples
                var sampleArray = sampleInput.split("\n");
                var currPosition = 1;							// If less than 97, add 12. If >= 97, subtract 96, add 1

		var i, j;


		for(i = 0; i < primerArray.length; i++) {
			if(primerArray[i].length==0) continue;

 			for(j = 0; j < sampleArray.length; j++) {
				if(sampleArray[j].length==0) continue;

				document.getElementById(currPosition+"_a").value = sampleArray[j];      // Write the sample into the layout field
				document.getElementById(currPosition+"_b").value = primerArray[i];      // Write the primer into the layout field

				if (sampleArray[j] == "X" || primerArray[i] == "X") {
					document.getElementById(currPosition+"_a").value = "X";
					document.getElementById(currPosition+"_b").value = "X";
					}

				if(currPosition <= 84) { currPosition += 12; }
				else { currPosition = currPosition - 83; }
				}
                        }
		}


        function populatePrimersOnCollumnsB() {

                for (var count = 1; count <= 96; count++) {                             // Clear the existing fields
                        document.getElementById(count+"_a").value = "";
                        document.getElementById(count+"_b").value = "";
                        }
                var primerInput = document.getElementById("primerEntry").value;         // Get the primers and samples (Newline delimited)
                var sampleInput = document.getElementById("sampleEntry").value;
                var primerArray = primerInput.split("\n");                              // Extract out individual primers and samples
                var sampleArray = sampleInput.split("\n");
                var currPosition = 1;                                                   // If less than 97, add 12. If >= 97, subtract 96, add 1

		var i, j;

                for(i = 0; i < sampleArray.length; i++) {
                        if(sampleArray[i].length==0) continue;

                        for(j = 0; j < primerArray.length; j++) {
                                if(primerArray[j].length==0) continue;

                                document.getElementById(currPosition+"_a").value = sampleArray[i];      // Write the sample into the layout field
                                document.getElementById(currPosition+"_b").value = primerArray[j];      // Write the primer into the layout field

                                if(currPosition <= 84) { currPosition += 12; }
                                else { currPosition = currPosition - 83; }
                                }
                        }
                }

	function populateSixPrimers () {
                for (var count = 1; count <= 96; count++) {				// Clear the existing fields
                        document.getElementById(count+"_a").value = "";
                        document.getElementById(count+"_b").value = "";
                        }

                var primerInput = document.getElementById("primerEntry").value;		// Get primers and samples (Newline delimited)
                var sampleInput = document.getElementById("sampleEntry").value;
                var primerArray = primerInput.split("\n");				// Extract primers and samples
                var sampleArray = sampleInput.split("\n");
                var currPosition = 1;

		var i, j;


                for(i = 0; i < sampleArray.length; i++) {
                        if(sampleArray[i].length==0) continue;

                        for(j = 0; j < primerArray.length; j++) {			// For every single primer...
                                if(primerArray[j].length==0) continue;

				if (currPosition == 97) { currPosition = 7; }

                                document.getElementById(currPosition+"_a").value = sampleArray[i];	// Write the sample into the layout field
                                document.getElementById(currPosition+"_b").value = primerArray[j];	// Write the primer into the layout field

				if (currPosition % 6 == 0) { currPosition += 7; }
				else { currPosition += 1; }
                                }
                        }

		}

	function populateFourPrimers () {
		for (var count = 1; count <= 96; count++) {
			document.getElementById(count+"_a").value = "";
			document.getElementById(count+"_b").value = "";
			}

		var primerInput = document.getElementById("primerEntry").value;		// Get primers and samples (Newline delimited)
                var sampleInput = document.getElementById("sampleEntry").value;
		var primerArray = primerInput.split("\n");				// Extract primers and samples
                var sampleArray = sampleInput.split("\n");
                var currPosition = 1;

		// Do samples 1-8 (Primer 1)
		// Do samples 1-8 (Primer 2)
		// Do samples 1-8 (Primer 3)
		// Do samples 1-8 (Primer 4)

		var i;
		var j;

		// Samples 1-8 (Primer 1)
		for (i = 0; i < 4; i++) {
			for (j = 0; j < 8; j++) {
				document.getElementById(currPosition+"_a").value = sampleArray[j];      // Write the sample into the layout field
				document.getElementById(currPosition+"_b").value = primerArray[i];      // Write the primer into the layout field
				currPosition += 12;
				if (currPosition > 96) { currPosition -= 95; }
				}
			}

		for (i = 0; i < 4; i++) {
			for (j = 8; j < 16; j++) {
				document.getElementById(currPosition+"_a").value = sampleArray[j];      // Write the sample into the layout field
				document.getElementById(currPosition+"_b").value = primerArray[i];      // Write the primer into the layout field
				currPosition += 12;
				if (currPosition > 96) { currPosition -= 95; }
				}
			}

		for (i = 0; i < 4; i++) {
			for (j = 16; j < 24; j++) {
				document.getElementById(currPosition+"_a").value = sampleArray[j];      // Write the sample into the layout field
				document.getElementById(currPosition+"_b").value = primerArray[i];      // Write the primer into the layout field
				currPosition += 12;
				if (currPosition > 96) { currPosition -= 95; }
				}
			}
		}

	function populate() {
		var selection = document.getElementById("combinatoric").value;
		if (document.getElementsByName('layoutAlignment')[0].checked == true && selection == 'A') populatePrimersOnRows();
		else if (document.getElementsByName('layoutAlignment')[0].checked == true && selection == 'B') populatePrimersOnRowsB();
		else if (document.getElementsByName('layoutAlignment')[1].checked == true && selection == 'A') populatePrimersOnCollumns();
		else if (document.getElementsByName('layoutAlignment')[1].checked == true && selection == 'B') populatePrimersOnCollumnsB();
		else if (document.getElementsByName('layoutAlignment')[2].checked == true) populateSixPrimers();
		else if (document.getElementsByName('layoutAlignment')[3].checked == true) populateFourPrimers();
		}

	function dumpTable() {
		document.getElementById('manualFields').value = "";
		currPosition = 1;

		while(currPosition != 96) {
			i = currPosition;
			if (document.getElementById(i+'_a').value == "" || document.getElementById(i+'_b').value == "")
				document.getElementById('manualFields').value += 'X+X\n';
			else {
				document.getElementById('manualFields').value = document.getElementById('manualFields').value + document.getElementById(i+'_a').value;
				document.getElementById('manualFields').value = document.getElementById('manualFields').value + "+" + document.getElementById(i+'_b').value;
				document.getElementById('manualFields').value = document.getElementById('manualFields').value + '\n';
				}
			if(currPosition <= 84) { currPosition += 12; }
			else { currPosition = currPosition - 83; }
			}
	
		//We are now at position 96 which we have to do manually
	
		if (document.getElementById(96+'_a').value == "" || document.getElementById(96+'_b').value == "" ) {
			document.getElementById('manualFields').value += "X+X\n";
			}
		else {
			document.getElementById('manualFields').value = document.getElementById('manualFields').value + document.getElementById(currPosition+'_a').value;
			document.getElementById('manualFields').value = document.getElementById('manualFields').value + "+" + document.getElementById(currPosition+'_b').value;
			document.getElementById('manualFields').value = document.getElementById('manualFields').value + '\n';
			}


		}

	window.onload = clearFields;
