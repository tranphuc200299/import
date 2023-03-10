from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("f_cfsc1300/", views.menu4.f_cfsc1300, name="f_cfsc1300"),
    path("f_cfsc3100/", views.menu4.f_cfsc3100, name="f_cfsc3100"),
    path("f_cfsc0300/", views.menu4.f_cfsc0300, name="f_cfsc0300"),
    path("f_cfsc0100/", views.menu4.f_cfsc0100, name="f_cfsc0100"),
    path("f_cfsc2900/", views.menu4.f_cfsc2900, name="f_cfsc2900"),
    path("f_cfsc0500/", views.menu4.f_cfsc0500, name="f_cfsc0500"),
    path("f_cfsc1900/", views.menu4.f_cfsc1900, name="f_cfsc1900"),
    path("f_cfsc0900/", views.menu4.f_cfsc0900, name="f_cfsc0900"),
    path("f_cfsc1500/", views.menu4.f_cfsc1500, name="f_cfsc1500"),
    path("f_cfsc2700/", views.menu4.f_cfsc2700, name="f_cfsc2700"),
    path("f_cfsc2100/", views.menu4.f_cfsc2100, name="f_cfsc2100"),
    path("f_cfsc2300/", views.menu4.f_cfsc2300, name="f_cfsc2300"),
    path("f_cfsc1100/", views.menu4.f_cfsc1100, name="f_cfsc1100"),
    path("f_cfsc0700/", views.menu4.f_cfsc0700, name="f_cfsc0700"),
]
