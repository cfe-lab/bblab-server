$(document).ready(function(){

	//**********************************************************************
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
	});

	$("#clearbutton").click(function() {
		$("#userinput").val('');
		$("#clearbutton").addClass('hide')
	});
	//**********************************************************************

	//**********************************************************************
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

	// This function gets the caret position within an element
	function getCaretCharacterOffsetWithin(element) {
		var caretOffset = 0;
		var doc = element.ownerDocument || element.document;
		var win = doc.defaultView || doc.parentWindow;
		var sel;
		if (typeof win.getSelection != "undefined") {
			var range = win.getSelection().getRangeAt(0);
			var preCaretRange = range.cloneRange();
			preCaretRange.selectNodeContents(element);
			preCaretRange.setEnd(range.endContainer, range.endOffset);
			caretOffset = preCaretRange.toString().length;
		} else if ( (sel = doc.selection) && sel.type != "Control") {
			var textRange = sel.createRange();
			var preCaretTextRange = doc.body.createTextRange();
			preCaretTextRange.moveToElementText(element);
			preCaretTextRange.setEndPoint("EndToEnd", textRange);
			caretOffset = preCaretTextRange.text.length;
		}
		return caretOffset;
	}

	//**********************************************************************

	caret = 0;

	function updateCopy(e) {
		text = e.text();
		matches = text.match(/.{1,3}/gi);
		newtext = '';
		if (matches == null) {$("#copy").html(''); return;}
		if (matches.length > 0) {
			i = 0;
			while (i < matches.length) {
				newmatch = '';
				for (j=0; j < matches[i].length; j++) {
					if (matches[i].charAt(j).match(/[ATCG]/i)) newmatch += '<span class="good">'+matches[i].charAt(j)+'</span>';
					else if (matches[i].charAt(j).match(/[RYKMSWBHDVNX\:\-\*]/i)) newmatch += '<span class="mix">'+matches[i].charAt(j)+'</span>';
					else newmatch += '<span class="bad">'+matches[i].charAt(j)+'</span>';
				}
				matches[i] = newmatch;
				newtext += "<div class=\"codon_wrapper\"><div class=\"codon\">"+matches[i]+"</div><div class=\"numberfloat\">"+(i+1)+"</div></div>";
				i++;
			}
			$("#copy").html(newtext);
		}
	}

	$('#validate').keyup(function() {
		updateCopy($(this));
	});
	

	$('#validate').bind('DOMNodeInserted', function(e) {
		updateCopy($(this));
	});
	
	/*
	$('#validate').click(function() {
		caret = getCaretCharacterOffsetWithin($(this));
		console.log(caret);
	});
	*/
});
