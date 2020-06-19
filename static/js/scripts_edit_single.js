function createEvent(obj, eventName, functionToInvoke){
    if (document.addEventListener)
        obj.addEventListener(eventName, functionToInvoke);
    else
        obj.attachEvent("on"+eventName, functionToInvoke);
}

$(document).ready(function () {
    document.getElementById("id_holiday_type").parentElement.setAttribute("id", "absence_type");
    var holidays = document.getElementById("id_holiday");
    var extra_time = document.getElementById("id_extra_time");
    createEvent(holidays, "click", holiday_bool);
    if (document.getElementById("id_holiday").checked){
        document.getElementById("absence_type").style.display = 'block';
        document.getElementById("absence_type").firstChild.innerHTML = "absence type";
        extra_time.parentElement.style.display = 'none';
    }else{
        document.getElementById("absence_type").style.display = 'none';
        extra_time.parentElement.style.display = 'block';
    }
});

function holiday_bool() {
        var hol_init = document.getElementById("id_holiday").checked;
        var extra_time = document.getElementById("id_extra_time");
        document.getElementById("id_holiday").checked !== hol_init;
        console.log(hol_init);
        if (hol_init === false) {
            document.getElementById("id_entry_time").previousElementSibling.innerHTML = "entry";
            document.getElementById("id_leaving_time").previousElementSibling.innerHTML = "leaving";
            document.getElementById("absence_type").style.display = 'none';
            extra_time.style.display = 'block';
            extra_time.previousElementSibling.style.display = 'block';
            $('#id_entry_time, #id_leaving_time').datetimepicker({
                format: 'd.m.Y H:i',
                lang: 'en',
                formatTime: 'H:i',
                timepicker:true,
                weeks: true,
                dayOfWeekStart: 1
            });
        } else {
            document.getElementById("id_entry_time").previousElementSibling.innerHTML = "from";
            document.getElementById("id_leaving_time").previousElementSibling.innerHTML = "to";
            var absence = document.getElementById("absence_type");
            absence.firstChild.innerHTML = "absence type";
            absence.style.display = 'block';
            extra_time.style.display = 'none';
            extra_time.previousElementSibling.style.display = 'none';
            $('#id_entry_time, #id_leaving_time').datetimepicker({
                format: 'd.m.Y',
                lang: 'en',
                timepicker:false,
                weeks: true,
                dayOfWeekStart: 1
            });
        }
    }

$(document).ready(function() {
    var hol_init = document.getElementById("id_holiday").checked;
    var extra_hours = document.getElementById('id_extra_time');
        var list;
        list = document.querySelectorAll("input[name='shortsign'], input[name='entry_time'], input[name='extra_time']," +
            "input[name='leaving_time'], select[name='holiday_type']");
        for (var i = 0; i < list.length; ++i) {
            list[i].classList.add('form-control');
    }
        if (hol_init === false) {
            document.getElementById("id_entry_time").previousElementSibling.innerHTML = "entry";
            document.getElementById("id_leaving_time").previousElementSibling.innerHTML = "leaving";

            extra_hours.previousElementSibling.innerHTML = "over hours";
            extra_hours.style.display = 'block';
            extra_hours.previousElementSibling.style.display = 'block';
        } else {
            document.getElementById("id_entry_time").previousElementSibling.innerHTML = "from";
            document.getElementById("id_leaving_time").previousElementSibling.innerHTML = "to";
            extra_hours.style.display = 'none';
            extra_hours.previousElementSibling.style.display = 'none';
        }
        document.getElementById("id_accepted").previousElementSibling.innerHTML = "accepted(?)";
        document.getElementById("id_holiday").previousElementSibling.innerHTML = "days off(?)";

    });
    if (document.getElementById("id_leaving_time").value === '') {
        $(function () {
            $('#id_leaving_time').datetimepicker({
                format: 'd.m.Y H:i',
                lang: 'en',
                formatTime: 'H:i',
                weeks: true,
                dayOfWeekStart: 1
            });
        });
    }

