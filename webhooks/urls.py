from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WebhookSubscriptionViewSet, WebhookReceiverView, WebhookEventViewSet

router = DefaultRouter()
router.register("subscriptions", WebhookSubscriptionViewSet, basename="webhook-sub")
router.register("events", WebhookEventViewSet, basename="webhook-event")

urlpatterns = [
    path("", include(router.urls)),
    path("receive/", WebhookReceiverView.as_view(), name="webhook-receive"),
]
