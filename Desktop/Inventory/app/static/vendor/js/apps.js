$(function() {

    $('#shipping-items').paginate({itemsPerPage: 4});

    var groupName = $('#groupName').html();
    $('#groupName').hide();
    
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

        var rows = [];
        $("tbody tr",$("#tbPurchase"))
          .filter(function( index ) {
            return index > 0;
          }).map(function(index) {
            rows.push([
                $("td:eq(0)",this).html(),
                $("td:eq(1)",this).html(),
                $("td:eq(2)",this).html(),
                $("td:eq(3)",this).html(),
                $("td:eq(4)",this).html(),
                $("td:eq(5)",this).html()
            ]);
        });

        $("#orders").val(rows.toString());

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

        var rows = [];
        $("tbody tr",$("#tbPurchase"))
          .filter(function( index ) {
            return index > 0;
          }).map(function(index) {
            rows.push([
                $("td:eq(0)",this).html(),
                $("td:eq(1)",this).html(),
                $("td:eq(2)",this).html(),
                $("td:eq(3)",this).html(),
                $("td:eq(4)",this).html(),
                $("td:eq(5)",this).html()
            ]);
        });
        $("#orders").val(rows.toString());
    });

    $("#item_discount").change(function() {
        var discount = $("#item_discount").val();
        var current = $("#tbTotal").text();
        $("#tbDiscount").html(discount);
        $("#tbFinal").html(parseFloat(current)-discount).toFixed(2);
    });

    $('#export_to_pdf').on('click', function(e) {

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
          }).map(function(index) {
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
        doc.save('invoice.pdf');
    });

    $('#export_to_csv').on('click', function(e) {
        var vendorName = $("#vendor option:selected").text();
        var purchaseOrder = $("#purchase").val();
        var referenceOrder = $("#reference").val();
        var currentDate = $("#datepick").val();
        var deliveryDate = $("#deliverypick").val();
        //prevent Default functionality
        e.preventDefault();
        var rows = [[
            "",
            "Item Details",
            "League",
            "Quantity",
            "Rate",
            "Tax",
            "Amount",
            "Vendor Name",
            "Purchase Order",
            "Reference Order",
            "Current Date",
            "Delivery Date"
        ]];

        $("tbody tr",$("#tbPurchase"))
          .filter(function( index ) {
            return index > 0;
          }).map(function(index) {
            rows.push([
                index+1,
                $("td:eq(0)",this).html(),
                $("td:eq(1)",this).html(),
                $("td:eq(2)",this).html(),
                $("td:eq(3)",this).html(),
                $("td:eq(4)",this).html(),
                $("td:eq(5)",this).html(),
                vendorName,
                purchaseOrder,
                referenceOrder,
                currentDate,
                deliveryDate
            ]);
        });

        var subTotal = $("#tbTotal").html();
        var discount = $("#tbDiscount").html();
        var final    = $("#tbFinal").html();
        var notes    = $("#notes").val();
        var terms    = $("#terms").val();
        // ----------------------------------- //
        let csvContent = "data:text/csv;charset=utf-8,";

        rows.forEach(function(rowArray){
            let row = `,` + rowArray.join(",");
            csvContent += row + "\r\n";
        });
        csvContent += '\r\n';
        csvContent += `, , Sub Total, ${subTotal}\r\n`;
        csvContent += `, , Discount, ${discount}\r\n`;
        csvContent += `, , Total, ${final}\r\n`;
        csvContent += `, , Notes, ${notes}\r\n`;
        csvContent += `, , Terms & Conditions, ${terms}\r\n`;
        var encodedUri = encodeURI(csvContent);
        var link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "order.csv");
        document.body.appendChild(link);
        link.click();
    });
    $('#export_to_excel').on('click', function(e) {

        //prevent Default functionality
        e.preventDefault();

        var vendorName = $("#vendor option:selected").text();
        var purchaseOrder = $("#purchase").val();
        var referenceOrder = $("#reference").val();
        var currentDate = $("#datepick").val();
        var deliveryDate = $("#deliverypick").val();

        var rows = [];
        rows.push(['Vendor Name', vendorName]);
        rows.push([]);
        rows.push(['Deliver to']);
        rows.push(['', 'Johnathan Stevens']);
        rows.push(['', 'Eloraus, LLC']);
        rows.push(['', '5988 Chesbro Ave']);
        rows.push(['', 'San Jose, CA 95123']);
        rows.push([]);
        rows.push(['Purchase Order#', purchaseOrder]);
        rows.push(['Reference Order#', referenceOrder]);
        rows.push(['Current Date', currentDate, '', 'Delivery Date', deliveryDate]);
        rows.push([]);
        rows.push(['', 'Item Details', 'League', 'Quantity', 'Rate', 'Tax', 'Amount']);
        $("tbody tr",$("#tbPurchase"))
          .filter(function( index ) {
            return index > 0;
          }).map(function(index) {
            rows.push([
                index+1,
                $("td:eq(0)",this).html(),
                $("td:eq(1)",this).html(),
                $("td:eq(2)",this).html(),
                $("td:eq(3)",this).html(),
                $("td:eq(4)",this).html(),
                $("td:eq(5)",this).html()
            ]);
        });
        rows.push([]);

        var subTotal = $("#tbTotal").html();
        var discount = $("#tbDiscount").html();
        var final    = $("#tbFinal").html();
        var notes    = $("#notes").val();
        var terms    = $("#terms").val();
        rows.push(['Sub Total', subTotal]);
        rows.push(['Discount', discount]);
        rows.push(['Total', final]);
        rows.push(['Notes', notes]);
        rows.push(['Terms & Conditions', terms]);
        // ----------------------------------- //

        var wb = XLSX.utils.book_new();
        wb.SheetNames.push("Order");
        var ws = XLSX.utils.aoa_to_sheet(rows);
        wb.Sheets["Order"] = ws;

        var wbout = XLSX.write(wb, {bookType:'xlsx',  type: 'binary'});
        var buf = new ArrayBuffer(wbout.length); //convert s to arrayBuffer
        var view = new Uint8Array(buf);  //create uint8array as viewer
        for (var i=0; i<wbout.length; i++) view[i] = wbout.charCodeAt(i) & 0xFF;
        saveAs(new Blob([buf],{type:"application/octet-stream"}), 'order.xlsx');
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

    $("#analytics_by_date_type").on('change', function () {
        $("#analytics_by_date").remove();
        $("#analytics_by_date_container").append('<canvas id="analytics_by_date"></canvas>');
        switch($("#analytics_by_date_type").val()) {
            case 'by_daily':
                $.ajax({
                    url: "/analytics",
                    type: "post",
                    dataType: "json",
                    contentType: "application/json",
                    data: JSON.stringify({'type': 'by_daily'}),
                })
                .done(function(res) {
                    labelArray = [];
                    dataArray  = [];
                    res.analyticsByDaily.forEach(value => {
                        labelArray.push(value['_id']['year'] + "." + value['_id']['day']);
                        dataArray.push(value['quantity']);
                    });
                    var ctxAnalyticsByDaily = document.getElementById("analytics_by_date").getContext('2d');
                    new Chart(ctxAnalyticsByDaily, {
                        type: 'bar',
                        data: {
                            labels: labelArray,
                            datasets: [{
                                label: 'Analytics By Date',
                                data: dataArray,
                                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                                borderColor: 'rgba(255,99,132,1)',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            scales: {
                                yAxes: [{
                                    ticks: {
                                        beginAtZero:true
                                    }
                                }]
                            }
                        }
                    });
                });
                break;
            case 'by_weekly':
                $.ajax({
                    url: "/analytics",
                    type: "post",
                    dataType: "json",
                    contentType: "application/json",
                    data: JSON.stringify({'type': 'by_weekly'}),
                })
                .done(function(res) {
                    labelArray = [];
                    dataArray  = [];
                    res.analyticsByWeekly.forEach(value => {
                        labelArray.push(value['_id']['year'] + "." + value['_id']['week']);
                        dataArray.push(value['quantity']);
                    });
                    var ctxAnalyticsByWeekly = document.getElementById("analytics_by_date").getContext('2d');
                    new Chart(ctxAnalyticsByWeekly, {
                        type: 'bar',
                        data: {
                            labels: labelArray,
                            datasets: [{
                                label: 'Analytics By Date',
                                data: dataArray,
                                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                                borderColor: 'rgba(255,99,132,1)',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            scales: {
                                yAxes: [{
                                    ticks: {
                                        beginAtZero:true
                                    }
                                }]
                            }
                        }
                    });
                });
                break;
            case 'by_monthly':
                $.ajax({
                    url: "/analytics",
                    type: "post",
                    dataType: "json",
                    contentType: "application/json",
                    data: JSON.stringify({'type': 'by_monthly'}),
                })
                .done(function(res) {
                    labelArray = [];
                    dataArray  = [];
                    res.analyticsByMonthly.forEach(value => {
                        labelArray.push(value['_id']['year'] + "." + value['_id']['month']);
                        dataArray.push(value['quantity']);
                    });
                    var ctxAnalyticsByMonthly = document.getElementById("analytics_by_date").getContext('2d');
                    new Chart(ctxAnalyticsByMonthly, {
                        type: 'bar',
                        data: {
                            labels: labelArray,
                            datasets: [{
                                label: 'Analytics By Date',
                                data: dataArray,
                                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                                borderColor: 'rgba(255,99,132,1)',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            scales: {
                                yAxes: [{
                                    ticks: {
                                        beginAtZero:true
                                    }
                                }]
                            }
                        }
                    });
                });
                break;
            case 'by_yearly':
                $.ajax({
                    url: "/analytics",
                    type: "post",
                    dataType: "json",
                    contentType: "application/json",
                    data: JSON.stringify({'type': 'by_yearly'}),
                })
                .done(function(res) {
                    labelArray = [];
                    dataArray  = [];
                    res.analyticsByYearly.forEach(value => {
                        labelArray.push(value['_id']['year']);
                        dataArray.push(value['quantity']);
                    });
                    var ctxAnalyticsByYearly = document.getElementById("analytics_by_date").getContext('2d');
                    new Chart(ctxAnalyticsByYearly, {
                        type: 'bar',
                        data: {
                            labels: labelArray,
                            datasets: [{
                                label: 'Analytics By Date',
                                data: dataArray,
                                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                                borderColor: 'rgba(255,99,132,1)',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            scales: {
                                yAxes: [{
                                    ticks: {
                                        beginAtZero:true
                                    }
                                }]
                            }
                        }
                    });
                });
                break;
        }
    })

    $("#analytics_by_location_type").on('change', function () {
        $("#analytics_by_location").remove();
        $("#analytics_by_location_container").append('<canvas id="analytics_by_location"></canvas>');
        switch($("#analytics_by_location_type").val()) {
            case 'by_city':
                break;
            case 'by_state':
                $.ajax({
                    url: "/analytics",
                    type: "post",
                    dataType: "json",
                    contentType: "application/json",
                    data: JSON.stringify({'type': 'by_state'}),
                })
                .done(function(res) {
                    var labelArray = [];
                    var dataArray  = [];
                    labelArray = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", 
                    "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", 
                    "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", 
                    "VA", "WA", "WV", "WI", "WY"];
                    var dataJson = {};
                    res.analyticsByState.forEach(value => {
                        dataJson[value["_id"]] = value["quantity"];
                    });
                    dataArray = labelArray.map(state => {
                        if (dataJson[state])
                            return dataJson[state];
                        return 0;
                    });
                    
                    var ctxAnalyticsByLocation = document.getElementById("analytics_by_location").getContext('2d');
                    new Chart(ctxAnalyticsByLocation, {
                        type: 'bar',
                        data: {
                            labels: labelArray,
                            datasets: [{
                                label: 'Analytics By Location',
                                data: dataArray,
                                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                                borderColor: 'rgba(255,99,132,1)',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            scales: {
                                yAxes: [{
                                    ticks: {
                                        beginAtZero:true
                                    }
                                }]
                            }
                        }
                    });
                });
                break;
            case 'by_country':
                $.ajax({
                    url: "/analytics",
                    type: "post",
                    dataType: "json",
                    contentType: "application/json",
                    data: JSON.stringify({'type': 'by_country'}),
                })
                .done(function(res) {
                    var labelArray = [];
                    var dataArray  = [];
                    res.analyticsByCountry.forEach(value => {
                        labelArray.push(value['_id']);
                        dataArray.push(value['quantity']);
                    });
                    
                    var ctxAnalyticsByLocation = document.getElementById("analytics_by_location").getContext('2d');
                    new Chart(ctxAnalyticsByLocation, {
                        type: 'bar',
                        data: {
                            labels: labelArray,
                            datasets: [{
                                label: 'Analytics By Location',
                                data: dataArray,
                                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                                borderColor: 'rgba(255,99,132,1)',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            scales: {
                                yAxes: [{
                                    ticks: {
                                        beginAtZero:true
                                    }
                                }]
                            }
                        }
                    });
                });
                break;
        }
    })
    //////////////////////////////////////////////////////////////////////////////
    ////// Added By XLZ
    var cntAttrs = 0;
    $("#btnAddAttr").on("click", function(){
        for(var i=1; i<6; i++) {
            cntAttrs++;
            if (!$("#attr"+cntAttrs).length) break;
            if (cntAttrs == 5) return;
        }

        var htmlAddAttr = '<div class="row" style="margin-top:10px;">'+
                        '<div class="col-lg-3"><label for="attr'+cntAttrs+'">Attribute</label><input type="text" class="form-control" id="attr'+cntAttrs+'" name="attr'+cntAttrs+'" placeholder="eg:color"></div>'+
                        '<div class="col-lg-5"><label for="options'+cntAttrs+'">Options</label><input type="text" class="form-control" id="options'+cntAttrs+'" name="options'+cntAttrs+'" data-role="tagsinput" placeholder=""></div>'+
                        '</div>';
        $("div#dvAttr").append(htmlAddAttr);

        // Erase Values on Table
        $("#attr"+cntAttrs).val("");
        $("#options"+cntAttrs).tagsinput();

    });

    ////// Upload image drag&drop
    Dropzone.autoDiscover = false;
    Dropzone.options.frmDropZone = {
        paramName: "photos", // The name that will be used to transfer the file
        acceptedFiles: '.jpg, .jpeg, .png, .gif',
        maxFilesize: 2, // MB
    }
    jQuery(".dropzone").dropzone({
        success : function(file, response) {
            //console.log(file);
            //console.log("------response: ",response);
            if (response['target_file'] != '') {
                var currentValue = jQuery("#hdfiles").val(); //jQuery("#frmNP input[name='hdfiles'").val();
                if (currentValue == '') {
                    jQuery("#hdfiles").val(response['target_file']);
                } else {
                    jQuery("#hdfiles").val(currentValue + "," + response['target_file']);
                }
            }
        }
    });

    function getProduct(pid) {
        $.ajax({
            url: "/getProduct",
            type: "post",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({'pid':pid}),
        })
        .done(function(result) {
            //location.reload();
            if (result) {
                $("#pid").val(result['id']);
                $("#pname").val(result['product']);
                $("#ptitle").text(result['product']);
                $("#sku").val(result['sku']);
                $("#cate").val(result['category']).change();

                $("#price").val(result['price']);
                $("#curr").val(result['currency']);

                var attrs = result['attributes'];
                //console.log("------> attrs: ", attrs);
                var cntAttrs = 0;
                $("div#dvAttr").html('');
                $.each(attrs, function(key,value) {
                    var htmlAddAttr = '<div class="row" style="margin-top:10px;">'+
                        '<div class="col-lg-3"><label for="attr'+cntAttrs+'">Attribute</label><input type="text" class="form-control" id="attr'+cntAttrs+'" name="attr'+cntAttrs+'" placeholder="eg:color" value="'+key+'"></div>'+
                        '<div class="col-lg-5"><label for="options'+cntAttrs+'">Options</label><input type="text" class="form-control" id="options'+cntAttrs+'" name="options'+cntAttrs+'" data-role="tagsinput" placeholder="" value="'+value+'"></div>';
                    if (cntAttrs == 0) {
                        htmlAddAttr += ' <div class="col-lg-3" style="margin-top: 25px;"><button type="button" id="btnAddAttr" class="btn btn-link">+Add more attribute</button></div>';
                    }
                    htmlAddAttr += '</div>';
                    $("div#dvAttr").append(htmlAddAttr);

                    $("#attr"+cntAttrs).val(key);
                    $("#options"+cntAttrs).val(value);
                    $("#options"+cntAttrs).tagsinput();
                    cntAttrs++;
                });

                $("#vendor").val(result['vendor']);
                $("#url").val(result['url']);

            } else {
                console.log("Failed to get Product Info from server!!!");
            }

        });
    }
})

function initDashboard() {
    $.ajax({
        url: "/analytics",
        type: "post",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify({'type': 'init'}),
    })
    .done(function(res) {
        $("#analytics_total_order").html(res.totalQuantity);
        $("#analytics_total_price").html(res.totalCost);
        $("#analytics_packed_order_count").html(res.packedOrderCount);
        $("#analytics_shipped_order_count").html(res.shippedOrderCount);
        $("#analytics_delivered_order_count").html(res.deliveredOrderCount);
        $("#analytics_invoiced_order_count").html(res.invoicedOrderCount);

        // Analytics by location
        var labelArray = [];
        var dataArray  = [];
        labelArray = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", 
          "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", 
          "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", 
          "VA", "WA", "WV", "WI", "WY"];
        var dataJson = {};
        res.analyticsByState.forEach(value => {
            dataJson[value["_id"]] = value["quantity"];
        });
        dataArray = labelArray.map(state => {
            if (dataJson[state])
                return dataJson[state];
            return 0;
        });
        
        var ctxAnalyticsByLocation = document.getElementById("analytics_by_location").getContext('2d');
        new Chart(ctxAnalyticsByLocation, {
            type: 'bar',
            data: {
                labels: labelArray,
                datasets: [{
                    label: 'Analytics By Location',
                    data: dataArray,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255,99,132,1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero:true
                        }
                    }]
                }
            }
        });

        // Analytics by group
        labelArray = [];
        dataArray  = [];
        res.analyticsByGroup.forEach(value => {
            labelArray.push(value['group']);
            dataArray.push(value['quantity']);
        });
        
        var ctxAnalyticsByGroup = document.getElementById("analytics_by_group").getContext('2d');
        new Chart(ctxAnalyticsByGroup, {
            type: 'bar',
            data: {
                labels: labelArray,
                datasets: [{
                    label: 'Analytics By Group',
                    data: dataArray,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255,99,132,1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero:true
                        }
                    }]
                }
            }
        });

        // Analytics by date
        labelArray = [];
        dataArray  = [];

        res.analyticsByYearly.forEach(value => {
            labelArray.push(value['_id']['year']);
            dataArray.push(value['quantity']);
        });
        var ctxAnalyticsByYearly = document.getElementById("analytics_by_date").getContext('2d');
        new Chart(ctxAnalyticsByYearly, {
            type: 'bar',
            data: {
                labels: labelArray,
                datasets: [{
                    label: 'Analytics By Date',
                    data: dataArray,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255,99,132,1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero:true
                        }
                    }]
                }
            }
        });
    });
}