"""
Profiler middleware for the application.
"""

from datetime import datetime
from pathlib import Path

from fastapi import Request, Response
from pyinstrument import Profiler
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.config import settings


class PyInstrumentMiddleWare(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        profiler = Profiler(interval=0.001, async_mode="enabled")
        profiler.start()
        response = await call_next(request)
        profiler.stop()

        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"profile_{timestamp}.html"
        profiling_dir = Path(settings.BASE_DIR) / "backend" / "monitoring" / "profiling"
        profiling_dir.mkdir(parents=True, exist_ok=True)
        profiler.write_html(profiling_dir / filename)
        return response
