

$(document).ready(function () {
    $(".gauge-section-solutions-category").on('click', function () {
        toggleCategory($(this));
    })

    footer_pages();
});


function toggleCategory(category_element) {
    category = category_element.attr('category');

    category_element.find(".dropdown-arrow").toggleClass("active");
    all_category_elements = $(`.gauge-section-solutions *[category='${category}']:not(.gauge-section-solutions-category)`);

    //all_category_elements.filter("table").hide();
    all_category_elements.slideToggle();

}

function footer_pages() {
    report_pages = $(".pagebreak:not(.no-footer)")
    report_pages_count = report_pages.length

    page_index = 1

    footer_content = $("#footer-content").html();
    report_pages.each(function () {
        $(this).children(':last').css('margin-bottom', 0);
        $(this).append(`<div class="page-number">${footer_content}</div>`);
        page_index = page_index + 1;
    });

}