import logging
from .models import AlertLog, AlertPreference
from core.weatherai_client import client

logger = logging.getLogger(__name__)


def evaluate_alert(pref: AlertPreference) -> AlertLog:
  
    user = pref.user

    try:
        weather = client.get_current(lat=user.lat, lon=user.lon, units="metric", ai=False)
    except Exception as exc:
        return AlertLog.objects.create(
            user=user, trigger="system", status="error",
            weather_snapshot={}, message=str(exc),
        )

    current = weather.get("current", {})
    triggered = []

    checks = {
        "rain": lambda: current.get("precip_mm", 0) >= pref.rain_threshold_mm,
        "extreme_wind": lambda: current.get("wind_kph", 0) >= pref.wind_threshold_kmh,
        "high_temp": lambda: current.get("temp_c", 0) >= pref.temp_high_threshold_c,
        "low_temp": lambda: current.get("temp_c", 99) <= pref.temp_low_threshold_c,
        "frost": lambda: current.get("temp_c", 99) <= 0,
    }

    for trigger in pref.triggers:
        check = checks.get(trigger)
        if check and check():
            triggered.append(trigger)
            logger.info("Alert triggered: %s for %s", trigger, user.email)

    status = "triggered" if triggered else "no_action"
    message = f"Triggers fired: {', '.join(triggered)}" if triggered else "No thresholds exceeded."

    return AlertLog.objects.create(
        user=user,
        trigger=", ".join(triggered) or "none",
        status=status,
        weather_snapshot=current,
        message=message,
    )
