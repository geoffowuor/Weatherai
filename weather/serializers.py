from rest_framework import serializers
from .models import UserLocation


class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_lat(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value

    def validate_lon(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return value


class WeatherQuerySerializer(serializers.Serializer):
    days = serializers.IntegerField(min_value=1, max_value=16, default=7)
    ai = serializers.BooleanField(default=False)
    units = serializers.ChoiceField(choices=["metric", "imperial"], default="metric")
    lang = serializers.CharField(max_length=5, default="en")


class GeoWeatherSerializer(serializers.Serializer):
    ip = serializers.IPAddressField(required=False, default="auto")
    days = serializers.IntegerField(min_value=1, max_value=7, default=3)
    ai = serializers.BooleanField(default=False)


class TreeAnalysisSerializer(serializers.Serializer):
    image = serializers.ImageField()
    farmer_id = serializers.CharField(required=False, allow_blank=True)
    county = serializers.CharField(required=False, allow_blank=True)
    land_acres = serializers.FloatField(required=False, min_value=0.1)
    location = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
