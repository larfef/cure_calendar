

$(document).ready(function () {

    const cortisol = $("#a3-cortisol");

    if(cortisol.length){
        const cortisolHeight = cortisol.outerHeight(true);
        var availableSpace = $('#page1-analyses').outerHeight(false);

        $('#page1-analyses').children().each(function () {
            availableSpace = availableSpace - $(this).outerHeight(true);
        });

        if(availableSpace > cortisolHeight + 20){
            cortisol.css('margin-top', '20px');
            $('#page1-analyses').append(cortisol);
            $("#recom_title_no_cortisol").show();
        }
    } else {
        console.log("SHOW NO CORTISOL TITLE")
        $("#recom_title_no_cortisol").show();
    }


});