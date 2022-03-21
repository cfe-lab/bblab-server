$(document).ready(function(){

	if ($("#userinput").val() != '') {
		$("#clearbutton").removeClass('hide')
	}

	$("#userinput").keyup(function() {
		if ($(this).val() == '') {
			$("#clearbutton").addClass('hide')
		}
		else {
			$("#clearbutton").removeClass('hide')
		}
		text = $(this).val();
		text = text.replace(/[ATCG]/i, '<span class="highlight">$1</span>')
		//console.log($(this).val().length);
		//console.log($(this).val().slice(-1));
	});

	$("#clearbutton").click(function() {
		$("#userinput").val('');
		$("#clearbutton").addClass('hide')
	});

	jQuery.fn.selectText = function(){
		var doc = document
		, element = this[0]
		, range, selection
		;
		if (doc.body.createTextRange) {
			range = document.body.createTextRange();
			range.moveToElementText(element);
			range.select();
		} else if (window.getSelection) {
			selection = window.getSelection();        
			range = document.createRange();
			range.selectNodeContents(element);
			selection.removeAllRanges();
			selection.addRange(range);
		}
	};

	$("#sequencestag").click(function(){
		$('#sequences').selectText();
	});

});
