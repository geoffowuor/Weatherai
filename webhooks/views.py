from django.shortcuts import render

# Create your views here.
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from core.weatherai_client import client
from .models import WebhookSubscription, WebhookEvent
from .serializers import WebhookSubscriptionSerializer, WebhookEventSerializer

logger = logging.getLogger(__name__)


class WebhookSubscriptionViewSet(viewsets.ModelViewSet):
   

    queryset = WebhookSubscription.objects.select_related("user").all()
    serializer_class = WebhookSubscriptionSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        # Register with WeatherAI
        try:
            resp = client.create_webhook(
                url=instance.receiver_url,
                lat=instance.user.lat,
                lon=instance.user.lon,
                triggers=instance.triggers,
                timezone=instance.timezone,
            )
            instance.weatherai_id = resp.get("id", "")
            instance.save(update_fields=["weatherai_id"])
        except Exception as exc:
            logger.warning("Could not register webhook with WeatherAI: %s", exc)

    def perform_destroy(self, instance):
        if instance.weatherai_id:
            try:
                client.delete_webhook(instance.weatherai_id)
            except Exception as exc:
                logger.warning("Could not delete WeatherAI webhook %s: %s", instance.weatherai_id, exc)
        instance.delete()

    @action(detail=False, methods=["get"], url_path="remote")
    def remote(self, request):
        
        try:
            data = client.list_webhooks()
            return Response(data)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


class WebhookReceiverView(APIView):


    def post(self, request):
        payload = request.data
        source_ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR"))

        logger.info("Received WeatherAI webhook from %s: %s", source_ip, payload)

        WebhookEvent.objects.create(payload=payload, source_ip=source_ip)

        return Response({"received": True}, status=status.HTTP_200_OK)


class WebhookEventViewSet(viewsets.ReadOnlyModelViewSet):
  

    queryset = WebhookEvent.objects.all()
    serializer_class = WebhookEventSerializer
