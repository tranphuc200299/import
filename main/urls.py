from django.urls import path
from . import views
urlpatterns = [
    path("", views.login, name="login"),
    path("f_cfsc1300/", views.f_cfsc1300, name="f_cfsc1300"),
    path("home", views.home, name="home"),
    path("f_cfsc3100/", views.f_cfsc3100, name="f_cfsc3100"),
    path("f_cfsc0900/", views.f_cfsc0900, name="f_cfsc0900"),
]