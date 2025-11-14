from django.shortcuts import render
from templates_app.models.product import Product


# green-line

# type
# arrow -->
# stop --<
# default --

# start
# Integer from 1 to 7 to know on wich day start the line

# product display
# full ==> name , border box, posology,
# name ==> name
# None ==> no display
# pause ==> grey line


class LineRenderer:
    """Handles line rendering logic for cure calendar"""

    def __init__(
        self,
        line_type,
        start,
        end=None,
        width=None,
        restart=False,
        product=False,
        stop=False,
    ):
        """
        Args:
            line_type: 'default', 'arrow', or 'stop'
            start: Integer from 0-7 indicating start day
            end: Integer from 0-7 indicating end day (optional)
            width: Width value (default: "100%")
            restart: Boolean indicating if this is a restart line
            stop: Boolean indicating if this is a stop line
        """
        self.type = line_type
        self.start = start
        self.product = product
        self.end = end
        self.width = width or "100%"
        self.restart = restart and self.type != "stop"
        self.stop = stop

    def get_context(self):
        """Returns pre-calculated values for template"""
        return {
            "type": self.type,
            "restart": self.restart,
            "product": self.product,
            "stop": self.stop,
            "width": self.width,
            "start": self.start,
            "end": self.end,
            "end_modulo": self._calculate_end_modulo(),
            # Pre-calculated styles
            "restart_style": self._get_restart_style() if self.restart else "",
            "stop_style": self._get_stop_style(),
            "line_style": self._get_line_style(),
            "margin_left": self._get_margin_left(),
        }

    def _calculate_end_modulo(self):
        """Calculate end_modulo value"""
        if self.end:
            return 7 - self.end

    def _get_restart_style(self):
        """Calculate inline style for restart indicator"""
        if self.start < 6:
            return f"margin-left: calc({self.start} * calc(var(--cell-width) + 1px))"
        else:
            return f"right: 1px;"

    def _get_stop_style(self):
        """Calculate inline style for stop indicator"""
        end_modulo = self._calculate_end_modulo()
        return f"margin-right: calc((var(--cell-width) * (7 - {self.end})) + {end_modulo}px)"

    def _get_margin_left(self):
        return f"margin-left: calc({self.start} * calc(var(--cell-width) + 1px))"

    def _get_line_style(self):
        """Calculate inline style for the line itself"""
        styles = [f"width: {self.width}"]

        # Add margin-left for all types
        styles.append(
            f"margin-left: calc({self.start} * calc(var(--cell-width) + 1px))"
        )

        # Add margin-right for stop type
        if self.type == "stop" and self.end:
            end_modulo = self._calculate_end_modulo()
            styles.append(
                f"margin-right: calc((var(--cell-width) * (7 - {self.end})) + {end_modulo}px)"
            )

        return "; ".join(styles)


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
    "weeks": [
        {
            "morning": {
                "enabled": True,
                "rows": [
                    LineRenderer(
                        line_type="arrow", start=6, restart=False
                    ).get_context(),
                ],
            },
            "evening": {
                "enabled": True,
                "rows": [
                    LineRenderer(
                        line_type="arrow",
                        start=4,
                        restart=False,
                        product={
                            "name": "Magnésium",
                            "intake": "3x",
                            "icon": "pill.svg",
                        },
                    ).get_context(),
                    LineRenderer(
                        line_type="stop", start=0, end=6, restart=False
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
                    LineRenderer(
                        line_type="arrow", start=6, restart=False
                    ).get_context(),
                ],
            },
            "evening": {
                "enabled": True,
                "rows": [
                    LineRenderer(
                        line_type="arrow",
                        start=0,
                        restart=False,
                    ).get_context(),
                    LineRenderer(
                        line_type="stop", start=0, end=6, restart=False
                    ).get_context(),
                ],
            },
            "time_col": False,
            "table_header": True,
        },
    ],
    "content": {
        "line": LineRenderer(
            line_type="arrow", start=6, end=6, restart=False
        ).get_context(),
    },
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
