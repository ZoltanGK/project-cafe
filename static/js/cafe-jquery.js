$(document).ready(function() {

    $(".visibility_toggle").click(function() {
        curr_button = $(this).html();
        if (curr_button == "▷ Responses") {
            $(this).html("▽ Responses");
        }
        else {
            $(this).html("▷ Responses");
        }
        issue_id = $(this).attr("issueId");
        $("#responses_to_"+issue_id).toggle();
    });

    $(".issue_reply_button").click(function() {
        issue_id = $(this).attr("issueId");
        // Hide all forms, then show the specific one
        // Avoids clutter
        $(".response_form").hide();
        $("#issue_" + issue_id + "_response_form").show();
    });
});