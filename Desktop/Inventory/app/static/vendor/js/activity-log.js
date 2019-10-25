$(function () {
    $( "#activity_log_to_date" ).datepicker();
    $( "#activity_log_from_date" ).datepicker();

    currentDate = new Date();
    $( "#activity_log_from_date" ).datepicker().datepicker("setDate", new Date(currentDate.getYear()+1900, 0, 1));
    $( "#activity_log_to_date" ).datepicker().datepicker("setDate", currentDate);
    
    $( "#report_activity_log_history_apply" ).click(function() {
        var fromDate = new Date($( "#activity_log_from_date" ).val());
        var toDate   = new Date($( "#activity_log_to_date" ).val());
        $.ajax({
            url: "/reports/activity-log",
            type: "post",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                'from'  : fromDate.getFullYear() + '/' + ("0"+(fromDate.getMonth()+1)).slice(-2) + '/' + ("0" + fromDate.getDate()).slice(-2),
                'to'    : toDate.getFullYear() + '/' + ("0"+(toDate.getMonth()+1)).slice(-2) + '/' + ("0" + toDate.getDate()).slice(-2)
            }),
        })
        .done(function(res) {
            console.log(res);
            $("#report-activity-log-content").html('');
            if (res.report.length) {
                res.report.forEach(item => {
                    $("#report-activity-log-content").append(`
                        <div class="col-lg-2"><p>${item.type}</p></div>
                        <div class="col-lg-2"><p>${item.reason}</p></div>
                        <div class="col-lg-2"><p>${item.description}</p></div>
                        <div class="col-lg-1"></div>
                        <div class="col-lg-3"><p>${item.adjustments}</p></div>
                        <div class="col-lg-1"></div>
                        <div class="col-lg-1"><p>${item.date}</p></div></div>
                    `);
                })
            } else {
                $("#report-activity-log-content").append(`
                    <div class="col-lg-5"></div>
                    <div class="col-lg-4">
                        <p>No Data To Display</p>
                    </div>
                    <div class="col-lg-3"></div>
                `);
            }
        });
    });
    $( "#report_activity_log_export_csv" ).click(function() {
        var fromDate = new Date($( "#activity_log_from_date" ).val());
        var toDate   = new Date($( "#activity_log_to_date" ).val());
        $.ajax({
            url: "/reports/activity-log",
            type: "post",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                'from'  : fromDate.getFullYear() + '/' + ("0"+(fromDate.getMonth()+1)).slice(-2) + '/' + ("0" + fromDate.getDate()).slice(-2),
                'to'    : toDate.getFullYear() + '/' + ("0"+(toDate.getMonth()+1)).slice(-2) + '/' + ("0" + toDate.getDate()).slice(-2)
            }),
        })
        .done(function(res) {
            let csvContent = "data:text/csv;charset=utf-8,";
            csvContent += ",TYPE,REASON,DESCRIPTION,ADJUSTMENTS,DATE\r\n";
            res.report.forEach(function(item) {
                csvContent += `,${item.type}, ${item.reason}, ${item.description},${item.adjustments}, ${item.date}\r\n`;
            });
            var encodedUri = encodeURI(csvContent);
            var link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "report_activity_log_export.csv");
            document.body.appendChild(link);
            link.click();
        });
    });
    $( "#report_activity_log_export_excel" ).click(function() {
        var fromDate = new Date($( "#activity_log_from_date" ).val());
        var toDate   = new Date($( "#activity_log_to_date" ).val());
        $.ajax({
            url: "/reports/activity-log",
            type: "post",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                'from'  : fromDate.getFullYear() + '/' + ("0"+(fromDate.getMonth()+1)).slice(-2) + '/' + ("0" + fromDate.getDate()).slice(-2),
                'to'    : toDate.getFullYear() + '/' + ("0"+(toDate.getMonth()+1)).slice(-2) + '/' + ("0" + toDate.getDate()).slice(-2)
            }),
        })
        .done(function(res) {
            var rows = [];
            rows.push(['', 'TYPE','REASON','DESCRIPTION','ADJUSTMENTS','DATE']);
            res.report.forEach(function(item) {
                rows.push([ '', item.type, item.reason, item.description, item.adjustments, item.date]);
            });
            var wb = XLSX.utils.book_new();
            wb.SheetNames.push("Order");
            var ws = XLSX.utils.aoa_to_sheet(rows);
            wb.Sheets["Order"] = ws;

            var wbout = XLSX.write(wb, {bookType:'xlsx',  type: 'binary'});
            var buf = new ArrayBuffer(wbout.length); //convert s to arrayBuffer
            var view = new Uint8Array(buf);  //create uint8array as viewer
            for (var i=0; i<wbout.length; i++) view[i] = wbout.charCodeAt(i) & 0xFF;
            saveAs(new Blob([buf],{type:"application/octet-stream"}), 'report_activity_log.xlsx');
        });
    });
    $( "#report_activity_log_export_doc" ).click(function() {
        var fromDate = new Date($( "#activity_log_from_date" ).val());
        var toDate   = new Date($( "#activity_log_to_date" ).val());
        $.ajax({
            url: "/reports/activity-log",
            type: "post",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                'from'  : fromDate.getFullYear() + '/' + ("0"+(fromDate.getMonth()+1)).slice(-2) + '/' + ("0" + fromDate.getDate()).slice(-2),
                'to'    : toDate.getFullYear() + '/' + ("0"+(toDate.getMonth()+1)).slice(-2) + '/' + ("0" + toDate.getDate()).slice(-2)
            }),
        })
        .done(function(res) {
            var preHtml = "<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'><head><meta charset='utf-8'><title>Export HTML To Doc</title></head><body>";
            var postHtml = "</body></html>";
            let docContent = "";
            docContent += `<table>
                <tr>
                    <th>TYPE</th>
                    <th>REASON</th>
                    <th>DESCRIPTION</th>
                    <th>ADJUSTMENTS</th>
                    <th>DATE</th>
                </tr>`;
            res.report.forEach(function(item) {
                docContent += `
                    <tr>
                        <td>${item.type}</td>
                        <td>${item.reason}</td>
                        <td>${item.description}</td>
                        <td>${item.adjustments}</td>
                        <td>${item.date}</td>
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
                navigator.msSaveOrOpenBlob(blob, 'report_activity_log.doc');
            }else{
                // Create a link to the file
                downloadLink.href = url;
                
                // Setting the file name
                downloadLink.download = 'report_activity_log.doc';
                
                //triggering the function
                downloadLink.click();
            }
            
            document.body.removeChild(downloadLink);
        });
    });
    $( "#report_activity_log_export_pdf" ).click(function() {
        var fromDate = new Date($( "#activity_log_from_date" ).val());
        var toDate   = new Date($( "#activity_log_to_date" ).val());
        $.ajax({
            url: "/reports/activity-log",
            type: "post",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                'from'  : fromDate.getFullYear() + '/' + ("0"+(fromDate.getMonth()+1)).slice(-2) + '/' + ("0" + fromDate.getDate()).slice(-2),
                'to'    : toDate.getFullYear() + '/' + ("0"+(toDate.getMonth()+1)).slice(-2) + '/' + ("0" + toDate.getDate()).slice(-2)
            }),
        })
        .done(function(res) {
            var col = [
                {
                    title: "TYPE",
                    dataKey: "type"
                },
                {
                    title: "REASON",
                    dataKey: "reason"
                },
                {
                    title: "DESCRIPTION",
                    dataKey: "description"
                },
                {
                    title: 'ADJUSTMENTS',
                    dataKey: "adjustments"
                },
                {
                    title: "DATE",
                    dataKey: "date"
                }
            ];
            rows = [];
            res.report.forEach(function(item, index) {
                rows.push({
                    type            : item.type,
                    reason             : item.reason,
                    description          : item.description,
                    adjustments        : item.adjustments,
                    date     : item.date,
                });
            });
            var doc = new jsPDF();
            doc.autoTable(col, rows, { startX: 50, startY: 50 });
            doc.save('report_activity_log.pdf');
        });
    });
})