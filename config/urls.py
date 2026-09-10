from django.http import HttpResponse
from django.urls import path


def homepage(request):
    return HttpResponse("Candor")


urlpatterns = [
    path("", homepage, name="homepage"),
]
