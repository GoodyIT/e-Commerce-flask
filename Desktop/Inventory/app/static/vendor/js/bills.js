$(function() {
    $( "#bills_datepick" ).datepicker();
    $( "#bills_deliverypick" ).datepicker();
    var hulla = new hullabaloo();
    $("#bills_add_row").on("click", function(){
        // Get Values in Table
        var item_details = $("#bills_item_details").val();
        var league = $("#bills_league").val();
        var quantity = $("#bills_quantity").val();
        var rate = $("#bills_rate").val();
        var tax = $("#bills_tax").val();
        var amount = $("#bills_amount").val();
        var total = $("#bills_tbTotal").text();
        var finaltotal = $("#bills_tbFinal").text();

        var validate = true;
        if (item_details == "" || quantity <=0 || amount <=0) {
            validate = false;
            hulla.send("Insert data into the form", "warning");
        }

        if (validate) {
            var markup = "<tr class='add-row'>" +
                    "<td>" + item_details + "</td>" +
                    "<td>" + league + "</td>" +
                    "<td>" + quantity + "</td>" +
                    "<td>" + rate + "</td>" +
                    "<td>" + tax + "</td>" +
                    "<td>" + amount + "</td>" +
                    "<td style='border: none;'><button type='button' class='btn btn-primary btnDelete'>Delete</button></td></tr>"
            $("table#bills_tbPurchase tbody").append(markup);
            // $("table tbody").append(markup);

            var rows = [];
            $("tbody tr",$("#bills_tbPurchase"))
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

            // Erase Values on Table
            $("#bills_item_details").val("");
            $("#bills_league").val("");
            $("#bills_quantity").val("");
            $("#bills_rate").val("");
            $("#bills_tax").val("");
            $("#bills_amount").val("");

            if (tax < 1) {tax=1}
            if (rate < 1) {rate=1}

            // Update Totals
            var rate_cost = rate * quantity;
            var total_cost = rate_cost * amount;
            var tax_cost = total_cost * (tax*.01);
            var final = (total_cost - tax_cost) + parseFloat(total);
            var finalresult = (total_cost - tax_cost) + parseFloat(finaltotal);
            $("#bills_tbTotal").html(final.toFixed(2));
            $("#bills_tbFinal").html(finalresult.toFixed(2));
        }
        
    });

    // Find and remove selected table rows
    $("#bills_tbPurchase").on('click', '.btnDelete', function () {
        // Get Values in Row
        var rquantity = $(this).closest('tr').find("td:nth-child(3)").text();
        var rrate = $(this).closest('tr').find("td:nth-child(4)").text();
        var rtax = $(this).closest('tr').find("td:nth-child(5)").text();
        var ramount = $(this).closest('tr').find("td:nth-child(6)").text();
        var rtotal = $("#bills_tbTotal").text();
        var rfinaltotal = $("#bills_tbFinal").text();

        if (rtax < 1) {rtax=1;}
        if (rrate < 1) {rrate=1;}

        // Get Values Before Delete
        var rrate_cost = rrate * rquantity;
        var rtotal_cost = rrate_cost * ramount;
        var rtax_cost = rtotal_cost * (rtax*.01)
        var rfinal = parseFloat(rtotal) - (rtotal_cost - rtax_cost);
        var rfinalresult = parseFloat(rfinaltotal) - (rtotal_cost - rtax_cost);
        $("#bills_tbTotal").html(rfinal.toFixed(2));
        $("#bills_tbFinal").html(rfinalresult.toFixed(2));

        // Update Totals
        $(this).closest('tr').remove();

        var rows = [];
        $("tbody tr",$("#bills_tbPurchase"))
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
    });

    $("#bills_item_discount").change(function() {
        var discount = $("#bills_item_discount").val();
        var current = $("#bills_tbTotal").text();
        $("#bills_tbDiscount").html(discount);
        $("#bills_tbFinal").html((parseFloat(current)-discount).toFixed(2));
    });

    function createPDF(image) {
        var currentDate = $("#bills_datepick").val();
        var deliveryDate = $("#bills_deliverypick").val();
        var balance = $("#bills_balance").text();
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
        $("tbody tr",$("#bills_tbPurchase"))
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
        var subTotal = $("#bills_tbTotal").html();
        var discount = $("#bills_tbDiscount").html();
        var final    = $("#bills_tbFinal").html();
        var notes    = $("#bills_notes").val();
        var terms    = $("#bills_terms").val();

        var doc = new jsPDF();
        if (image) {
            doc.addImage(image.data, image.extension, 17, 20, 35*image.ratio>70? 70: 35*image.ratio, 35*image.ratio>70? 70/image.ratio: 35);
        }
        doc.setFontSize(12);
        doc.text("Current Date", 120, 30);
        doc.text(currentDate, 160, 30);
        doc.text("Delivery Date", 120, 40);
        doc.text(deliveryDate, 160, 40);
        doc.setFillColor(245,245,245);
        doc.rect(115, 44, 81, 9, 'F');
        doc.text("Balance", 120, 50);
        doc.text(balance, 160, 50);
        doc.autoTable(col, rows, { startX: 50, startY: 60 });
        doc.text("Sub Total", 120, 190);
        doc.text(subTotal, 160, 190);
        doc.text("Discount", 120, 200);
        doc.text(discount, 160, 200);
        doc.setDrawColor(0);
        doc.line(120, 203, 196, 203);
        doc.text("Total", 120, 210);
        doc.text(final, 160, 210);
        doc.text("Note", 10, 230);
        doc.text(notes, 10, 237);
        doc.text("Terms & Conditions", 10, 250);
        doc.text(terms, 10, 257);
        doc.save('bills.pdf');
    }

    $('#bills_export_to_pdf').on('click', function(e) {
        //prevent Default functionality
        e.preventDefault();
        var imageUrl = $('#logo_file').val();
        if ( imageUrl )
        {
            var strArray = imageUrl.split('.');
            var extension = strArray[strArray.length - 1];
            
            var img = new Image, data;
	
            img.onError = function() {
                throw new Error('Cannot load image: "'+imageUrl+'"');
            }
            img.onload = function() {
                var canvas = document.createElement('canvas');
                document.body.appendChild(canvas);
                canvas.width = img.width;
                canvas.height = img.height;

                var ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                // Grab the image as a jpeg encoded in base64, but only the data
                data = canvas.toDataURL(`image/${extension}`).slice(`data:image/${extension};base64,`.length);
                // Convert the data to binary form
                document.body.removeChild(canvas);
                createPDF({data: data, extension: extension, ratio: img.width/img.height}); 
            }
            img.src = imageUrl;
        } else {
            createPDF();
        }
    });

    $('#bills_export_to_csv').on('click', function(e) {
        var currentDate = $("#bills_datepick").val();
        var deliveryDate = $("#bills_deliverypick").val();
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
            "Billing date",
            "Delivery date"
        ]];

        $("tbody tr",$("#bills_tbPurchase"))
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
                currentDate,
                deliveryDate
            ]);
        });
        
        // ----------------------------------- //
        let csvContent = "data:text/csv;charset=utf-8,";

        rows.forEach(function(rowArray){
            let row = `,` + rowArray.join(",");
            csvContent += row + "\r\n";
        });
        var encodedUri = encodeURI(csvContent);
        var link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "bills.csv");
        document.body.appendChild(link);
        link.click();
    });
    $('#bills_export_to_excel').on('click', function(e) {

        //prevent Default functionality
        e.preventDefault();

        var currentDate = $("#bills_datepick").val();
        var deliveryDate = $("#bills_deliverypick").val();

        var rows = [];
        
        rows.push(['', 'Item Details', 'League', 'Quantity', 'Rate', 'Tax', 'Amount', 'Billing Date', 'Delivery Date']);
        $("tbody tr",$("#bills_tbPurchase"))
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
                currentDate,
                deliveryDate
            ]);
        });
        // ----------------------------------- //

        var wb = XLSX.utils.book_new();
        wb.SheetNames.push("Order");
        var ws = XLSX.utils.aoa_to_sheet(rows);
        wb.Sheets["Order"] = ws;

        var wbout = XLSX.write(wb, {bookType:'xlsx',  type: 'binary'});
        var buf = new ArrayBuffer(wbout.length); //convert s to arrayBuffer
        var view = new Uint8Array(buf);  //create uint8array as viewer
        for (var i=0; i<wbout.length; i++) view[i] = wbout.charCodeAt(i) & 0xFF;
        saveAs(new Blob([buf],{type:"application/octet-stream"}), 'bills.xlsx');
    });
})