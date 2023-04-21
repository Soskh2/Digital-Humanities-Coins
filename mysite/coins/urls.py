from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("home", views.index, name="index"),
    path("coin-data/", views.coin_data, name="coin_data"),
]