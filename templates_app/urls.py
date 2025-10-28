from django.urls import path, include
from . import views

app_name = "templates_app"

urlpatterns = [
    path("", views.calendar, name="calendar"),
    path("cure", views.cure, name="cure"),
    path("nested_admin/", include("nested_admin.urls")),
]
