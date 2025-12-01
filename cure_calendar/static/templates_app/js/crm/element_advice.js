

$("input#search-element-advice").keyup(function(event) {
    if (event.keyCode === 13) {
        searchElementAdvice();
    }
});

$(document).ready(function () {
    searchElementAdvice();
});

function searchElementAdvice(){
    var searchValue = $("input#search-element-advice").val();

    if(searchValue){
        searchValue = searchValue.toLowerCase();
        const allElementAdvices = $(".element-advice-label");

        allElementAdvices.each(function () {
            const elementLabel = $(this).parent().attr('label');

            const searchRegex = new RegExp(`${searchValue}`);

            if(searchRegex.test(elementLabel.toLowerCase())){
                $(`tr[label="${elementLabel}"]`).show();
            } else {
                $(`tr[label="${elementLabel}"]`).hide();
            }
        });
    } else {
        $("tr").show();
    }
}

function resetForm() {
    $(".modify-title").hide();
    $(".new-title").hide();
    $("#nut-add-save").hide();
    $("#nut-edit-save").hide();

    $(".new-pop-up select").prop("disabled", false);
    $(".new-pop-up select option").prop("selected", false);
    $(".new-pop-up input").val();
}

function handlePopUpOpen(nutType, elementId, nutId) {
    $("input#nut-type-field").val(nutType);

    $(".new-pop-up .form-field[nut-type]").hide();
    $(`.new-pop-up .form-field[nut-type='${nutType}']`).show();

    if(nutType == "nutrient"){
        $("#nutrient-form-fields").show();
        $("#parity-form-field").hide();
    } else {
        $("#nutrient-form-fields").hide();
        $("#parity-form-field").show();
    }
    $(`.form-field#element-form-field option[value='${elementId}']`).prop("selected",true)
    $(`.form-field#element-form-field option[value='${elementId}']`).prop("selected",true)

    $(`.form-field.nut-form-field[nut-type='${nutType}'] option[value='${nutId}']`).prop("selected", true);
    $(".black-background").show();
    $(".new-pop-up").css('display','flex');
}

$(".nut-add").on('click', function () {
    resetForm();

    $(".new-title").show();
    $("#nut-add-save").show();

    const nutType = $(this).attr('nut-type');
    const elementId = $(this).closest('tr').attr('nut-id');
    handlePopUpOpen(nutType, elementId);
});

$(".pop-up-close").on('click', function () {
    $(this).closest('.pop-up').hide();
    $(".black-background").hide();

});

$("tr:not(.cortisol-row) .food-card").on('click', function () {
    resetForm();

    $(".modify-title").show();
    $("#nut-edit-save").show();

    const nutType = $(this).find('.nut-type').val();
    $("#element-form-field select").attr("disabled", true);
    $(".nut-form-field select").attr("disabled", true);

    const perturbation = $(this).find('.perturbation').val();
    $(`#perturbations-form-field select option[mnemonic='${perturbation}']`).prop("selected", true);

    if(nutType == "nutrient"){
        const value = $(this).find('.value').val();
        $("#value-form-field").val(value);
        const valueUnit = $(this).find('.value_unit').val();
        console.log(valueUnit);
        $(`select#unit-form-field option[value='${valueUnit}']`).prop("selected", true);
        const daysCount = $(this).find('.days_count').val();
        $("#days-count-form-field").val(daysCount);
        const displayCount = $(this).find('.display_count').val();
        $("#display-count-form-field").val(displayCount);
        const priority = $(this).find('.priority').val();
        $(`#priority-form-field select option[value='${priority}']`).prop("selected", true);

        const symptoms = $(this).find('.symptom');
        symptoms.each(function () {
            const symptomId = $(this).val();
            $(`#symptoms-form-field select option[value='${symptomId}']`).prop("selected", true);
        });
    }

    const elementId = $(this).find('input.element-id').val();
    const nutId = $(this).find('input.nut-id').val();
    handlePopUpOpen(nutType, elementId, nutId);
});

function gatherData(){
    const selectedElement = $("#element-form-field select").val();
    const nutType = $("input#nut-type-field").val();
    const selectedNut = $(`.nut-form-field[nut-type='${nutType}'] select`).val();
    const selectedPerturbations = $("#perturbations-form-field select").val();
    const selectedParity = $("#parity-form-field select").val();
    const displayCount = $("#display-count-form-field").val();
    const priority = $("#priority-form-field select").val();
    const symptoms = $("#symptoms-form-field select").val();
    const value = $("#value-form-field").val();
    const unit = $("#unit-form-field").val();
    const daysCount = $("#days-count-form-field").val();

    const data = {
        "element": selectedElement,
        "nut-type": nutType,
        "nut-id": selectedNut,
        "perturbations": selectedPerturbations,
        "parity": selectedParity,
        "display-count": displayCount,
        "priority": priority,
        "symptoms": symptoms,
        "value": value,
        "unit": unit,
        "days-count": daysCount
        }

    return data;
}

$("button#nut-edit-save").on('click', function () {
    var searchValue = $("input#search-element-advice").val();
    const data = gatherData();
    if(data['perturbations'].length == 0){
        alert("Au moins 1 perturbation requise")
    } else {
        fetch("/sympAPI/crm/element_advice", {
            method: "PUT",
            headers: {
                "X-CSRFToken": csrftoken,
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        }).then((res) => {
            if(res.status == 200){
                let url = window.location.href.split('?')[0];
                url += "?search_value=" + searchValue;
                window.location.href = url;
                //location.reload();
            } else {
                alert("Erreur dans la modification, (tu peux me le signaler :D)")
            }
        });
    }

});

$("button#nut-add-save").on('click', function () {
    var searchValue = $("input#search-element-advice").val();
    const data = gatherData();
    if(data['perturbations'].length == 0){
        alert("Au moins 1 perturbation requise")
    } else {
        fetch("/sympAPI/crm/element_advice", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken,
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        }).then((res) => {
            if(res.status == 200){
                let url = window.location.href.split('?')[0];
                url += "?search_value=" + searchValue;
                window.location.href = url;
                //location.reload();
            } else {
                alert("Erreur dans l'ajout, (tu peux me le signaler :D)")
            }
        });
    }


})

$("tr:not(.cortisol-row) .food-card-wrapper").hover(function () {
    $(this).children('.food-card-close').css('display', 'flex');
}, function () {
    $(this).children('.food-card-close').hide();
});

$(".food-card-close").on('click', function () {
    const adviceId = $(this).parent().find('.advice-id').val();
    const perturbation = $(this).parent().find('.perturbation').val();
    const nutType = $(this).parent().find('.nut-type').val();

    if(adviceId && perturbation && nutType){

        fetch(`/sympAPI/crm/element_advice?advice=${adviceId}&perturbation=${perturbation}&nut-type=${nutType}`, {
            method: "DELETE",
            headers: {
                "X-CSRFToken": csrftoken,
                "Content-Type": "application/json",
            }
        }).then((res) => {
            if(res.status == 200){
                location.reload();
            } else {
                alert("Erreur dans la suppression, (tu peux me le signaler :D)")
            }
        });
    }

});