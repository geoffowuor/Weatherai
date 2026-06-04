from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertPreferenceViewSet, AlertLogViewSet

router = DefaultRouter()
router.register("preferences", AlertPreferenceViewSet, basename="alert-pref")
router.register("logs", AlertLogViewSet, basename="alert-log")

urlpatterns = [path("", include(router.urls))]
