from django.urls import path
from . import views
urlpatterns = [
    path("", views.login, name="login"),
    path("home", views.home, name="home"),
    path("f_cfsc3100/", views.f_cfsc3100, name="f_cfsc3100"),
]