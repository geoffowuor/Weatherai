from rest_framework import serializers
from .models import AlertPreference, AlertLog


class AlertPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertPreference
        fields = "__all__"
        read_only_fields = ("id", "created_at")

    def validate_triggers(self, value):
        valid = {"rain", "extreme_wind", "frost", "drought", "high_temp", "low_temp"}
        for t in value:
            if t not in valid:
                raise serializers.ValidationError(f"'{t}' is not a valid trigger. Choose from: {valid}")
        return value


class AlertLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertLog
        fields = "__all__"
        read_only_fields = ("id", "created_at")
