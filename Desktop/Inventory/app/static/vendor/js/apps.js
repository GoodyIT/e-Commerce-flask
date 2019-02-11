$(function() {
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
    $('#gl_orderTable').DataTable();
    $('#gl_historyTable').DataTable();

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
            gl_uid = result['id'];
            gl_pname = result['product'];
            gl_sku = result['sku'];
            gl_cate = result['category'];
            gl_price = result['price'];
            gl_curr = result['currency'];
            
            gl_attr0 = "";
            gl_attr1 = -1;
            gl_attr2 = -1;
            gl_options0 = "";
            gl_options1 = -1;
            gl_options2 = -1;

            gl_vendor = result['vendor'];
            gl_url = result['url'];
                   
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
            
                //update global variable
                window["gl_attr"+cntAttrs] = key;
                window["gl_options"+cntAttrs] = value;
                
                cntAttrs++;
            });

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

            $("#vendor").val(result['vendor']);
            $("#url").val(result['url']);

            getOrders(pid);
            
        } else {
            console.log("Failed to get Product Info from server!!!");
        }

    });
}
function getOrders(pid) {
    $.ajax({
        url: "/getOrders",
        type: "post",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify({'pid':pid}),
    })
    .done(function(result) {        
        //console.log("------ result: ",result);
        if (result) {
            var htmlTxt = "";
            for (var i=0;i<result.orders.length;i++) {
                item = result.orders[i];
                htmlTxt += '<tr role="row"><td class="sorting_1">'+item.oid+'</td>';
                htmlTxt += '<td>'+item.playerid+'</td>';
                htmlTxt += '<td>'+item.itemid+'</td>';
                htmlTxt += '<td>'+item.qty+'</td>';
                htmlTxt += '<td>'+item.type+'</td>';
                htmlTxt += '<td>'+item.price+'</td>';
                htmlTxt += '<td class="text-center"><button type="button" class="btn btn-primary" id="tbl-btn">X</button></td>';
                htmlTxt += '</tr>';
            }
            $("#gl_orderTable tbody").html(htmlTxt);
            
            getHistory(pid);

        } else {
            console.log("Failed to get Product Info from server!!!");
        }

    });
}

function getHistory(pid) {
    $.ajax({
        url: "/getHistory",
        type: "post",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify({'pid':pid}),
    })
    .done(function(result) {        
        //console.log("------ result: ",result);
        if (result) {
            var htmlTxt = "";
            for (var i=0;i<result.history.length;i++) {
                item = result.history[i];
                htmlTxt += '<tr role="row"><td class="sorting_1">'+item['type']+'</td>';
                htmlTxt += '<td>'+item['date']+'</td>';
                htmlTxt += '<td>'+item['reason']+'</td>';
                htmlTxt += '<td>'+item['adjustments']+'</td>';
                htmlTxt += '<td>'+item['description']+'</td>';
                htmlTxt += '</tr>';
            }
            $("#gl_historyTable tbody").html(htmlTxt);
            
        } else {
            console.log("Failed to get Product Info from server!!!");
        }

    });
}

