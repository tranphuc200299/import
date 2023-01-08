from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name="home"),
    path("f_cfsc1300/", views.f_cfsc1300, name="f_cfsc1300"),
    path("f_cfsc3100/", views.f_cfsc3100, name="f_cfsc3100"),
    path("f_cfsc0300/", views.f_cfsc0300, name="f_cfsc0300"),
]