$(document).ready(function() {

    // Buttons for toggling the visibility of responses to a given Issue
    $(".visibility_toggle").click(function() {
        curr_button = $(this).html();
        if (curr_button == "▷ Responses") {
            $(this).html("▽ Responses");
        }
        else {
            $(this).html("▷ Responses");
        }
        // Button must have an issueId attribute
        issue_id = $(this).attr("issueId");
        $("#responses_to_"+issue_id).toggle();
    });

    // Button for opening the ResponseForm for a given Issue
    $(".issue_reply_button").click(function() {
        issue_id = $(this).attr("issueId");
        // Hide all forms, then show the specific one
        // Avoids clutter - only one form is shown at a time
        $(".response_form").hide();
        $("#issue_" + issue_id + "_response_form").show();
    });
});