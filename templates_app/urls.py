from django.urls import path, include
from . import views

app_name = "templates_app"

urlpatterns = [
    path("cure", views.cure, name="cure"),
    path("assets", views.test_calendar, name="test_calendar"),
    path("nested_admin/", include("nested_admin.urls")),
]
