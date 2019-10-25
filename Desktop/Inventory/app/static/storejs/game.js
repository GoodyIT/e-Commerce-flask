$(document).ready(function() {
	$('ul.order-list li#price .none').hide();
    var toLoad = localStorage.getItem("accending");
    if (toLoad == 1) {
    	$('ul.order-list li#price a#1').addClass('none');
    	$('ul.order-list li#price a#1').hide();
    	// $('ul.order-list li#price a#1').css('display','none');
    	$('ul.order-list li#price a#-1').removeClass('none');
    	$('ul.order-list li#price a#-1').show();
    	// $('ul.order-list li#price a#-1').css('display','block');
    }
    else if (toLoad == -1) {
    	$('ul.order-list li#price a#-1').addClass('none');
    	$('ul.order-list li#price a#-1').hide();
    	// $('ul.order-list li#price a#-1').css('display','none');
    	$('ul.order-list li#price a#1').removeClass('none');
    	$('ul.order-list li#price a#1').show();
    	// $('ul.order-list li#price a#1').css('display','block');
    }

    $('ul.order-list li#price').click(function() {
    	var toSave = $(this).children('.none').attr('id');
    	localStorage.setItem("accending", toSave);
    });


});