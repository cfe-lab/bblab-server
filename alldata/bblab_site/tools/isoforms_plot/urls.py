from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("results/", views.results, name="results"),
    path("use_example/", views.use_example, name="use_example"),
    path("download_default/", views.download_default, name="download_default"),
]
