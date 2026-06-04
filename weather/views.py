from django.shortcuts import render

# Create your views here.
import logging
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter

from core.weatherai_client import client
from .models import UserLocation
from .serializers import (
    UserLocationSerializer,
    WeatherQuerySerializer,
    GeoWeatherSerializer,
    TreeAnalysisSerializer,
)

logger = logging.getLogger(__name__)


class UserLocationViewSet(viewsets.ModelViewSet):

    queryset = UserLocation.objects.all()
    serializer_class = UserLocationSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter("days", int, description="Forecast days (1–7 Free)"),
            OpenApiParameter("ai", bool, description="Include AI summary"),
            OpenApiParameter("units", str, description="metric or imperial"),
        ],
        description="Fetch current weather for this user's registered location.",
    )
    @action(detail=True, methods=["get"], url_path="weather")
    def weather(self, request, pk=None):
       
        user = self.get_object()
        query = WeatherQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        p = query.validated_data

        try:
            data = client.get_weather(
                lat=user.lat, lon=user.lon,
                days=p["days"], ai=p["ai"],
                units=p.get("units", user.units),
                lang=p.get("lang", user.lang),
            )
            return Response(data)
        except Exception as exc:
            logger.exception("WeatherAI error for user %s", user.id)
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

    @action(detail=True, methods=["get"], url_path="current")
    def current(self, request, pk=None):
      
        user = self.get_object()
        try:
            data = client.get_current(lat=user.lat, lon=user.lon, units=user.units)
            return Response(data)
        except Exception as exc:
            logger.exception("WeatherAI current error for user %s", user.id)
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

    @action(detail=True, methods=["get"], url_path="insights")
    def insights(self, request, pk=None):

        user = self.get_object()
        try:
            data = client.get_insights(lat=user.lat, lon=user.lon, units=user.units)
            return Response(data)
        except Exception as exc:
            logger.exception("WeatherAI insights error for user %s", user.id)
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


class GeoWeatherView(APIView):
   

    @extend_schema(
        parameters=[
            OpenApiParameter("ip", str, description="IP address or 'auto'"),
            OpenApiParameter("days", int),
            OpenApiParameter("ai", bool),
        ]
    )
    def get(self, request):
        serializer = GeoWeatherSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        p = serializer.validated_data

        try:
            data = client.get_weather_geo(ip=p["ip"], days=p["days"], ai=p["ai"])
            return Response(data)
        except Exception as exc:
            logger.exception("WeatherAI geo error")
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


class UsageView(APIView):
  

    def get(self, request):
        try:
            data = client.get_usage()
            return Response(data)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


class TreeAnalysisView(APIView):
  

    def post(self, request):
        serializer = TreeAnalysisSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        p = serializer.validated_data

        try:
            data = client.analyze_trees(
                image_file=p["image"],
                farmer_id=p.get("farmer_id", ""),
                county=p.get("county", ""),
                land_acres=p.get("land_acres"),
                location=p.get("location", ""),
                notes=p.get("notes", ""),
            )
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            logger.exception("Tree analysis error")
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


class HealthView(APIView):
 

    def get(self, request):
        return Response({
            "status": "ok",
            "service": "weatherai-django",
            "weatherai_key_configured": bool(
                __import__("django.conf", fromlist=["settings"]).settings.WEATHERAI_API_KEY
            ),
        })
