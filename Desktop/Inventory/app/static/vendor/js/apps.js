$(function() {
    // preloader 
    $(function() {
        $(".preloader").fadeOut();
    });

    $('#type-0').css('margin-right', '25px');

    // JS Bootstrap
    $('.dropdown-toggle').dropdown();

    // Dropdown menu
    $('li.dropdown').hover(function() {
        $(this).find('.dropdown-menu').stop(true, true).delay(200).fadeIn(500);
        }, function() {
            $(this).find('.dropdown-menu').stop(true, true).delay(200).fadeOut(500);
        }
    );

    // Tables
    $('#orderTable').DataTable();
    $('#productTable').DataTable();

    // DATEPICKER on Tables
    $( "#datepick" ).datepicker();
    $( "#deliverypick" ).datepicker();

    // Table buttons
    $("#tbl-btn").on("click", function() {
        var item = $(this).closest('tr').find("td:nth-child(1)").text();
        $.ajax({
            url: "/products",
            type: "post",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({'id':item}),
        })
        .done(function() {
            location.reload();
        });
    });

    // Table Add Row
    $(".add-row").on("click", function(){
        // Get Values in Table
        var item_details = $("#item_details").val();
        var league = $("#league").val();
        var quantity = $("#quantity").val();
        var rate = $("#rate").val();
        var tax = $("#tax").val();
        var amount = $("#amount").val();
        var total = $("#tbTotal").text();

        // Update Table
        var markup = "<tr class='add-row'>" +
                    "<td>" + item_details + "</td>" +
                    "<td>" + league + "</td>" +
                    "<td>" + quantity + "</td>" +
                    "<td>" + rate + "</td>" +
                    "<td>" + tax + "</td>" +
                    "<td>" + amount + "</td>" +
                    "<td><button type='button' class='btn btn-primary btnDelete'>Delete</button></td></tr>"
        $("table tbody").append(markup);

        // Erase Values on Table
        $("#item_details").val("");
        $("#league").val("");
        $("#quantity").val("");
        $("#rate").val("");
        $("#tax").val("");
        $("#amount").val("");

        if (tax < 1) {tax=1}
        if (rate < 1) {rate=1}

        // Update Totals
        var rate_cost = rate * quantity;
        var total_cost = rate_cost * amount;
        var tax_cost = total_cost * (tax*.01);
        var final = (total_cost - tax_cost) + parseFloat(total);
        $("#tbTotal").html(final.toFixed(2));
    });

    // Find and remove selected table rows
    $("#tbPurchase").on('click', '.btnDelete', function () {
        // Get Values in Row
        var rquantity = $(this).closest('tr').find("td:nth-child(3)").text();
        var rrate = $(this).closest('tr').find("td:nth-child(4)").text();
        var rtax = $(this).closest('tr').find("td:nth-child(5)").text();
        var ramount = $(this).closest('tr').find("td:nth-child(6)").text();
        var rtotal = $("#tbTotal").text();

        if (rtax < 1) {rtax=1;}
        if (rrate < 1) {rrate=1;}

        // Get Values Before Delete
        var rrate_cost = rrate * rquantity;
        var rtotal_cost = rrate_cost * ramount;
        var rtax_cost = rtotal_cost * (rtax*.01)
        var rfinal = parseFloat(rtotal) - (rtotal_cost - rtax_cost);
        $("#tbTotal").html(rfinal.toFixed(2));


        // Update Totals
        $(this).closest('tr').remove();
    });

    $("#item_discount").change(function() {
        var discount = $("#item_discount").val();
        var current = $("#tbTotal").text();
        $("#tbDiscount").html(discount);
        $("#tbFinal").html(parseFloat(current)-discount).toFixed(2);
    });

    $('#submit').submit(function(e) {

        //prevent Default functionality
        e.preventDefault();

        //get the action-url of the form
        var actionurl = 'localhost:5000/purchase/post'

        //do your own request an handle the results
        $.ajax({
                url: actionurl,
                type: 'post',
                dataType: 'application/json',
                data: $("#submit").serialize(),
                success: function(data) {
                    alert("done!");
                }
        });

    });

    $('#export').on('click', function(e) {

        //prevent Default functionality
        e.preventDefault();
        
        var vendorName = $("#vendor option:selected").text();
        var purchaseOrder = $("#purchase").val();
        var referenceOrder = $("#reference").val();
        var currentDate = $("#datepick").val();
        var deliveryDate = $("#deliverypick").val();
        // ------------- Table --------------- //
        var col = [
            {
                title: "Item Details",
                dataKey: "item_details"
            }, 
            {
                title: "League",
                dataKey: "league"
            }, 
            {
                title: "Quantity",
                dataKey: "quantity"
            }, 
            {
                title: "Rate",
                dataKey: "rate"
            }, 
            {
                title: "Tax",
                dataKey: "tax"
            }, 
            {
                title: "Amount",
                dataKey: "amount"
            }
        ];
        var rows = [];
        $("tbody tr",$("#tbPurchase"))
          .filter(function( index ) {
            return index > 0;
          }).map(function(item, index) { 
            rows.push({
                index           : index,
                item_details    : $("td:eq(0)",this).html(),
                league          : $("td:eq(1)",this).html(),
                quantity        : $("td:eq(2)",this).html(),
                rate            : $("td:eq(3)",this).html(),
                tax             : $("td:eq(4)",this).html(),
                amount          : $("td:eq(5)",this).html(),
            });
        });
        // ----------------------------------- //
        var subTotal = $("#tbTotal").html();
        var discount = $("#tbDiscount").html();
        var final    = $("#tbFinal").html();
        var notes    = $("#notes").val();
        var terms    = $("#terms").val();

        var doc = new jsPDF();
        doc.text(vendorName + "VENDOR NAME HERE", 50, 10);
        doc.line(0,15, 500, 15);
        doc.text("Deliver To", 10, 30);
        doc.text("Johnathan Stevens", 50, 40);
        doc.text("Eloraus, LLC", 50, 50);
        doc.text("5988 Chesbro Ave", 50, 60);
        doc.text("San Jose, CA 95123", 50, 70);
        doc.line(0,75, 500, 75);
        doc.text("Purchase Order #", 10, 90);
        doc.text(purchaseOrder, 60, 90);
        doc.text("Reference Order #", 10, 110);
        doc.text(referenceOrder, 60, 110);
        doc.text("Current Date", 10, 130);
        doc.text(currentDate, 60, 130);
        doc.text("Delivery Date", 100, 130);
        doc.text(deliveryDate, 150, 130);
        doc.autoTable(col, rows, { startX: 50, startY: 150 });
        doc.line(0,185, 300, 185);
        doc.text("Sub Total", 10, 200);
        doc.text(subTotal, 50, 200);
        doc.text("Discount", 10, 210);
        doc.text(discount, 50, 210);
        doc.text("Total", 10, 220);
        doc.text(final, 50, 220);
        doc.text("Note", 10, 230);
        doc.text(notes, 10, 240);
        doc.text("Terms & Conditions", 10, 260);
        doc.text(terms, 10, 270);
        doc.save('invoice.pdf')
    });

    // Queue approve
    $(".que-app").on("click", function() {
        var item = $(this).closest('.row').find("#order_id").html();
        $.ajax({
            url: "/orders",
            type: "post",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({'id':item}),
        })
        .done(function() {
            location.reload();
        });
    });

    // Queue disapprove
    $(".que-dis").on("click", function() {
        var item = $(this).closest('.row').find("#order_id").html();
        $.ajax({
            url: "/queue",
            type: "post",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({'id':item}),
        })
        .done(function() {
            location.reload();
        });
    });

});
