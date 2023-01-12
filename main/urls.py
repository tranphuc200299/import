from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("f_cfsc1300/", views.menu4.f_cfsc1300, name="f_cfsc1300"),
    path("f_cfsc3100/", views.menu4.f_cfsc3100, name="f_cfsc3100"),
    path("f_cfsc0300/", views.menu4.f_cfsc0300, name="f_cfsc0300"),
    path("f_cfsc0100/", views.menu4.f_cfsc0100, name="f_cfsc0100"),
    path("f_cfsc1500/", views.menu4.f_cfsc1500, name="f_cfsc1500"),
]