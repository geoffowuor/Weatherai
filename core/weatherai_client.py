
#Wraps all calls to https://api.weather-ai.co, handles auth, rate-limit headers, and retries with exponential back-off.

import time
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

RATE_LIMIT_HEADERS = ("X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset")


class WeatherAIClient:
    def __init__(self):
        self.base_url = settings.WEATHERAI_BASE_URL
        self.api_key = settings.WEATHERAI_API_KEY
        self.timeout = settings.WEATHERAI_TIMEOUT
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})



    def _request(self, method: str, path: str, retries: int = 3, **kwargs):
        url = f"{self.base_url}{path}"
        for attempt in range(retries):
            try:
                resp = self.session.request(method, url, timeout=self.timeout, **kwargs)
                self._log_rate_limits(resp)

                if resp.status_code == 429:
                    wait = 2 ** attempt
                    logger.warning("Rate limited by WeatherAI — retrying in %ss", wait)
                    time.sleep(wait)
                    continue

                resp.raise_for_status()
                return resp.json()

            except requests.exceptions.Timeout:
                logger.error("WeatherAI request timed out (attempt %d)", attempt + 1)
                if attempt == retries - 1:
                    raise
                time.sleep(2 ** attempt)

            except requests.exceptions.HTTPError as exc:
                logger.error("WeatherAI HTTP error: %s", exc)
                raise

        raise RuntimeError("WeatherAI request failed after retries")

    def _log_rate_limits(self, resp):
        info = {h: resp.headers.get(h) for h in RATE_LIMIT_HEADERS if resp.headers.get(h)}
        if info:
            logger.debug("WeatherAI rate limits: %s", info)

 

    def get_weather(self, lat: float, lon: float, days: int = 7,
                    ai: bool = False, units: str = "metric", lang: str = "en"):
       
        return self._request("GET", "/v1/weather", params={
            "lat": lat, "lon": lon, "days": days,
            "ai": str(ai).lower(), "units": units, "lang": lang,
        })

    def get_current(self, lat: float, lon: float,
                    ai: bool = False, units: str = "metric"):
      
        return self._request("GET", "/v1/current", params={
            "lat": lat, "lon": lon,
            "ai": str(ai).lower(), "units": units,
        })

    def get_weather_geo(self, ip: str = "auto", days: int = 7, ai: bool = False):
       
        return self._request("GET", "/v1/weather-geo", params={
            "ip": ip, "days": days, "ai": str(ai).lower(),
        })

    def get_insights(self, lat: float, lon: float, days: int = 7,
                     units: str = "metric", lang: str = "en"):
     
        return self._request("GET", "/v1/insights", params={
            "lat": lat, "lon": lon, "days": days, "units": units, "lang": lang,
        })

    def get_usage(self):
     
        return self._request("GET", "/v1/usage")

    def create_webhook(self, url: str, lat: float, lon: float,
                       triggers: list[str], timezone: str = "Africa/Nairobi"):
        
        return self._request("POST", "/v1/webhooks", json={
            "url": url, "lat": lat, "lon": lon,
            "triggers": triggers, "timezone": timezone,
        })

    def list_webhooks(self):  return self._request("GET", "/v1/webhooks")

    def delete_webhook(self, webhook_id: str):
      
        return self._request("DELETE", f"/v1/webhooks/{webhook_id}")

    def analyze_trees(self, image_file, farmer_id: str = "",
                      county: str = "", land_acres: float = None,
                      location: str = "", notes: str = ""):
     
        files = {"image": image_file}
        data = {k: v for k, v in {
            "farmerId": farmer_id, "county": county,
            "landAcres": land_acres, "location": location, "notes": notes,
        }.items() if v}
        return self._request("POST", "/v1/trees/analyze", files=files, data=data)


# Singleton
client = WeatherAIClient()
