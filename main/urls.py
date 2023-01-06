from django.urls import path
from . import views
urlpatterns = [
    path("", views.login, name="login"),
    path("f_cfsc1300/", views.f_cfsc1300, name="f_cfsc1300"),
]