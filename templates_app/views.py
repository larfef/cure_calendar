from django.shortcuts import render
from templates_app.models import Product


def calendar(request):
    """Calendar view for supplement cure schedule"""

    text = {
        "header": {
            "1": "Calendrier de votre cure Symp",
            "2": "Accrochez ce calendrier à un endroit visible - un petit coup d'œil chaque jour suffit pour rester régulier.",
            "3": "Votre cure de compléments est une étape essentielle pour transformer vos analyses en actions. Pensez à la commander si ce n'est déjà fait.",
        },
        "table": {
            "header": {"1": "Produit", "2": "Moment", "3": "Dosage", "4": "Durée"}
        },
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
        "products": Product.objects.all(),
    }

    cure = {
        "phases": {
            "applicability": a5["apply_phases"],
        },
        "products": sorted(a5["products"], key=lambda p: p.phase),
    }

    context = {
        "title": "Calendrier de votre cure Symp",
        "text": text,
        "cure": cure,
    }
    return render(request, "templates_app/cure_calendar/base.html", context)


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
        "cure_delay": "Délai:",
        "cure_product_recommended": "Produit recommandé",
        "cure_command": "Commander ma cure",
        "cure_mail": "Envoyer par email",
    }

    a5 = {
        "apply_phases": True,
        "products": Product.objects.all(),
        # "products": [
        #     {
        #         "phase": 1,
        #         "nutrients": [
        #             {"label": "Vitamine D3"},
        #             {"label": "Magnésium"},
        #         ],
        #         "delay": 0,
        #         "posology": "2 gélules le matin",
        #         "duration": "30 jours",
        #         "label": "Complexe Vitamine D + Magnésium",
        #     },
        #     {
        #         "phase": 1,
        #         "nutrients": [
        #             {"label": "Oméga 3"},
        #         ],
        #         "delay": 5,
        #         "posology": "1 gélule au repas",
        #         "duration": "60 jours",
        #         "label": "Oméga 3 Premium",
        #     },
        #     {
        #         "phase": 2,
        #         "nutrients": [
        #             {"label": "Probiotiques"},
        #             {"label": "Zinc"},
        #         ],
        #         "delay": 0,
        #         "posology": "1 gélule le soir",
        #         "duration": "30 jours",
        #         "label": "Probio + Zinc",
        #     },
        #     {
        #         "phase": 2,
        #         "nutrients": [
        #             {"label": "Probiotiques"},
        #             {"label": "Zinc"},
        #         ],
        #         "delay": 0,
        #         "posology": "1 gélule le soir",
        #         "duration": "30 jours",
        #         "label": "Probio + Zinc",
        #     },
        # ],
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
                    "count": len([p for p in a5["products"] if p.phase == 1]),
                    "items": [p for p in a5["products"] if p.phase == 1],
                }
            },
            "2": {
                "products": {
                    "count": len([p for p in a5["products"] if p.phase == 2]),
                    "items": [p for p in a5["products"] if p.phase == 2],
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
