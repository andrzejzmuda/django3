$(document).ready(function(){calculations(); triggers()});

function createEvent(obj, eventName, functionToInvoke)
{
    if (document.addEventListener)
        obj.addEventListener(eventName, functionToInvoke);
    else
        obj.attachEvent("on"+eventName, functionToInvoke);
}
function countRows() {
    rows = document.querySelectorAll('input[id*="-order"]').length;
    // console.log(rows);
    return rows
}

function triggers() {
    countRows();
    for (var i=0; i<countRows(); i++) {
    document.getElementById("id_orderitems_set-" + [i] + "-product").onchange = function () {calculations()};
    document.getElementById("orderitems_set-"+[i]+"-quantity").onchange = function () {calculations()};
    }
}

window.onchange = function () {
    var addbutton = document.getElementsByClassName("add-row");
    var delbuttons = document.getElementsByClassName("delete-row");
    for (var n = 0; n < delbuttons.length; n++) {
        createEvent(delbuttons[n], "click", calculations);
    }
        createEvent(addbutton[0], "click", triggers);
    };


function calculations(){
        sum = 0;
        countRows();
        for (var i = 0; i < countRows(); i++) {
            var x = document.getElementById("id_orderitems_set-"+[i]+"-product").selectedIndex;
            var y = document.getElementById("id_orderitems_set-"+[i]+"-product").options;

            if(y[x].index !== 0 && y[x].parentNode.parentNode.parentNode.attributes.getNamedItem('style') == null) {
                // console.log(y[x].parentNode.parentNode.parentNode.attributes.getNamedItem('style'));
                var quantity = document.getElementById("orderitems_set-"+[i]+"-quantity").value;
                var items = y[x].innerHTML;
                price = ((parseFloat(items.substr(items.length - 5))).toFixed(2) * quantity);
                sum += price;
            }
            if(sum<=30) {
                your_price = sum*0.4
            }
            else {
                your_price = sum-(30*0.6)
            }
            document.querySelector('#result').innerHTML = parseFloat(sum).toFixed(2);
            document.querySelector('#your_price').innerHTML = parseFloat(your_price).toFixed(2);
            }
        }
