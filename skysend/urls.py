from django.contrib import admin
from django.urls import path
from .views import send_email

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", send_email, name="send_email"),
]
