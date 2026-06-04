from django.db import models

# Create your models here.

class UserLocation(models.Model):
    

    UNITS_CHOICES = [("metric", "Metric (C)"), ("imperial", "Imperial (F)")]

    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    lat = models.FloatField()
    lon = models.FloatField()
    units = models.CharField(max_length=10, choices=UNITS_CHOICES, default="metric")
    lang = models.CharField(max_length=10, default="en")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.lat}, {self.lon})"


class WeatherCache(models.Model):


    user = models.ForeignKey(UserLocation, on_delete=models.CASCADE, related_name="cache")
    endpoint = models.CharField(max_length=50)  # e.g. "weather", "current"
    payload = models.JSONField()
    fetched_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "endpoint")

    def __str__(self):
        return f"{self.user.email} — {self.endpoint}"
