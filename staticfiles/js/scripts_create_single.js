    function createEvent(obj, eventName, functionToInvoke)
{
    if (document.addEventListener)
        obj.addEventListener(eventName, functionToInvoke);
    else
        obj.attachEvent("on"+eventName, functionToInvoke);
}
$(document).ready(function () {
    var holidays = document.getElementById("id_holiday");
    createEvent(holidays, "click", holiday_bool);
    document.getElementById("absence_type").style.display = 'none';
});

    function holiday_bool() {
        var hol_init = document.getElementById("id_holiday").checked;
        document.getElementById("id_holiday").checked !== hol_init;
        console.log(hol_init);
        if (hol_init === false) {
            document.getElementById("id_entry_time").previousElementSibling.innerHTML = "wejście";
            document.getElementById("id_leaving_time").previousElementSibling.innerHTML = "wyjście";
            document.getElementById("absence_type").style.display = 'none';
            $('#id_entry_time').datetimepicker({
                format: 'd.m.Y H:i',
                lang: 'pl',
                formatTime: 'H:i',
                timepicker:true,
                weeks: true,
                dayOfWeekStart: 1
            });
        } else {
            document.getElementById("id_entry_time").previousElementSibling.innerHTML = "od";
            document.getElementById("id_leaving_time").previousElementSibling.innerHTML = "do";
            document.getElementById("absence_type").style.display = 'block';
            $('#id_entry_time').datetimepicker({
                format: 'd.m.Y',
                lang: 'pl',
                timepicker:false,
                weeks: true,
                dayOfWeekStart: 1
            });
        }
    }

$(document).ready(function() {
        var list;
        list = document.querySelectorAll("input[name='kzz'], input[name='entry_time']," +
            "input[name='leaving_time'], select[name='holiday_type']");
        for (var i = 0; i < list.length; ++i) {
            list[i].classList.add('form-control');
    }
        document.getElementById("id_entry_time").previousElementSibling.innerHTML = "wejście";
        document.getElementById("id_leaving_time").previousElementSibling.innerHTML = "wyjście";
    });
    // $(function () {
    //         $('#id_entry_time').datetimepicker({
    //             format: 'd.m.Y H:i',
    //             lang: 'pl',
    //             formatTime: 'H:i',
    //             timepicker:true,
    //             weeks: true,
    //             dayOfWeekStart: 1
    //         });
    //     });
