from django.db import models

# Create your models here.
from weather.models import UserLocation


class WebhookSubscription(models.Model):
 

    TRIGGER_CHOICES = [
        ("rain", "Rain"),
        ("extreme_wind", "Extreme Wind"),
        ("frost", "Frost"),
        ("drought", "Drought"),
    ]

    user = models.ForeignKey(UserLocation, on_delete=models.CASCADE, related_name="webhooks")
    weatherai_id = models.CharField(max_length=100, blank=True, help_text="ID returned by WeatherAI")
    receiver_url = models.URLField(help_text="Your HTTPS endpoint to receive payloads")
    triggers = models.JSONField(default=list)
    timezone = models.CharField(max_length=60, default="Africa/Nairobi")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Webhook {self.weatherai_id or '(unregistered)'} for {self.user.email}"


class WebhookEvent(models.Model):
  

    subscription = models.ForeignKey(
        WebhookSubscription, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="events",
    )
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)
    source_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-received_at"]

    def __str__(self):
        return f"Event at {self.received_at}"
