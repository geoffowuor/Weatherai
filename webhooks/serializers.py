from rest_framework import serializers
from .models import WebhookSubscription, WebhookEvent


class WebhookSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookSubscription
        fields = "__all__"
        read_only_fields = ("id", "weatherai_id", "active", "created_at")


class WebhookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEvent
        fields = "__all__"
        read_only_fields = ("id", "received_at", "source_ip")
