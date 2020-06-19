$(document).ready(function working_hours() {
        $('[data-toggle="tooltip"]').tooltip({ trigger: 'click' });
        $('[data-toggle="time_diff"]').tooltip({ trigger: 'focus hover' });
        $('[data-toggle="zero_extra_hours"]').tooltip({ trigger: 'focus hover' });
        $('[data-toggle="accept_entry"]').tooltip({ trigger: 'focus hover' });

        var sum_hours = 0;
        var sum_extra_hours = 0;
        var sum_minutes = 0;
        var sum_extra_minutes = 0;
            var tableElem = document.getElementById("table");
            var tableBody = tableElem.getElementsByTagName("tbody").item(0);
            var howManyRows = tableBody.rows.length;
            for (var i = 0; i < howManyRows; i++) {
                var thisTrElem = tableBody.rows[i];
                var thisTdElem = thisTrElem.cells[2];
                var thisTdElem_2 = thisTrElem.cells[3];
                var thisTextNode;
                var thisTextNode_2;
                if (thisTrElem.cells[4].childNodes.item(0).nodeValue === 'tak' &&
                    thisTrElem.cells[5].childNodes.item(0).nodeValue >= 'nie') {
                    thisTextNode = thisTdElem.childNodes.item(0).nodeValue;
                    thisTextNode_2 = thisTdElem_2.childNodes.item(0).nodeValue;
                }
                else {
                    thisTextNode = '0:0';
                    thisTextNode_2 = '0:0';
                }
                var hours = Number(thisTextNode.split(":", 2)[0]);
                var extra_hours = Number(thisTextNode_2.split(":", 2)[0]);
                var minutes = Number(thisTextNode.split(":", 2)[1]);
                var extra_minutes = Number(thisTextNode_2.split(":", 2)[1]);
                if (!isNaN(hours) && !isNaN(minutes)) {
                       sum_hours += hours;
                       sum_extra_hours += extra_hours;
                       sum_minutes += minutes;
                       sum_extra_minutes += extra_minutes;
                       var realmin = sum_minutes % 60;
                       var realmin_extra = sum_extra_minutes % 60;
                       var hours_from_mins = Math.floor(sum_minutes / 60);
                       var hours_from_extra_mins = Math.floor(sum_extra_minutes / 60);
                   }
                var result = Number(sum_hours+hours_from_mins) + ":" + (realmin < 9 ? '0' + realmin : realmin);
                var result_extra = Number(sum_extra_hours+hours_from_extra_mins) + ":" + (realmin_extra < 9 ? '0' + realmin_extra : realmin_extra);
               }
                document.querySelector('#result').innerHTML = result;
                document.querySelector('#result_extra').innerHTML = result_extra;
    });


$(document).ready(function holiday() {
    var tableElem = document.getElementById("table");
            var tableBody = tableElem.getElementsByTagName("tbody").item(0);
            var howManyRows = tableBody.rows.length;
            for (var i = 0; i < howManyRows; i++) {
                var thisTrElem = tableBody.rows[i];
                if (thisTrElem.cells[0].childNodes.item(0).nodeValue.includes("Sobota")) {

                    thisTrElem.style.color = "blue"
                }
                if (thisTrElem.cells[0].childNodes.item(0).nodeValue.includes("Niedziela")) {

                    thisTrElem.style.color = "red"
                }
                if (thisTrElem.cells[5].childNodes.item(0).nodeValue >= 'tak') {
                    var holStart = thisTrElem.cells[0].childNodes.item(0).nodeValue.slice(0,10).replace(/\s/g, '');
                    var holEnd = thisTrElem.cells[1].childNodes.item(0).nodeValue.slice(0,10).replace(/\s/g, '');
                    var startDate = new Date(holStart.split(".")[2], Number(holStart.split(".")[1])-1, holStart.split(".")[0]);
                    var endDate = new Date(holEnd.split(".")[2], Number(holStart.split(".")[1])-1, holEnd.split(".")[0]);
                    var oneDay = 24 * 60 * 60 * 1000;
                    var Diff = Math.round(Math.abs((startDate - endDate) / oneDay)) + 1;
                    var getDaysArray = function(start, end) {
                        for(var arr=[],dt=start; dt<=end; dt.setDate(dt.getDate()+1)){
                            arr.push(new Date(dt).toLocaleDateString());
                        }
                        return arr;
                    };
                    var daylist = getDaysArray(startDate,
                                                endDate);
                    for (var c = 0; c < howManyRows; c++) {
                        console.log(document.getElementById("table").getElementsByTagName("tbody")[0].rows[c].cells[1].innerText);
                        if ( daylist.indexOf(document.getElementById("table").getElementsByTagName("tbody")[0].rows[c].cells[0].innerText.substring(0,10).replace(/\s/g, '')) >= 0
                        &&
                            document.getElementById("table").getElementsByTagName("tbody")[0].rows[c].cells[1].innerText.substring(0,10).replace(/\s/g, '') === '' )
                        {
                            document.getElementById("table").getElementsByTagName("tbody")[0].rows[c].style.display = 'none';
                        }
                    }
                }
            }
        });


function selectElementContents(el) {
  var body = document.body, range, sel;
    if (document.createRange && window.getSelection) {
        range = document.createRange();
        sel = window.getSelection();
        sel.removeAllRanges();
        try {
            range.selectNodeContents(el);
            sel.addRange(range);
        } catch (e) {
            range.selectNode(el);
            sel.addRange(range);
        }
        document.execCommand("copy");
    } else if (body.createTextRange) {
        range = body.createTextRange();
        range.moveToElementText(el);
        range.execCommand("Copy");
    }
}
