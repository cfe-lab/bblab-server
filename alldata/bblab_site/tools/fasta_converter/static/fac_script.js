$(document).ready(function(){
	$("#datafile").prop('required',true);
	$("#textinput").prop('required',true);

	
	if ($("#textinput").val() != '') {
		$("#clearbutton").removeClass('hide')
	}

	$("#textinput").keyup(function() {
		if ($(this).val() == '') {
			$("#clearbutton").addClass('hide')
		}
		else {
			$("#clearbutton").removeClass('hide')
		}
	});

	$("#clearbutton").click(function() {
		$("#textinput").val('');
		$("#clearbutton").addClass('hide')
	});
	
		
	// This function changes which input fields are required.
	$("button, input[type=submit]").click(function() {
		if ($("#datafile").get(0).files.length === 0 && $("#textinput").val() == ''){
			$("#datafile").prop('required',true);
			$("#textinput").prop('required',true);
		} else {
			$("#datafile").prop('required',false);
			$("#textinput").prop('required',false);
		}
	});
	
	// This function activates and deactivates the "strip whitespace"
	// option when the delimiter is whitespace.
	$("select[name=delim]").change(function() {
		var selection = $(this).children("option:selected").val();
		if (selection === ' ') {
			$("#whitespace-strip").attr('style', 'background-color: #efdfdf; color: #999');
			$("#cboxTwo").prop("disabled", true);	
			$("#cboxTwo").prop("checked", false);	
		} else {
			$("#whitespace-strip").attr('style', 'background-color: #ffe5e5; color: #000');	
			$("#cboxTwo").prop("disabled", false);
			$("#cboxTwo").prop("checked", true);
		}
	});

});

