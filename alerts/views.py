from django.shortcuts import render
# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import AlertPreference, AlertLog
from .serializers import AlertPreferenceSerializer, AlertLogSerializer
from .services import evaluate_alert


class AlertPreferenceViewSet(viewsets.ModelViewSet):
  
    queryset = AlertPreference.objects.select_related("user").all()
    serializer_class = AlertPreferenceSerializer

    @action(detail=True, methods=["post"], url_path="check")
    def check(self, request, pk=None):
     
        pref = self.get_object()
        log = evaluate_alert(pref)
        return Response(AlertLogSerializer(log).data, status=status.HTTP_200_OK)


class AlertLogViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = AlertLog.objects.select_related("user").all()
    serializer_class = AlertLogSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user_id = self.request.query_params.get("user_id")
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs
