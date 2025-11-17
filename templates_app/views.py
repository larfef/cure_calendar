from django.shortcuts import render
from django.db import transaction
from django.http import HttpResponse
from templates_app.classes.posology_calculation_model import PosologyCalculationModel
from templates_app.models.product import Product
from templates_app.classes.table_row_content import TableRowContent


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
                create_mock_a5_product(labels[v])
                for v in random.sample(
                    range(0, len(labels)), random.randint(4, len(labels))
                )
            ]

            calculator = PosologyCalculationModel(
                a5_products, cortisol_phase=random.randint(0, 1)
            )

            # TableRowContent(
            #     line_type="default" if i == 0 else "stop",
            #     start=product["delay"] if i == 0 else 0,
            #     end=5,
            #     restart=False,
            #     product=product if i == 0 else False,
            # ).get_context()
            # for product in calculator.products
            # if product["posology_scheme"].first().day_time == "morning"

            NB_DAY = 7

            empty_week = [
                {
                    "morning": {
                        "enabled": True,
                        "rows": [],
                    },
                    "evening": {"enabled": True, "rows": []},
                    "time_col": i == 0,
                    "table_header": True,
                }
                for i in range(1)
            ]

            for product in calculator.products:
                if product["delay"] < NB_DAY:
                    day_time = product["posology_scheme"].day_time
                    content = TableRowContent(
                        line_type="default", start=product["delay"], product=product
                    ).get_context()
                    empty_week[0][day_time]["rows"].append(content)

            empty_week[0]["morning"]["row_count"] = len(
                empty_week[0]["morning"]["rows"]
            )
            empty_week[0]["evening"]["row_count"] = len(
                empty_week[0]["evening"]["rows"]
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
                "weeks": empty_week,
                "months": [
                    {
                        "weeks": empty_week,
                    }
                ],
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
