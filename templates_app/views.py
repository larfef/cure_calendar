from calendar import c
from django.shortcuts import render
from django.db import transaction
from django.http import HttpResponse
from templates_app.classes.posology_calculation_model import PosologyCalculationModel
from templates_app.models.product import Product
from templates_app.classes.table_row_content import TableRowContent
import copy


def test_calendar(request):
    from templates_app.tests.posology.initial_state import (
        populate_database,
        create_mock_a5_product,
        labels,
    )
    from templates_app.models.product import Product
    import random

    try:
        with transaction.atomic():
            populate_database()
            a5_products = [
                # create_mock_a5_product(labels[v])
                # for v in random.sample(
                #     range(0, len(labels)), random.randint(4, len(labels))
                # )
                create_mock_a5_product(labels[0])
            ]

            calculator = PosologyCalculationModel(
                a5_products, cortisol_phase=random.randint(0, 1)
            )

            import math

            months = []

            empty_week = {
                "morning": {
                    "enabled": True,
                    "rows": [],
                },
                "evening": {"enabled": True, "rows": []},
                "time_col": False,
                "table_header": False,
            }

            tot_weeks = math.ceil(calculator.get_microbiote_phase_end() / 7)
            for week_index in range(tot_weeks):
                current_month = week_index // 4
                current_week = week_index % 4

                # Ensure the month dict exists
                if current_month >= len(months):
                    months.append(
                        {
                            "weeks": [],
                            "evening": {"num_line": 0},
                            "morning": {"num_line": 0},
                        }
                    )

                week = copy.deepcopy(empty_week)
                week["time_col"] = current_week == 0
                week["table_header"] = current_month == 0
                months[current_month]["weeks"].append(week)

                for product in calculator.products:
                    day_time = product["posology_scheme"].day_time
                    if (
                        product["delay"] < (week_index + 1) * 7
                        and product["delay"] >= week_index * 7
                    ):
                        content = TableRowContent(
                            line_type="default",
                            start=product["delay"] - week_index * 7
                            if product["delay"] > 28 or product["delay"] < 22
                            else 0,
                            product=product,
                        ).get_context()
                        week[day_time]["rows"].append(content)
                    elif (
                        product["posology_scheme"].duration_value > (week_index + 1) * 7
                        and product["delay"] < (week_index) * 7
                    ):
                        content = TableRowContent(
                            line_type="default",
                            start=0,
                        ).get_context()
                        week[day_time]["rows"].append(content)
                    else:
                        content = TableRowContent(
                            line_type="stop", start=0, end=5, stop=True
                        ).get_context()
                        week[day_time]["rows"].append(content)

                week["morning"]["row_count"] = len(week["morning"]["rows"])
                week["evening"]["row_count"] = len(week["evening"]["rows"])
                months[current_month]["evening"]["num_line"] = max(
                    len(w["evening"]["rows"]) for w in months[current_month]["weeks"]
                )
                months[current_month]["morning"]["num_line"] = max(
                    len(w["morning"]["rows"]) for w in months[current_month]["weeks"]
                )

            context = {
                "text": {
                    "header": {
                        "1": "Calendrier Symp",
                    },
                    "table": {"header": ["L", "M", "M", "J", "V", "S", "D"]},
                    "line": {
                        "stop": "Arrêter",
                        "restart": "Reprendre",
                    },
                },
                "months": months,
            }

            response = render(
                request, "templates_app/cure_calendar/assets.html", context
            )
            transaction.set_rollback(True)
            return response

    except Exception as e:
        # If something goes wrong, transaction automatically rolls back
        return HttpResponse(f"Error in test view: {str(e)}", status=500)


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