$("#gl_btnUpdate").on("click", function(){        
    ///// Validation for all form element
    var pname = $("#pname").val();
    var sku = $("#sku").val();
    var cate = $("#cate").val();
    var cateText = $('#cate').find(":selected").text();
    var price = $("#price").val();
    var curr = $("#curr").val();

    var attr0 = "";
    var attr1 = -1;
    var attr2 = -1;
    var options0 = "";
    var options1 = -1;
    var options2 = -1;
    var attr0 = $("#attr0").val();
    var options0 = $("#options0").val();
    if ($("#attr1").length) {
        attr1 = $("#attr1").val();
        options1 = $("#options1").val();
    }
    if ($("#attr2").length) {
        attr2 = $("#attr2").val();
        options2 = $("#options2").val();
    }
    
    var vendor = $("#vendor").val();
    var url = $("#url").val();

    if (pname == "") {
        alert("Please input the Product Name!");
        $("#pname").focus();
        return;
    }
    if (sku == "") {
        alert("Please input the SKU!");
        $("#sku").focus();
        return;
    }
    if (price == "") {
        alert("Please input the Price!");
        $("#price").focus();
        return;
    }
    if (attr0 == "") {
        alert("Please input the Attribute!");
        $("#attr0").focus();
        return;
    }
    if (options0 == "") {
        alert("Please input the Options!");
        $("#options0").focus();
        return;
    }
    if (url == "") {
        alert("Please input the URL!");
        $("#url").focus();
        return;
    }

    /////Check the modifications
    var dicChgs = {}; var dicAttr = {};
    var arrChgs = []; 

    var d = new Date();
    var month = d.getMonth()+1;
    var day = d.getDate();    
    var todayDate = d.getFullYear() + '/' + (month<10 ? '0' : '') + month + '/' + (day<10 ? '0' : '') + day;    

    if (pname != gl_pname) {
        arrChgs.push("Product Name,"+todayDate+","+gl_uid);
        dicChgs['product'] = pname;
    }
    if (sku != gl_sku) {
        arrChgs.push("SKU,"+todayDate+","+gl_uid);
        dicChgs['sku'] = sku;
    }
    if (cate != gl_cate) {
        arrChgs.push("Category,"+todayDate+","+gl_uid);
        dicChgs['category'] = cate;
    }
    if (price != gl_price) {
        arrChgs.push("Price,"+todayDate+","+gl_uid);
        dicChgs['price'] = price;
    }
    if (curr != gl_curr) {
        arrChgs.push("Currency,"+todayDate+","+gl_uid);
        dicChgs['currency'] = curr;
    }
    //console.log("---[",attr0,",",gl_attr0,"] : [",attr1,",",gl_attr1,"] : [",attr2,",",gl_attr2,"] ");
    if (attr0 != gl_attr0) {
        arrChgs.push("Attribute,"+todayDate+","+gl_uid);
        if (options0 != "")
            dicAttr[attr0] = options0;
    }
    if (attr1 != gl_attr1) {
        arrChgs.push("Attribute,"+todayDate+","+gl_uid);
        if (options1 != -1)
            dicAttr[attr1] = options1;
    }
    if (attr2 != gl_attr2) {
        arrChgs.push("Attribute,"+todayDate+","+gl_uid);
        if (options2 != -1)
            dicAttr[attr2] = options2;
    }
    //console.log("---[",options0,",",gl_options0,"] : [",options1,",",gl_options1,"] : [",options2,",",gl_options2,"] ");
    if (options0 != gl_options0) {
        arrChgs.push("Option,"+todayDate+","+gl_uid);
        if (attr0 != "")
            dicAttr[attr0] = options0;
    }
    if (options1 != gl_options1) {
        arrChgs.push("Option,"+todayDate+","+gl_uid);
        if (attr1 != -1)
            dicAttr[attr1] = options1;
    }
    if (options2 != gl_options2) {
        arrChgs.push("Option,"+todayDate+","+gl_uid);
        if (attr2 != -1)
            dicAttr[attr2] = options2;
    }
    if (!jQuery.isEmptyObject(dicAttr)){
        dicChgs['attributes'] = {}; //dicChgs['attributes'] = dicAttr;
        if (attr0 != "") 
            dicChgs['attributes'][attr0] = options0;
        if (attr1 != -1) {
            if (attr1 != "") dicChgs['attributes'][attr1] = options1;
        }
        if (attr2 != -1) {
            if (attr2 != "") dicChgs['attributes'][attr2] = options2;
        }
    }

    if (vendor != gl_vendor) {
        arrChgs.push("Vendor,"+todayDate+","+gl_uid);
        dicChgs['vendor'] = vendor;
    }
    if (url != gl_url) {
        arrChgs.push("Url,"+todayDate+","+gl_uid);
        dicChgs['url'] = url;
    }
    if (arrChgs.length > 0) {
        $.ajax({
            url: "/addHistory",
            type: "post",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({'chgs':arrChgs}),
        })
        .done(function(result) {        
            //console.log("------ result: ",result);
            if (result) {
                var htmlTxt = "";
                /*
                for (var i=0;i<arrChgs.length;i++) {
                    item = arrChgs[i].split(',');
                    htmlTxt += '<tr role="row"><td class="sorting_1">'+item[0]+'</td>';
                    htmlTxt += '<td>'+item[1]+'</td>';
                    htmlTxt += '<td>Item Updated</td>';
                    htmlTxt += '<td>'+item[2]+'</td>';
                    htmlTxt += '<td></td>';
                    htmlTxt += '</tr>';
                }
                */
               for (var i=0;i<result.history.length;i++) {
                    item = result.history[i];
                    htmlTxt += '<tr role="row"><td class="sorting_1">'+item['type']+'</td>';
                    htmlTxt += '<td>'+item['date']+'</td>';
                    htmlTxt += '<td>'+item['reason']+'</td>';
                    htmlTxt += '<td>'+item['adjustments']+'</td>';
                    htmlTxt += '<td>'+item['description']+'</td>';
                    htmlTxt += '</tr>';
                }
                
                $("#gl_historyTable tbody").append(htmlTxt);
                
            } else {
                console.log("Failed to get History Info from server!!!");
            }

        });
    }

    ///// form submission
    if (!jQuery.isEmptyObject(dicChgs)) {
        //$("#frmAdjust").submit(); 
        
        $.ajax({
            url: "/updateProduct",
            type: "post",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({'pid':gl_uid,'item':dicChgs}),
        })
        .done(function(result) {        
            //console.log("------ result: ",result);
            if (result) {
                alert("Success to update product information!");

                if ("category" in dicChgs) {
                    //location.reload();
                    window.location = '/groups/'+cateText;
                    return;
                }

                //Activate the History tab
                $('.nav-tabs a[href="#History"]').tab('show');
                //$('.nav-tabs a:last').tab('show');
                
            } else {
                console.log("Failed to get Product Info from server!!!");
            }
    
        });
    }

});

/// Upload file 
uploadFileImport = function(id) {
    //alert("uploadFileImport - id: "+id);
    $.ajaxFileUpload({
        secureuri: false,
        fileElementId: id,
        dataType: 'json',
        data: {
            'param1': id,
        },
        url: "/importFile", 
        success: function (data, status)
        {
            //console.log("data: ",data);
            if(data.status != 'error')
            {
                //location.reload();
            } else {

            }
        },
        error: function (xhr, status, error) {
            //console.log("xhr: ",xhr);                

        }
    });
}

