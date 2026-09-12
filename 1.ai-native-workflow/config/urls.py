from django.http import HttpResponse
from django.urls import include, path

from accounts.views import signup


def homepage(request):
    return HttpResponse("Candor")


urlpatterns = [
    path("", homepage, name="homepage"),
    path("signup/", signup, name="signup"),
    path("", include("django.contrib.auth.urls")),
]
