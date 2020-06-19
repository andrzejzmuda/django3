$(document).ready(function(){Counter();
    $('[data-toggle="tooltip"]').tooltip({ trigger: 'click' });
});


function Counter() {
    var tables = document.querySelectorAll('table[id="table"]');
    var count = tables.length;
    for (var n=0; n<count; n++) {
        document.getElementById('table').setAttribute("id", "table"+n);
        document.getElementById('result').setAttribute("id", "result"+n);
        document.getElementById('result_extra').setAttribute("id", "result_extra"+n);
        var sum_hours = 0;
        var sum_minutes = 0;
        var sum_extra_hours = 0;
        var sum_extra_minutes = 0;
        var tableElem = document.getElementById("table"+n);
        var tableBody = tableElem.getElementsByTagName("tbody").item(0);
        var howManyRows = tableBody.rows.length;
        for (var i = 0; i < howManyRows; i++) {
            var thisTrElem = tableBody.rows[i];
            var thisTdElem = thisTrElem.cells[2];
            var thisTdElem_2 = thisTrElem.cells[3];
            var thisTextNode;
            var thisTextNode_2;
            if (thisTrElem.cells[4].childNodes.item(0).nodeValue !== 'nie' &&
                thisTrElem.cells[5].childNodes.item(0).nodeValue >= 'nie') {
                thisTextNode = thisTdElem.childNodes.item(0).nodeValue;
                thisTextNode_2 = thisTdElem_2.childNodes.item(0).nodeValue;
            } else {
                thisTextNode = '0:0';
                thisTextNode_2 = '0:0';
            }
            var hours = Number(thisTextNode.split(":", 2)[0]);
            var extra_hours = Number(thisTextNode_2.split(":", 2)[0]);
            var minutes = Number(thisTextNode.split(":", 2)[1]);
            var extra_minutes = Number(thisTextNode_2.split(":", 2)[1]);

            if (!isNaN(hours) && !isNaN(minutes)) {
                sum_hours += hours;
                sum_minutes += minutes;
                sum_extra_hours += extra_hours;
                sum_extra_minutes += extra_minutes;
                var realmin = sum_minutes % 60;
                var hours_from_mins = Math.floor(sum_minutes / 60);
                var realmin_extra = sum_extra_minutes % 60;
                var hours_from_extra_mins = Math.floor(sum_extra_minutes / 60);
            }
            var result = Number(sum_hours + hours_from_mins) + ":" + (realmin < 10 ? '0' + realmin : realmin);
            var result_extra = Number(sum_extra_hours+hours_from_extra_mins) + ":" + (realmin_extra < 9 ? '0' + realmin_extra : realmin_extra);
        }
        document.querySelector('#result'+n).innerHTML = result;
        document.querySelector('#result_extra'+n).innerHTML = result_extra;
    }
    }

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


// function calculateTime() {
//         var tables = document.querySelectorAll('table[id="table"]');
//         var count = tables.length;
//         var sum_hours = 0;
//         var sum_minutes = 0;
//         for (var n=0; n<count; n++) {
//             var tableElem = document.getElementById("table"+n);
//             console.log(tableElem);
//             var tableBody = tableElem.getElementsByTagName("tbody").item(0);
//             var howManyRows = tableBody.rows.length;
//             for (var i = 0; i < howManyRows; i++) {
//                 var thisTrElem = tableBody.rows[i];
//                 var thisTdElem = thisTrElem.cells[2];
//                 var thisTextNode;
//                 if (thisTrElem.cells[3].childNodes.item(0).nodeValue !== 'nie' &&
//                     thisTrElem.cells[4].childNodes.item(0).nodeValue === 'nie') {
//                     thisTextNode = thisTdElem.childNodes.item(0).nodeValue;
//                 } else {
//                     thisTextNode = '0:0';
//                 }
//                 var hours = Number(thisTextNode.split(":", 2)[0]);
//                 var minutes = Number(thisTextNode.split(":", 2)[1]);
//
//                 if (!isNaN(hours) && !isNaN(minutes)) {
//                     sum_hours += hours;
//                     sum_minutes += minutes;
//                     var realmin = sum_minutes % 60;
//                     var hours_from_mins = Math.floor(sum_minutes / 60);
//                 }
//                 var result = Number(sum_hours + hours_from_mins) + ":" + (realmin < 9 ? '0' + realmin : realmin)
//             }
//         }
//         document.querySelector('#result'+n).innerHTML = result;
//         }
