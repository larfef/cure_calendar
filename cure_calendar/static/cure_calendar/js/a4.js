
$(document).ready(function () {

    order_date = $("#creation-time").text();
    new_text = $(".material-text").text().replace('{{date_de_prelevement}}', order_date);
    $(".material-text").text(new_text);
    console.log("REMOVE MATERIAL")


    $(".gauge-solutions-nutrients-title").each(function () {
        if($(this).next(".gauge-solutions-nutrients").length == 0){
            $(this).remove();
        }

    });
});