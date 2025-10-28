$(document).ready(function () {
    $(".invisible-to-hide").each(function () {
		const elementId = $(this).attr('id');

		if (elementId === 'analyses-items'
			&& window.innerWidth > 1200)
		{
			$(this).show();
            $(this).css('visibility', 'visible');
			$(this).css('display', 'block');
		}
        else {
            $(this).hide();
            $(this).css('visibility', 'visible');
			$(this).css('display', 'none');
		}
    });
});

// Open the analysis dropdown by default on desktop
$(document).ready(function () {

    const analysesDropdown = $('#analyses-dropdown');
    if (window.innerWidth > 1200) {
        analysesDropdown.addClass('active');
    } 
});

$(".dropdown-header").on('click', function () {
    const dropdown = $(this).parent(".dropdown");
    const analysesItems = $('#analyses-items');
	const meetItems = $('#meet-items');

	// Special case for meeting dropdown
	// where items are shown outside the header
	// border box
	if (dropdown.attr('id') === 'meet-dropdown') {
        if (dropdown.hasClass('active')) {
            dropdown.removeClass('active');
            meetItems.css({
                'visibility': 'hidden',
                'display': 'none'
            });
        } else {
            dropdown.addClass('active');
            meetItems.css({
                'visibility': 'visible',
                'display': 'block'
            });
        }
    }
	else if (dropdown.hasClass('active')) {
		dropdown.removeClass('active');
		
		if ($(this).attr('id') === 'analyses-header')
			analysesItems.css({
				'visibility': 'hidden',
				'display': 'none'
			});
	}
	else {
		dropdown.toggleClass('active');

		if ($(this).attr('id') === 'analyses-header')
			analysesItems.css({
				'visibility': 'visible',
				'display': 'block'
			});
	}
});

$(".tab").on('click', function () {
    $(this).siblings(".tab").removeClass("active");
    $(this).addClass("active");

    const tab = $(this).attr('target');
    $(this).parent(".tabs-wrapper").siblings(".tab-content").hide();

    const $targetTab = $(`.tab-content[tab='${tab}']`);
    const displayType = $targetTab.attr('data-display') || 'block';
    $targetTab.css('display', displayType);
});

$(".button-to-detailed").on('click', function () {
    $(".report-summary").hide();
    $(".report-detailed").show();
});

$(".button-to-summary").on('click', function () {
    $(".report-detailed").hide();
    $(".report-summary").show();

});



let oldWidth = window.innerWidth;
let responsiveThreshold = 800;

$(document).ready(function () {
    moveComponents(true);
});


$(window).on('resize', function () {
    moveComponents(false);
});

function moveComponents(initial) {
    const newWidth = window.innerWidth;

    if((oldWidth < responsiveThreshold || initial) && newWidth >= responsiveThreshold){
        console.log("Resize to laptop");

        $(".laptop-move").each(function () {
            const target = $(this).attr('target');
            console.log($(this));
            console.log(target);
            console.log($(`#${target}`));
            $(this).appendTo($(`#${target}`));
        });
    } else if((oldWidth >= responsiveThreshold || initial) && newWidth < responsiveThreshold) {
        console.log("Resize to mobile");
    }
    oldWidth = newWidth;
}

// $(".pdf-mail-button").on('click', function () {
//     const url = new URL(window.location.href);
//     const params = new URLSearchParams(url.search);
//     const code = params.get('code');
//     const id = params.get('id');
//     if(code && id) {
//         $(this).prop("disabled", true);
//         $(this).find(".no-load-section").hide();
//         $(this).find(".load-section").show();

//         fetch(`/sympAPI/client/send_report_mail?id=${id}&code=${code}`, {
//             method: "GET",
//             headers: {
//                 "Content-Type": "application/json",
//             }
//         }).then((res) => {
//             if(res.status == 200){
//                 window.alert("Le rapport a bien été envoyé par mail")
//             } else {
//                 window.alert("Un problème est survenu, veuillez contacter hello@symp.co")
//             }
//             $(this).find(".load-section").hide();
//             $(this).find(".no-load-section").show();
//         });
//     }
// });

$("#report-email-form").on('submit', function (e) {
    e.preventDefault();
    console.log("[DEBUG] Form submitted");

    const emailInput = document.getElementById('email-input');
    const email = emailInput.value.trim();
    console.log("[DEBUG] Email input value:", email);

    // Basic email validation
    if (!email || !email.includes('@')) {
        console.log("[DEBUG] Invalid email entered");
        document.getElementById('email-status').innerHTML = '<div style="color: red;">Veuillez entrer une adresse email valide</div>';
        return;
    }

    const url = new URL(window.location.href);
    const params = new URLSearchParams(url.search);
    const code = params.get('code');
    const id = params.get('id');
    console.log("[DEBUG] URL params - code:", code, "id:", id);

    if(code && id) {
        const submitButton = $(this).find('.pdf-mail-button');
        submitButton.prop("disabled", true);
        submitButton.find(".no-load-section").hide();
        submitButton.find(".load-section").show();

        // Clear previous status
        document.getElementById('email-status').innerHTML = '';

        const fetchUrl = `/sympAPI/client/send_report_mail?id=${id}&code=${code}&email=${encodeURIComponent(email)}`;
        console.log("[DEBUG] Fetching:", fetchUrl);

        fetch(fetchUrl, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            }
        }).then((res) => {
            console.log("[DEBUG] Fetch response status:", res.status);
            if(res.status == 200){
                document.getElementById('email-status').innerHTML = '<div style="color: green;">✓ Le rapport a bien été envoyé par mail</div>';
                emailInput.value = ''; // Clear the input
                console.log("[DEBUG] Email sent successfully");
            } else {
                document.getElementById('email-status').innerHTML = '<div style="color: red;">Un problème est survenu, veuillez contacter hello@symp.co</div>';
                console.log("[DEBUG] Error sending email, status:", res.status);
            }
            submitButton.find(".load-section").hide();
            submitButton.find(".no-load-section").show();
            submitButton.prop("disabled", false);
        }).catch((error) => {
            document.getElementById('email-status').innerHTML = '<div style="color: red;">Erreur de connexion</div>';
            submitButton.find(".load-section").hide();
            submitButton.find(".no-load-section").show();
            submitButton.prop("disabled", false);
            console.log("[DEBUG] Fetch error:", error);
        });
    } else {
        document.getElementById('email-status').innerHTML = '<div style="color: red;">Paramètres manquants</div>';
        console.log("[DEBUG] Missing code or id in URL parameters");
    }
});
