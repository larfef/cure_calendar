

$(document).ready(function () {
    console.log("Center A5 footer");

    // Center footer
    fullHeight = $(".a5-container").height();
    remainingHeight = fullHeight - $(".a5-header").outerHeight(true) - $(".a5-body").outerHeight(true) - $(".a5-footer-text").outerHeight();


    if(remainingHeight > 0) {
        computedMargin = remainingHeight / 3;

        $(".a5-body").css("margin-top", computedMargin)
        $(".a5-footer-text").css("margin-top", computedMargin)
    } else {
        $(".a5-container").css("padding-top", "8px")
    }



});