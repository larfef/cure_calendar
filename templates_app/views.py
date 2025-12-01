import base64
import random
from django.shortcuts import render
from django.db import transaction
from django.http import HttpResponse
from templates_app.services import CalendarContextBuilder
from templates_app.constants.posology_constants import MAX_STARTING_DAYS
from templates_app.data_export.yaml import write_products_to_yaml
from templates_app.models.product import Product
from templates_app.services.posology.calculator import (
    PosologyCalculator,
    adapter_products_data_normalized,
)
from templates_app.tests.posology.initial_state import (
    load_products_from_yaml,
    populate_database,
    MOCK_PRODUCTS,
)
from templates_app.types import NormalizedProduct, ProductsData
from templates_app.utils.pdf_generator import generate_pdf_from_url


def generate_cart_url(products: NormalizedProduct, second_phase: bool) -> str:
    if second_phase:
        ids = [
            p["shopify_id"]
            for p in products
            if p["first_unit_start"] >= MAX_STARTING_DAYS - 1
            or p["second_unit"]
            and p["second_unit_start"] >= MAX_STARTING_DAYS - 1
        ]
    else:
        ids = [p["shopify_id"] for p in products]

    raw = b"".join(id.to_bytes(8, "big") for id in ids)
    decoded = base64.urlsafe_b64encode(raw).decode("utf-8")
    if len(decoded):
        return f"https://symp.co/cure_cart?content={decoded}&client=4666"
    else:
        return None


def calendar(request):
    try:
        with transaction.atomic():
            # Initial db state
            populate_database()

            # Check if we should load from YAML or generate random
            load_from_yaml = request.GET.get("load_snapshot", "false").lower() == "true"

            if load_from_yaml:
                products_data = load_products_from_yaml("products_snapshot.yaml")
            else:
                sample = random.randint(1, 6)
                sample = 5
                sample_dict = dict(random.sample(list(MOCK_PRODUCTS.items()), sample))

                products_data: ProductsData = {
                    "products": {},
                    "delays": {},
                    "cortisol_phase": False,
                }

                for k, v in sample_dict.items():
                    product_id = v["id"]
                    products_data["products"][product_id] = Product.objects.get(
                        id=product_id
                    )
                    products_data["delays"][product_id] = (
                        0  # or random.randint(0, 7) or whatever logic you need
                    )

            normalized_products = adapter_products_data_normalized(
                products_data,
            )

            url = generate_cart_url(normalized_products, second_phase=True)

            # # Compute states common to products
            calculator = PosologyCalculator(
                normalized_products,
                cortisol_phase=products_data["cortisol_phase"],
                # cortisol_phase=any(p["phase"] == 1 for p in normalized_products),
            )

            # Log products states
            if not load_from_yaml:
                write_products_to_yaml(products_data, "products_snapshot.yaml")

            # Initialize builder
            builder = CalendarContextBuilder(
                calculator=calculator, products=normalized_products, cart_url=url
            )

            context = builder.build()
            pass

            response = render(request, "templates_app/cure_calendar/base.html", context)
            transaction.set_rollback(True)
            return response
            # return HttpResponse(status=200)

    except Exception as e:
        # If something goes wrong, transaction automatically rolls back
        return HttpResponse(f"Error in test view: {str(e)}", status=500)


def calendar_pdf(request):
    """Generate and display PDF of the cure calendar in browser"""
    from urllib.parse import urlencode

    # Extract all GET parameters from the request except those for this view (if any)
    query_params = request.GET.copy()
    # Remove any params you do NOT want forwarded, e.g. for /calendar_pdf only
    # query_params.pop("some_param", None)

    base_url = request.build_absolute_uri("/calendar")
    if query_params:
        calendar_url = f"{base_url}?{urlencode(query_params)}"
    else:
        calendar_url = base_url

    try:
        pdf_bytes = generate_pdf_from_url(calendar_url)

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = (
            'inline; filename="cure_calendar.pdf"'  # Changed to 'inline'
        )
        return response
    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)


def cure(request):
    static_sections = {
        "cure_text1": "Cette sélection personnalisée cible précisément vos déséquilibres observés. Certains compléments peuvent vous être familiers, mais ils ont été pensés pour agir ensemble, au bon moment, selon vos besoins.",
        "phase1_title": "Phase 1 Jour 1 de la cure",
        "phase1": "Jour 1",
        "phase2_title": "Phase 2 Jour 10 de la cure",
        "phase2": "Jour 10",
        "tab_titles": [
            "Nutriments prioritaires",
            "Dosage",
            "Durée",
        ],
        "cure_delay": "Démarrer au jour",
        "cure_product_recommended": "Nutriments recommandés",
        "cure_command": "Commander ma cure",
        "cure_mail": "Envoyer par email",
    }

    a5 = {
        "apply_phases": True,
        # "products": Product.objects.all(),
        "products": [
            {
                "phase": 1,
                "nutrients": [
                    {"label": "Vitamine D3"},
                    {"label": "Magnésium"},
                ],
                "delay": 0,
                "posology": "2 gélules le matin",
                "duration": "30 jours",
                "label": "Complexe Vitamine D + Magnésium",
            },
            {
                "phase": 2,
                "nutrients": [
                    {"label": "Oméga 3"},
                ],
                "delay": 5,
                "posology": "1 gélule au repas",
                "duration": "60 jours",
                "label": "Oméga 3 Premium",
            },
            {
                "phase": 2,
                "nutrients": [
                    {"label": "Probiotiques"},
                    {"label": "Zinc"},
                ],
                "delay": 0,
                "posology": "1 gélule le soir",
                "duration": "30 jours",
                "label": "Probio + Zinc",
            },
            {
                "phase": 2,
                "nutrients": [
                    {"label": "Probiotiques"},
                    {"label": "Zinc"},
                ],
                "delay": 0,
                "posology": "1 gélule le soir",
                "duration": "30 jours",
                "label": "Probio + Zinc",
            },
        ],
        "link": "https://example.com/order",
        "static_content": {
            "simplycure_text": "Commandez facilement vos compléments sur Symp",
            "no_simplycure_text": "Consultez votre praticien pour obtenir vos compléments",
            "footer_text": "Ces recommandations sont personnalisées selon votre profil santé. Consultez votre praticien en cas de doute.",
        },
    }

    pro_type = "DOCTOR"  # or "NUTRI" to hide the order button

    cure = {
        "url": "https://example.com/cure/123",
        "phases": {
            "1": {
                "products": {
                    "count": len([p for p in a5["products"] if p["phase"] == 1]),
                    "items": [p for p in a5["products"] if p["phase"] == 1],
                }
            },
            "2": {
                "products": {
                    "count": len([p for p in a5["products"] if p["phase"] == 2]),
                    "items": [p for p in a5["products"] if p["phase"] == 2],
                }
            },
        },
        "products": a5["products"],
        "section_titles": [
            "Nutriments prioritaires",
            "Dosage",
            "Durée",
        ],
    }

    context = {
        "static_sections": static_sections,
        "a5": a5,
        "pro_type": pro_type,
        "cure_template": cure,
    }

    return render(request, "templates_app/cure.html", context)
