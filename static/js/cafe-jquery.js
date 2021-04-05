$(document).ready(function() {

    $(".visibility_toggle").click(function(issue_id) {
        curr_display = document.getElementById("response_to_"+issue_id).style.display;
        if (curr_display == "none") {
            document.getElementById("toggle_"+issue_id+"_responses").innerHTML = "▽ Responses";
            document.getElementById("response_to_"+issue_id).style.display = "block";
        }
        else {
            document.getElementById("toggle_"+issue_id+"_responses").innerHTML = "▷ Responses";
            document.getElementById("response_to_"+issue_id).style.display = "none";
        }
    });
});