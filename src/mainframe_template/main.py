"""Application entrypoint and HTTP API routing.

Design by Contract:
- Pre-conditions: FastAPI and Uvicorn runtime environment initialized.
- Post-conditions: ASGI-compliant web application exposing health and operational endpoints.
"""

from __future__ import annotations

import socket
import time
from typing import Any, Dict

from mainframe_template.config import Settings, get_settings

START_TIME: float = time.time()


try:
    from fastapi import FastAPI, Response, status
    from fastapi.responses import JSONResponse
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    FastAPI = Any  # type: ignore[misc,assignment]


def create_app() -> Any:
    """Instantiate and configure the FastAPI application.

    Docstring:
        Pre-conditions:
            None.
        Post-conditions:
            Returns a configured FastAPI instance with health, readiness, and root handlers.
    """
    settings: Settings = get_settings()

    if not HAS_FASTAPI:
        # Minimal pure ASGI fallback for zero-dependency execution environments
        async def asgi_app(scope: Dict[str, Any], receive: Any, send: Any) -> None:
            if scope["type"] == "http":
                body = b'{"status": "ok", "runtime": "asgi-minimal"}'
                await send({
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [[b"content-type", b"application/json"]],
                })
                await send({"type": "http.response.body", "body": body})

        return asgi_app

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        docs_url="/docs",
        redoc_url=None,
    )

    @app.get("/healthz", status_code=status.HTTP_200_OK, tags=["Probe"])
    async def liveness_probe() -> Dict[str, str]:
        """Kubernetes liveness probe handler.

        Docstring:
            Pre-conditions:
                None.
            Post-conditions:
                Returns HTTP 200 with basic health status.
        """
        return {"status": "healthy"}

    @app.get("/ready", status_code=status.HTTP_200_OK, tags=["Probe"])
    async def readiness_probe() -> Dict[str, str]:
        """Kubernetes readiness probe handler.

        Docstring:
            Pre-conditions:
                Service initialization must be complete.
            Post-conditions:
                Returns HTTP 200 when container is ready to accept gateway ingress.
        """
        return {"status": "ready"}

    @app.get("/", status_code=status.HTTP_200_OK, tags=["Metadata"])
    async def root_status() -> Dict[str, Any]:
        """Root status handler returning operational telemetry and environment context.

        Docstring:
            Pre-conditions:
                None.
            Post-conditions:
                Returns detailed service runtime dictionary with uptime and host identification.
        """
        uptime_seconds: float = round(time.time() - START_TIME, 2)
        return {
            "app_name": settings.app_name,
            "environment": settings.app_env,
            "version": settings.version,
            "hostname": socket.gethostname(),
            "uptime_seconds": uptime_seconds,
            "status": "operational",
        }

    return app


app = create_app()


def run() -> None:
    """CLI execution entrypoint.

    Docstring:
        Pre-conditions:
            Network port specified in settings must be bindable.
        Post-conditions:
            Starts Uvicorn server serving the application indefinitely.
    """
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "mainframe_template.main:app",
        host="0.0.0.0",
        port=settings.port,
        log_level=settings.log_level.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    run()
