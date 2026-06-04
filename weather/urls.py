from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserLocationViewSet, GeoWeatherView, UsageView, TreeAnalysisView, HealthView

router = DefaultRouter()
router.register("users", UserLocationViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    path("weather/geo/", GeoWeatherView.as_view(), name="weather-geo"),
    path("weather/usage/", UsageView.as_view(), name="weather-usage"),
    path("trees/analyze/", TreeAnalysisView.as_view(), name="trees-analyze"),
    path("health/", HealthView.as_view(), name="health"),
]
