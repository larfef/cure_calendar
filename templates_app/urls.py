from django.urls import path, include
from . import views

app_name = "templates_app"

urlpatterns = [
    # path("cure", views.cure, name="cure"),
    path("assets", views.assets, name="assets"),
    path("calendar", views.calendar, name="calendar"),
    path("calendar/pdf", views.calendar_pdf, name="calendar_pdf"),
    path("nested_admin/", include("nested_admin.urls")),
]
