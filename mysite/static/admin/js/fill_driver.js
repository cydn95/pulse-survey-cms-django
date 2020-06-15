var response_cache = {};

function fill_drivers(survey_id) {
    if (response_cache[survey_id]) {
        $("#id_driver").html(response_cache[survey_id]);
    } else {

        jQuery.getJSON(window.location.href + "drivers_for_survey/", {survey_id: survey_id},
            function(ret, textStatus) {
                //console.log(ret); return;
                var options = '<option value="" selected="selected">--------</option>';
                for (var i in ret) {
                    options += '<option value="' + ret[i].pk + '">' + ret[i].fields.driverName + '</option>';
                }
                response_cache[survey_id] = options;
                $("#id_driver").html(options);
            });
    }
}

window.addEventListener("load", function() {
    $("#id_survey").prop("selectedIndex", 1).val();
    
    fill_drivers($("#id_survey").val());
    (function($) {
        $("#id_survey").change(function () {
            fill_drivers($(this).val());
        });
    })(django.jQuery);
});
