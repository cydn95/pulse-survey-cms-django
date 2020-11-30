var response_cache = {};

function fill_shgroups(survey_id) {
    if (response_cache[survey_id]) {
        $("#id_shGroup").html(response_cache[survey_id]);
    } else {

        jQuery.getJSON(window.location.href + "shgroups_for_survey/", {survey_id: survey_id},
            function(ret, textStatus) {
                //console.log(ret); return;
                var options = '<option value="" selected="selected">--------</option>';
                for (var i in ret) {
                    options += '<option value="' + ret[i].pk + '">' + ret[i].fields.SHGroupName + '</option>';
                }
                response_cache[survey_id] = options;
                $("#id_shGroup").html(options);
            });
    }
}

window.addEventListener("load", function() {
    $("#id_survey").prop("selectedIndex", 1).val();
    
    fill_shgroups($("#id_survey").val());
    (function($) {
        $("#id_survey").change(function () {
            fill_shgroups($(this).val());
        });
    })(django.jQuery);
});
