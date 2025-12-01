
a4_height = 1000
a4_inner_height = 1000

$(document).ready(function () {
    split_long_comments();
    console.log("CUT TABLES");
    cut_tables();
    console.log("CUT COMMENTS");
    cut_multi_page_comments();

    //Delete empty div
    $(".splitable-child:empty").remove();

    number_pages();

});

function split_long_comments() {
    comments = $(".long-comment");

    comments.each(function () {
        if($(this).outerHeight(true) > 300){
            cut_indexes = [];
            current_height = 0;
            $(this).children().each(function () {
                child_height = $(this).outerHeight(true);

                if(current_height + child_height > 250){
                    cut_indexes.push($(this).index());
                    current_height = child_height;
                } else {
                    current_height = current_height + child_height;
                }
            });
            parent_classes = $(this).attr('class');
            new_sections = []
            first_section = null
            for(let i = 0; i < cut_indexes.length - 1; i++){
                cut_index = cut_indexes[i];
                if(i == 0){
                    first_section = $(this).children().slice(0, cut_index).clone();
                }

                slice_end = cut_indexes[i+1];

                cut_clone = $(this).children().slice(cut_index, slice_end).clone();
                cut_clone.wrapAll(`<div class="${parent_classes}"></div>`)
                cut_clone.parent().removeClass('long-comment');
                new_sections.push(cut_clone.parent());
            }
            $(this).empty();
            $(this).append(first_section);

            for(const new_section of new_sections){
                $(this).parent().after(new_section);
            }
        }
    });
}

function cut_tables() {
    tables = $(".a4-report .multi-page-table");

    tables.each(function () {
        above_height = 0;
        $(this).prevAll().each(function () {
            console.log($(this));
            console.log($(this).css('padding-top'));
            console.log($(this).height());
            console.log($(this).outerHeight(true));
            above_height = above_height + $(this).outerHeight(true);
        });
        header_height = $(this).find('thead tr').outerHeight(true);
        console.log(above_height);

        $(this).find('thead tr th').children().each(function () {
            console.log($(this).text());
            console.log("Header child height: " + $(this).height());
            console.log("Header child width: " + $(this).width());
            console.log("Header font size: " + $(this).css('font-size'));
            console.log("Header line height: " + $(this).css('line-height'));
            console.log("Header letter spacing: " + $(this).css('letter-spacing'));
        });
        console.log("Header height: " + header_height);

        remaining_height = a4_inner_height - (above_height + header_height)

        cut_indexes = []
        $(this).find('tbody tr').each(function () {
            curr_height = $(this).outerHeight(true);

            if(remaining_height - curr_height < 0) {
                cut_indexes.push($(this).index());
                remaining_height = a4_inner_height - header_height - curr_height;
            } else {
                remaining_height = remaining_height - curr_height;
            }
        })
        console.log(cut_indexes);
        index = 0
        table_rows = $(this).find('tbody tr');
        tr_slices = []
        last_slice_start = 0
        for(const cut_index of cut_indexes) {
            if(index == 0) {
                tr_slices.push(table_rows.slice(0, cut_index))
            } else {
                tr_slices.push(tr_slice = table_rows.slice(cut_indexes[index-1], cut_index))
            }
            index ++;
            last_slice_start = cut_index;
        }
        tr_slices.push(table_rows.slice(last_slice_start))
        table_parent = $(this).parent();

        index = 0
        for(const tr_slice of tr_slices){
            table_clone = $(this).clone()

            table_clone.wrap(`<div class="${table_parent.attr('class')}"></div>`)
            if(index == 0){
                table_clone.parent().prepend($(this).prevAll().get().reverse());
            } else if(index == tr_slices.length - 1){
                table_clone.parent().append($(this).nextAll());
            }
            $(this).parent().before(table_clone.parent());

            table_clone.children("tbody").empty();
            table_clone.children("tbody").append(tr_slice);

            index ++;
        }
        $(this).parent().remove();

    });


}

function cut_multi_page_comments() {
    comments = $(".a4-report .multi-page-comment");

    comments.each(function () {
        protection = false
        inflammation = false
        console.log($(this).attr('id'));
        if($(this).attr('id') == "PROTECTION"){
            protection = true;
        }
        if($(this).attr('id') == "INFLAMMATION"){
            inflammation = true;
        }

        above_height = 0;
        page_parent = $(this).parentsUntil(".pagebreak").last();
        page_parent.prevAll().each(function () {
            above_height = above_height + $(this).outerHeight(true);
        });

        remaining_height = a4_inner_height - above_height
        if($(this).outerHeight(true) > remaining_height){
            comment_childs = $(this).children();
            current_remaining_height = remaining_height
            cut_indexes = []
            comment_childs.each(function () {

                child_height = $(this).outerHeight(true)
                if(inflammation){
                    console.log(child_height);
                    console.log(current_remaining_height);
                }

                if(current_remaining_height < child_height  || $(this).hasClass('reset-page')) {
                    if(inflammation){
                        console.log("RESET PAGE")
                    }
                    cut_indexes.push({
                        'index': $(this).index()
                    });
                    current_remaining_height = a4_inner_height - child_height;
                } else {
                    current_remaining_height = current_remaining_height - child_height
                }
            })
            console.log(cut_indexes);
            pages = []
            first_slice = null
            if(cut_indexes.length > 0){
                first_slice = $(this).children().slice(0, cut_indexes[0]['index']).clone();
            }
            last_part = null

            cut_indexes.push({
                'index': $(this).children().length
            })
            page_classes = page_parent.parent().attr('class');

            for(let i = 0; i < cut_indexes.length - 1; i++){
                cut_index = cut_indexes[i];
                slice_end = cut_indexes[i+1]['index'];

                cut_clone = $(this).children().slice(cut_index['index'], slice_end).clone();
                //cut_clone.wrapAll(`<div></div>`);
                //cut_clone = cut_clone.parent();
                cut_clone.wrapAll(`<div class="${page_classes}"></div>`)

                if(i == cut_indexes.length - 2){
                    page_parent.nextAll().each(function () {
                        $(this).detach().appendTo(cut_clone.parent());
                    });
                }
                pages.push(cut_clone.parent());
            }
            if(cut_indexes.length > 0 && cut_indexes[0]['index'] == 0){
                $(this).remove();
            }
            console.log(pages);

            $(this).empty();
            if(first_slice != null){
                first_slice.wrapAll('<div></div>');
                $(this).append(first_slice);
            }

            console.log("Nombre de pages:" + pages.length);
            for(const page of pages.reverse()){
                page_parent.parent().after(page);
            }
        } else {
            $(this).removeClass('multi-page-comment');
        }
    })

}

function number_pages() {
    report_pages = $(".pagebreak:not(.no-footer)")
    report_pages_count = report_pages.length

    page_index = 1
    report_pages.each(function () {
        $(this).children(':last').css('margin-bottom', 0);
        $(this).append(`<div class="page-number">L’interprétation des résultats, la description de symptômes pouvant y être attachés, ainsi que les conseils alimentaires résultent de l’expertise Symp.
        <br/>Ces résultats ne doivent en aucun cas êtres utilisés en tant que diagnostic, soin médical ou traitement d’une quelconque maladie.</div>`)
        page_index = page_index + 1;
    });

}