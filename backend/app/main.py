import logging
import os
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import coach, groq, metrics
from .schemas import MetricsOut, NutritionOut, PlanRequest, PlanResponse

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

PLANS_PER_HOUR = 20
CSRF_HEADER, CSRF_VALUE = "x-requested-with", "dimafit"

app = FastAPI(title="DimaFit", docs_url=None, redoc_url=None, openapi_url=None)


@app.middleware("http")
async def guard(request: Request, call_next):
    """Requests that use the API must come from our own page (other sites can't add this header)."""
    if (request.method not in ("GET", "HEAD", "OPTIONS") and request.url.path.startswith("/api/")
            and request.headers.get(CSRF_HEADER) != CSRF_VALUE):
        return JSONResponse({"error": "Request refused."}, status_code=403)
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    response.headers.setdefault("X-Frame-Options", "DENY")
    return response


@app.exception_handler(HTTPException)
async def http_error(_: Request, error: HTTPException) -> JSONResponse:
    return JSONResponse({"error": error.detail}, status_code=error.status_code)


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, error: RequestValidationError) -> JSONResponse:
    first = error.errors()[0] if error.errors() else {}
    field = ".".join(str(p) for p in first.get("loc", [])[2:])
    return JSONResponse({"error": "invalid", "field": field}, status_code=422)


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.get("/api/config")
def config() -> dict:
    return {"ai": groq.available()}


_recent: dict[str, list[float]] = {}


def _rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else ""
    moment = time.monotonic()
    recent = [t for t in _recent.get(ip, []) if moment - t < 3600]
    if len(recent) >= PLANS_PER_HOUR:
        raise HTTPException(429, "rate_limited")
    _recent[ip] = recent + [moment]


@app.post("/api/plan")
async def make_plan(body: PlanRequest, request: Request) -> PlanResponse:
    """Nothing is stored: the measurements are used for this answer only."""
    _rate_limit(request)
    profile = body.profile
    numbers = metrics.compute(profile)
    food = metrics.nutrition(profile, numbers)
    plan = await coach.build(profile, numbers, food, body.lang)

    warnings = []
    if profile.age >= 60 or numbers.bmi >= 35 or profile.injuries:
        warnings.append("see_doctor")
    if food.adjusted_goal == "underweight":
        warnings.append("underweight")
    if numbers.waist_to_height is not None and numbers.waist_to_height >= 0.5:
        warnings.append("waist_risk")
    if profile.waist_cm and profile.neck_cm and profile.body_fat_pct is None and numbers.body_fat is None:
        warnings.append("body_fat_unusable")
    if not plan.ai:
        warnings.append("ai_offline")
    return PlanResponse(metrics=MetricsOut(**numbers.__dict__), nutrition=NutritionOut(**food.__dict__),
                        plan=plan, warnings=warnings)


# The built React app, served from the same container in production.
_static = Path(os.environ.get("STATIC_DIR", Path(__file__).resolve().parents[2] / "frontend" / "dist"))
if _static.is_dir():
    app.mount("/assets", StaticFiles(directory=_static / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str) -> FileResponse:
        if path.startswith("api/"):
            raise HTTPException(404, "Not found.")
        file = (_static / path).resolve()
        if path and file.is_file() and _static.resolve() in file.parents:
            return FileResponse(file)
        return FileResponse(_static / "index.html")
