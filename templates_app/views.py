from calendar import HTMLCalendar
from http.client import HTTPResponse
import random
from django.shortcuts import render
from django.db import transaction
from django.http import HttpResponse
from templates_app.classes.calendar_context_builder import CalendarContextBuilder
from templates_app.classes.posology_calculation_model import (
    CORTISOL_PHASE_DURATION_DAYS,
    PosologyCalculationModel,
    adapter_products_data_normalized,
)
from templates_app.constants.calendar_constants import CALENDAR_TEXT
from templates_app.logging.yaml_writer import write_products_to_yaml
from templates_app.classes.line_content import (
    ContentDict,
    ContentType,
    LineContent,
    TextType,
)
from templates_app.models.product import Product
from templates_app.tests.posology.initial_state import (
    load_products_from_yaml,
    populate_database,
    MOCK_PRODUCTS,
)
from templates_app.types.product import ProductsData
from templates_app.utils.pdf_generator import generate_pdf_from_url


def calendar(request):
    try:
        with transaction.atomic():
            # Initial db state
            populate_database()

            # Check if we should load from YAML or generate random
            load_from_yaml = request.GET.get("load_snapshot", "false").lower() == "true"

            if load_from_yaml:
                products = load_products_from_yaml("products_snapshot.yaml")
            else:
                sample = random.randint(1, 6)
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

            # # Compute states common to products
            calculator = PosologyCalculationModel(
                normalized_products,
                # cortisol_phase=random.randint(0, 1)
                cortisol_phase=any(p["phase"] == 1 for p in normalized_products),
            )

            # Log products states
            # if not load_from_yaml:
            #     write_products_to_yaml(calculator.to_dict(), "products_snapshot.yaml")

            # Initialize builder
            builder = CalendarContextBuilder(
                calculator=calculator, products=normalized_products
            )

            context = builder.build()
            pass

            response = render(
                request, "templates_app/cure_calendar/calendar.html", context
            )
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


def assets(request):
    content: list[ContentDict] = [
        {
            "start": 0,
            "end": 1,
            "type": {"css": ContentType.GREEN_LINE, "inline": ContentType.CELL},
        },
        {
            "start": 2,
            "end": 4,
            "text": {
                "value": "Arrêter",
                "type": TextType.STOP_PRODUCT,
                "enabled": True,
            },
            "type": {"css": ContentType.GREEN_LINE, "inline": ContentType.CELL},
        },
        {
            "start": 5,
            "end": 7,
            "type": {"css": ContentType.GREEN_LINE, "inline": ContentType.CELL},
        },
    ]
    line_1 = LineContent(content, time_col=True).get_context()
    context = {
        "text": CALENDAR_TEXT,
        "month": {"morning": {"num_line": 2}, "evening": {"num_line": 2}},
        "weeks": [
            {
                "time_col": True,
                "morning": {"enabled": True, "rows": [line_1]},
                "evening": {"enabled": True, "rows": []},
                "mixed": {"enabled": False, "rows": []},
                "table_header": True,
            },
        ],
        "empty_week": {"enabled": True},
    }

    try:
        response = render(
            request, "templates_app/cure_calendar/assets/base.html", context
        )
        return response
    except Exception as e:
        return HttpResponse(f"Error rendering template: {e}")


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
