$(function () {
    
    $.ajax({
        url: "/reports/inventory-sales",
        type: "post"
    })
    .done(function(res) {
        $("#product-sales-report").html('');
        if (res.report.length) {
            res.report.forEach(item => {
                $("#product-sales-report").append(`
                        <div class="col-lg-3"><p>${item.product_name}</p></div>
                        <div class="col-lg-1"><p>SKU</p></div>
                        <div class="col-lg-1"></div>
                        <div class="col-lg-1"><h8>0.1</h8></div>
                        <div class="col-lg-1"></div>
                        <div class="col-lg-1"><h8>${item.quantity}</h8></div>
                        <div class="col-lg-1"></div>
                        <div class="col-lg-1"><h8>${item.quantity*item.price}</h8></div>
                        <div class="col-lg-1"></div>
                        <div class="col-lg-1"><h8>${(0.1*item.quantity*item.price).toFixed(2)}</h8></div>
                `);
            })
        } else {
            $("#product-sales-report").append(`
                <div class="col-lg-5"></div>
                <div class="col-lg-4">
                    <p>No Data To Display</p>
                </div>
                <div class="col-lg-3"></div>
            `);
        }
    });
    $( "#report_order_history_export_csv" ).click(function() {
        
        $.ajax({
            url: "/reports/inventory-sales",
            type: "post"
        })
        .done(function(res) {
            let csvContent = "data:text/csv;charset=utf-8,";
            csvContent += ",PRODUCT NAME,SKU,MARGIN,QTY SOLD,TOTAL SALES,SALES PRICE\r\n";
            res.report.forEach(function(item) {
                csvContent += `,${item.product_name},SKU, 0.1, ${item.quantity}, ${item.quantity*item.price},${(0.1*item.quantity*item.price).toFixed(2)}\r\n`;
            });
            var encodedUri = encodeURI(csvContent);
            var link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "report_product_sales_history.csv");
            document.body.appendChild(link);
            link.click();
        });
    });
    $( "#report_order_history_export_excel" ).click(function() {
        $.ajax({
            url: "/reports/inventory-sales",
            type: "post"
        })
        .done(function(res) {
            var rows = [];
            rows.push(['', 'PRODUCT NAME','SKU','MARGIN','QTY SOLD','TOTAL SALES','SALES PRICE']);
            res.report.forEach(function(item) {
                rows.push([ '', item.product_name, 'SKU', '0.1', item.quantity, item.quantity*item.price, (0.1*item.quantity*item.price).toFixed(2)]);
            });
            var wb = XLSX.utils.book_new();
            wb.SheetNames.push("Order");
            var ws = XLSX.utils.aoa_to_sheet(rows);
            wb.Sheets["Order"] = ws;

            var wbout = XLSX.write(wb, {bookType:'xlsx',  type: 'binary'});
            var buf = new ArrayBuffer(wbout.length); //convert s to arrayBuffer
            var view = new Uint8Array(buf);  //create uint8array as viewer
            for (var i=0; i<wbout.length; i++) view[i] = wbout.charCodeAt(i) & 0xFF;
            saveAs(new Blob([buf],{type:"application/octet-stream"}), 'report_product_sales_history.xlsx');
        });
    });
    $( "#report_order_history_export_doc" ).click(function() {
        $.ajax({
            url: "/reports/inventory-sales",
            type: "post"
        })
        .done(function(res) {
            var preHtml = "<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'><head><meta charset='utf-8'><title>Export HTML To Doc</title></head><body>";
            var postHtml = "</body></html>";
            let docContent = "";
            docContent += `<table>
                <tr>
                    <th>PRODUCT NAME</th>
                    <th>SKU</th>
                    <th>MARGIN</th>
                    <th>QTY SOLD</th>
                    <th>TOTAL SALES</th>
                    <th>SALES PRICE</th>
                </tr>`;
            res.report.forEach(function(item) {
                docContent += `
                    <tr>
                        <td>${item.product_name}</td>
                        <td>SKU</td>
                        <td>0.1</td>
                        <td>${item.quantity}</td>
                        <td>${item.quantity*item.price}</td>
                        <td>${(0.1*item.quantity*item.price).toFixed(2)}</td>
                    </tr>`;
            });
            docContent += '</table>';
            docContent = preHtml + docContent + postHtml;
            var blob = new Blob(['\ufeff', docContent], {
                type: 'application/msword'
            });
            var url = 'data:application/vnd.ms-word;charset=utf-8,' + encodeURIComponent(docContent);
            var downloadLink = document.createElement("a");

            document.body.appendChild(downloadLink);
            
            if(navigator.msSaveOrOpenBlob ){
                navigator.msSaveOrOpenBlob(blob, 'report_product_sales_history.doc');
            }else{
                // Create a link to the file
                downloadLink.href = url;
                
                // Setting the file name
                downloadLink.download = 'report_product_sales_history.doc';
                
                //triggering the function
                downloadLink.click();
            }
            
            document.body.removeChild(downloadLink);
        });
    });
    $( "#report_order_history_export_pdf" ).click(function() {
        $.ajax({
            url: "/reports/inventory-sales",
            type: "post"
        })
        .done(function(res) {
            var col = [
                {
                    title: "PRODUCT NAME",
                    dataKey: "product_id"
                },
                {
                    title: "SKU",
                    dataKey: "sku"
                },
                {
                    title: "MARGIN",
                    dataKey: "margin"
                },
                {
                    title: 'QTY SOLD',
                    dataKey: "qty_sold"
                },
                {
                    title: "TOTAL SALES",
                    dataKey: "total_sales"
                },
                {
                    title: "SALES PRICE",
                    dataKey: "sales_price"
                }
            ];
            rows = [];
            res.report.forEach(function(item, index) {
                rows.push({
                    index           : index + 1,
                    product_id      : item.product_name,
                    sku             : 'SKU',
                    margin          : '0.1',
                    qty_sold        : item.quantity,
                    total_sales     : item.quantity*item.price,
                    sales_price     : (0.1*item.quantity*item.price).toFixed(2),
                });
            });
            var doc = new jsPDF();
            doc.autoTable(col, rows, { startX: 50, startY: 50 });
            doc.save('report_product_sales_history.pdf');
        });
    });
})