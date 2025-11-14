from django.shortcuts import render
from templates_app.models.product import Product
from templates_app.classes.table_row_content import TableRowContent

# Edge case
# Product overflow of week table for week 4 and 8 ==> It goes out of template size

weeks_1 = [
    {
        "morning": {
            "enabled": True,
            "rows": [
                TableRowContent(
                    line_type="default", start=6, restart=True
                ).get_context(),
            ],
        },
        "evening": {
            "enabled": True,
            "rows": [
                TableRowContent(
                    line_type="default",
                    start=3,
                    restart=False,
                    product={
                        "name": "Magnésium",
                        "intake": "3x",
                        "icon": "pill.svg",
                    },
                ).get_context(),
                TableRowContent(
                    line_type="default", start=2, end=6, restart=False
                ).get_context(),
            ],
        },
        "time_col": True,
        "table_header": True,
    },
    {
        "morning": {
            "enabled": True,
            "rows": [
                TableRowContent(
                    line_type="stop", start=0, end=3, restart=False
                ).get_context(),
            ],
        },
        "evening": {
            "enabled": True,
            "rows": [
                TableRowContent(
                    line_type="arrow",
                    start=0,
                    restart=False,
                ).get_context(),
                TableRowContent(
                    line_type="stop", start=0, end=6, restart=False
                ).get_context(),
            ],
        },
        "time_col": False,
        "table_header": True,
    },
]

weeks_2 = [
    {
        "morning": {
            "enabled": True,
            "rows": [
                TableRowContent(
                    line_type="default",
                    start=0,
                    restart=False,
                    product={
                        "name": "Magnésium",
                        "intake": "3x",
                        "icon": "pill.svg",
                    },
                ).get_context(),
                TableRowContent(
                    line_type="default",
                    start=1,
                    restart=False,
                    product={
                        "name": "Magnésium",
                        "intake": "3x",
                        "icon": "pill.svg",
                    },
                ).get_context(),
                TableRowContent(
                    line_type="default",
                    start=6,
                    restart=False,
                    product={
                        "name": "Magnésium",
                        "intake": "3x",
                        "icon": "pill.svg",
                    },
                ).get_context(),
                "",
                "",
            ],
        },
        "evening": {
            "enabled": True,
            "rows": [
                TableRowContent(
                    line_type="default",
                    start=3,
                    restart=False,
                    product={
                        "name": "Magnésium",
                        "intake": "3x",
                        "icon": "pill.svg",
                    },
                ).get_context(),
                TableRowContent(
                    line_type="default",
                    start=3,
                    restart=False,
                    product={
                        "name": "Magnésium",
                        "intake": "3x",
                        "icon": "pill.svg",
                    },
                ).get_context(),
                TableRowContent(
                    line_type="default", start=2, end=6, restart=False
                ).get_context(),
            ],
        },
        "time_col": True,
        "table_header": True,
    },
    {
        "morning": {
            "enabled": True,
            "rows": [
                TableRowContent(
                    line_type="stop",
                    start=0,
                    end=5,
                    restart=False,
                ).get_context(),
                TableRowContent(
                    line_type="arrow",
                    start=0,
                    restart=False,
                ).get_context(),
                TableRowContent(
                    line_type="default",
                    start=0,
                    restart=False,
                ).get_context(),
            ],
        },
        "evening": {
            "enabled": True,
            "rows": [
                TableRowContent(
                    line_type="default",
                    start=3,
                    restart=False,
                    product={
                        "name": "Magnésium",
                        "intake": "3x",
                        "icon": "pill.svg",
                    },
                ).get_context(),
                TableRowContent(
                    line_type="default",
                    start=3,
                    restart=False,
                    product={
                        "name": "Magnésium",
                        "intake": "3x",
                        "icon": "pill.svg",
                    },
                ).get_context(),
                TableRowContent(
                    line_type="default", start=2, end=6, restart=False
                ).get_context(),
            ],
            "row_count": 5,
        },
        "time_col": False,
        "table_header": True,
    },
]


assets_context = {
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
    "weeks": weeks_2,
    "months": [{"weeks": weeks_2, "row_count": {"morning": 5, "evening": 5}}],
}


def calendar(request):
    """Calendar view for supplement cure schedule"""

    text = {
        "header": {
            "1": "Calendrier Symp",
        },
        "table": {"header": ["L", "M", "M", "J", "V", "S", "D"]},
        "phases": {
            "1": {"title": "Phase 1", "start": "Jour 1", "end": "Jour 9"},
            "2": {"title": "Phase 2", "start": "Jour 10", "end": "Jour X"},
            "subtitle": "Cochez chaque semaine terminée",
            "start": "Date début de la cure : ...................................",
            "changes": [
                {"stop": "Arrêter"},
                {"continue": "Continuer"},
                {"add": "Ajouter"},
            ],
        },
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
    }

    cure = {
        "phases": {
            "applicability": a5["apply_phases"],
        },
        "products": sorted(a5["products"], key=lambda p: p["phase"]),
    }

    context = {
        "title": "Calendrier de votre cure Symp",
        "text": text,
        "cure": cure,
    }
    return render(request, "templates_app/cure_calendar/base.html", context)


def assets(request):
    return render(request, "templates_app/cure_calendar/assets.html", assets_context)


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
