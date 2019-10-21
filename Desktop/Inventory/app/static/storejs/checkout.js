$(document).ready(function() {
	$(".checkout-btn").click(function() {
		var product = [];
		$('#product-list p').each(function (index, value) {
			product.push({
				"product_id": $(this).attr('id'),
				"product_name": $(this).children('a').text(),
				"price": $(this).children('a').attr('id'),
				"quantity": $(this).attr('class')
			});
		});

		var data = {
			"player_id": $("#fname").val(),
			"street": $("#adr").val(),
			"city": $("#city").val(),
			"state": $("#state").val(),
			"zip": $("#zip").val(),
			"products": product
		}

		$.ajax({
	        url: "/makeorder",
	        method: "post",
	        dataType: 'json',
	        contentType: "application/json",
	        data: JSON.stringify(data)
	    })
	    .done(function(res) {
	    	localStorage.removeItem('carts');
	        document.location = '/';
	    });
	});
})