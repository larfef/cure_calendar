from django.urls import path, include
from . import views

app_name = "cure_calendar"

urlpatterns = [
    # path("cure", views.cure, name="cure"),
    path("calendar", views.calendar, name="calendar"),
    path("calendar/pdf", views.calendar_pdf, name="calendar_pdf"),
    path("nested_admin/", include("nested_admin.urls")),
]
