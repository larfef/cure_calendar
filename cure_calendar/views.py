import base64
import random
from django.shortcuts import render
from django.db import transaction
from django.http import HttpResponse
from cure_calendar.services import CalendarContextBuilder
from cure_calendar.constants.posology import MAX_STARTING_DAYS
from cure_calendar.exporters.yaml import write_products_to_yaml
from cure_calendar.models.product import Product
from cure_calendar.services.posology.calculator import (
    PosologyCalculator,
    adapter_products_data_normalized,
)
from cure_calendar.tests.posology.initial_state import (
    load_products_from_yaml,
    populate_database,
    MOCK_PRODUCTS,
)
from cure_calendar.types import NormalizedProduct, ProductsData
from cure_calendar.utils.pdf_generator import generate_pdf_from_url


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
                # sample = random.randint(1, 6)
                sample = 7
                sample_dict = dict(random.sample(list(MOCK_PRODUCTS.items()), sample))

                products_data: ProductsData = {
                    "products": {},
                    "delays": {},
                    "cortisol_phase": True,
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

            response = render(request, "cure_calendar/base.html", context)
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
