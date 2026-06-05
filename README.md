# WeatherAI Django Integration API

Backend service for integrating WeatherAI weather, alert, tree-analysis, usage, and webhook APIs through a Django REST Framework application.

## Stack

- Python 3.10+
- Django 4.2
- Django REST Framework
- drf-spectacular for OpenAPI schema and Swagger/ReDoc docs
- python-dotenv for local environment configuration
- SQLite for local development
- Gunicorn for production process serving

## Project Layout

```text
.
|-- alerts/              # Alert preferences, alert evaluation, alert logs
|-- config/              # Django settings, ASGI/WSGI, root URLs
|-- core/                # Shared WeatherAI API client and exception handling
|-- weather/             # User locations, weather proxy endpoints, health check
|-- webhooks/            # Webhook subscriptions and inbound event receiver
|-- manage.py
|-- requirements.txt
`-- README.md
```

## Prerequisites

Install the following before setup:

- Python 3.10 or newer
- `pip`
- `venv`
- A valid WeatherAI API key

The application reads the WeatherAI key from `.env` using:

```python
load_dotenv(BASE_DIR / ".env")
```

That means the `.env` file must live at the project root, next to `manage.py`.

## Local Setup

From the project root:

```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Create a local environment file:

```bash
touch .env
```

Add your WeatherAI key:

```env
WEATHERAI_API_KEY=your_real_weatherai_api_key_here
DJANGO_SECRET_KEY=your_real_django_secret_key_here
```

Do not commit `.env`. It is already ignored by `.gitignore`.

## Database Setup

Run migrations:

```bash
python manage.py migrate
```

Optional: create an admin user:

```bash
python manage.py createsuperuser
```

Verify the project configuration:

```bash
python manage.py check
```

## Run the API Locally

Start the development server:

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

Useful local URLs:

```text
GET /api/health/
GET /api/docs/
GET /api/redoc/
GET /api/schema/
GET /admin/
```

The health endpoint returns whether the WeatherAI key is configured:

```bash
curl http://127.0.0.1:8000/api/health/
```

Expected shape:

```json
{
  "status": "ok",
  "service": "weatherai-django",
  "weatherai_key_configured": true
}
```

## API Endpoints

### User Locations

Base path:

```text
/api/users/
```

Create a user location:

```bash
curl -X POST http://127.0.0.1:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo Farmer",
    "email": "demo@example.com",
    "lat": -1.286389,
    "lon": 36.817223,
    "units": "metric",
    "lang": "en"
  }'
```

List user locations:

```bash
curl http://127.0.0.1:8000/api/users/
```

Fetch forecast for a saved user location:

```bash
curl "http://127.0.0.1:8000/api/users/1/weather/?days=3&ai=false&units=metric&lang=en"
```

Fetch current weather:

```bash
curl http://127.0.0.1:8000/api/users/1/current/
```

Fetch WeatherAI insights:

```bash
curl http://127.0.0.1:8000/api/users/1/insights/
```

### Geo Weather

Use WeatherAI IP geolocation:

```bash
curl "http://127.0.0.1:8000/api/weather/geo/?ip=auto&days=3&ai=false"
```

### Usage

Fetch WeatherAI account usage:

```bash
curl http://127.0.0.1:8000/api/weather/usage/
```

### Tree Analysis

Analyze a tree image:

```bash
curl -X POST http://127.0.0.1:8000/api/trees/analyze/ \
  -F "image=@/path/to/image.jpg" \
  -F "farmer_id=farmer-001" \
  -F "county=Nairobi" \
  -F "land_acres=2.5" \
  -F "location=Nairobi" \
  -F "notes=Pilot analysis"
```

This endpoint requires `Pillow`, which is included in `requirements.txt`.

### Alert Preferences

Base path:

```text
/api/alerts/preferences/
```

Create alert preferences for a user:

```bash
curl -X POST http://127.0.0.1:8000/api/alerts/preferences/ \
  -H "Content-Type: application/json" \
  -d '{
    "user": 1,
    "triggers": ["rain", "high_temp", "low_temp"],
    "rain_threshold_mm": 10,
    "wind_threshold_kmh": 60,
    "temp_high_threshold_c": 35,
    "temp_low_threshold_c": 5,
    "active": true
  }'
```

Evaluate an alert preference immediately:

```bash
curl -X POST http://127.0.0.1:8000/api/alerts/preferences/1/check/
```

List alert logs:

```bash
curl http://127.0.0.1:8000/api/alerts/logs/
```

Filter alert logs by user:

```bash
curl "http://127.0.0.1:8000/api/alerts/logs/?user_id=1"
```

Supported alert triggers:

```text
rain
extreme_wind
frost
drought
high_temp
low_temp
```

### Webhooks

Base path:

```text
/api/webhooks/subscriptions/
```

Create a webhook subscription:

```bash
curl -X POST http://127.0.0.1:8000/api/webhooks/subscriptions/ \
  -H "Content-Type: application/json" \
  -d '{
    "user": 1,
    "receiver_url": "https://example.com/api/webhooks/receive/",
    "triggers": ["rain", "frost"],
    "timezone": "Africa/Nairobi"
  }'
```

When created, the app attempts to register the subscription with WeatherAI and stores the returned `weatherai_id`.

List remote WeatherAI webhooks:

```bash
curl http://127.0.0.1:8000/api/webhooks/subscriptions/remote/
```

Receive a WeatherAI webhook payload:

```bash
curl -X POST http://127.0.0.1:8000/api/webhooks/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "event": "rain",
    "message": "Rain threshold exceeded",
    "data": {
      "lat": -1.286389,
      "lon": 36.817223
    }
  }'
```

List stored webhook events:

```bash
curl http://127.0.0.1:8000/api/webhooks/events/
```

## WeatherAI Client Behavior

The shared client is defined in `core/weatherai_client.py`.

It:

- Reads `WEATHERAI_BASE_URL`, `WEATHERAI_API_KEY`, and `WEATHERAI_TIMEOUT` from Django settings.
- Sends `Authorization: Bearer <key>` on outgoing WeatherAI requests.
- Retries rate-limited requests with exponential backoff.
- Logs WeatherAI rate-limit headers when they are present.
- Returns upstream JSON responses directly to API callers.

Configured defaults:

```python
WEATHERAI_BASE_URL = "https://api.weather-ai.co"
WEATHERAI_TIMEOUT = 10
```

## Running Tests

Run the Django test suite:

```bash
python manage.py test
```

For checks without external WeatherAI calls:

```bash
python manage.py check
```

## Production Environment

Set these variables in your deployment environment:

```env
WEATHERAI_API_KEY=your_real_weatherai_api_key
DJANGO_SECRET_KEY=your_real_django_secret_key
DJANGO_SETTINGS_MODULE=config.settings
```

The app requires `DJANGO_SECRET_KEY` at startup. If it is missing, Django will fail fast instead of booting with an unsafe fallback key.



## Troubleshooting
- Generate your API key from `https://weather-ai.co/docs`

If `weatherai_key_configured` is `false`:

- Confirm `.env` exists in the same directory as `manage.py`.
- Confirm the variable name is exactly `WEATHERAI_API_KEY`.
- Restart the Django server after editing `.env`.

If WeatherAI calls return `502`:

- Confirm the API key is valid.
- Confirm the WeatherAI API is reachable from the running environment.
- Check whether the requested WeatherAI feature is available on your plan.
- Check server logs for the upstream HTTP error.

If image upload validation fails:

- Confirm `Pillow` is installed with `pip show Pillow`.
- Reinstall dependencies with `pip install -r requirements.txt`.
- Use a valid image file such as JPEG or PNG.
