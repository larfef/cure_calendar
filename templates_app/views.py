from django.shortcuts import render
from django.db import transaction
from django.http import HttpResponse
from templates_app.classes.calendar_context_builder import CalendarContextBuilder
from templates_app.classes.posology_calculation_model import PosologyCalculationModel
from templates_app.constants.calendar_constants import text
from templates_app.logging.yaml_writer import write_products_to_yaml
from templates_app.classes.table_row_content import (
    ContentDict,
    ContentType,
    LineContent,
    TableRowContent,
    TextType,
)
import copy
import math
import random
from templates_app.tests.posology.initial_state import (
    populate_database,
    create_mock_a5_product,
    labels,
)
from templates_app.utils.pdf_generator import generate_pdf_from_url

NB_DAY = 7

MONTH_DAY = 4 * NB_DAY


def set_table_lines_for_month(month):
    arr = ["morning", "evening", "mixed"]

    for v in arr:
        month[v]["num_line"] = max(len(w[v]["rows"]) for w in month["weeks"])


def compute_week_content(product, week, week_index):
    # Check if content will be render in evening or
    # in morning row
    day_time = product["posology_scheme"].day_time

    # Get posology scheme duration with product delay
    posology_end = product["posology_scheme"].duration_value + product["delay"]

    current_week_start = week_index * NB_DAY
    current_week_end = (week_index + 1) * NB_DAY
    if product["delay"] < current_week_end and product["delay"] >= current_week_start:
        content = TableRowContent(
            line_type="default" if week_index % 4 != 3 else "arrow",
            start=product["delay"] - current_week_start
            # Use delay to offset the product in the week table only
            # when the product does not start in the last week of the month.
            # Otherwise, some product displays overflow from
            # the A4 dimensions.
            if product["delay"] > 28 or product["delay"] < 22
            else 0,
            time_col=not week_index % 4,
            product=product,
        ).get_context()
        week[day_time]["rows"].append(content)
    elif (
        product["posology_scheme"].duration_value + product["delay"] > current_week_end
        and product["delay"] < current_week_start
    ):
        content = TableRowContent(
            line_type="default" if week_index % 4 != 3 else "arrow",
            start=0,
            time_col=not week_index % 4,
            product_label=product["label"] if not week_index % 4 else False,
        ).get_context()
        week[day_time]["rows"].append(content)
    elif posology_end <= current_week_end and posology_end > current_week_start:
        content = TableRowContent(
            line_type="stop",
            start=0,
            end=7 - (current_week_end - posology_end),
            time_col=not week_index % 4,
        ).get_context()
        week[day_time]["rows"].append(content)
    elif (current_week_end // (MONTH_DAY + 1)) == (posology_end // (MONTH_DAY + 1)):
        week[day_time]["rows"].append("")
    elif product["delay"] >= current_week_end:
        week[day_time]["rows"].append("")


def calendar(request):
    try:
        with transaction.atomic():
            # Initial db state
            populate_database()

            # Create mock products
            a5_products = [
                # create_mock_a5_product(labels[v][0])
                # for v in random.sample(
                #     range(0, len(labels)), random.randint(4, len(labels))
                # )
                # for v in random.sample(range(0, len(labels)), 6)
                create_mock_a5_product(labels[8][0])
            ]

            # Compute states common to products
            calculator = PosologyCalculationModel(
                a5_products, cortisol_phase=random.randint(0, 1)
            )

            # Log products states
            write_products_to_yaml(calculator.to_dict(), "products_snapshot.yaml")

            # Initialize builder
            builder = CalendarContextBuilder(calculator)

            context = builder.build()

            response = render(
                request, "templates_app/cure_calendar/calendar.html", context
            )
            transaction.set_rollback(True)
            return response

    except Exception as e:
        # If something goes wrong, transaction automatically rolls back
        return HttpResponse(f"Error in test view: {str(e)}", status=500)


def calendar_pdf(request):
    """Generate and display PDF of the cure calendar in browser"""
    calendar_url = request.build_absolute_uri("/calendar")

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
        "text": text,
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
