from django.db import models
from weather.models import UserLocation

# Create your models here.



class AlertPreference(models.Model):
    """Weather thresholds a user wants to be notified about."""

    TRIGGER_CHOICES = [
        ("rain", "Rain"),
        ("extreme_wind", "Extreme Wind"),
        ("frost", "Frost"),
        ("drought", "Drought"),
        ("high_temp", "High Temperature"),
        ("low_temp", "Low Temperature"),
    ]

    user = models.OneToOneField(
        UserLocation, on_delete=models.CASCADE, related_name="alert_preferences"
    )
    triggers = models.JSONField(default=list, help_text="List of trigger keys e.g. ['rain','frost']")
    rain_threshold_mm = models.FloatField(default=10.0)
    wind_threshold_kmh = models.FloatField(default=60.0)
    temp_high_threshold_c = models.FloatField(default=35.0)
    temp_low_threshold_c = models.FloatField(default=5.0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alerts for {self.user.email}"


class AlertLog(models.Model):
    """Record of every alert that was evaluated or fired."""

    STATUS_CHOICES = [
        ("triggered", "Triggered"),
        ("no_action", "No Action"),
        ("error", "Error"),
    ]

    user = models.ForeignKey(UserLocation, on_delete=models.CASCADE, related_name="alert_logs")
    trigger = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    weather_snapshot = models.JSONField()
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.trigger} — {self.status} ({self.user.email})"
