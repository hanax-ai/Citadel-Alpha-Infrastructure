import time
import json
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, config: dict):
        super().__init__(app)
        self.logging_enabled = config.get('middleware', {}).get('logging', {}).get('enabled', False)
        self.include_body = config.get('middleware', {}).get('logging', {}).get('include_body', False)
        self.log_level_str = config.get('middleware', {}).get('logging', {}).get('level', 'info').upper()
        self.log_level = getattr(logging, self.log_level_str, logging.INFO)

    async def dispatch(self, request: Request, call_next):
        if not self.logging_enabled:
            return await call_next(request)

        start_time = time.time()
        request_id = request.headers.get("X-Request-ID", f"req-{int(start_time * 1000)}")

        # Log request details
        request_log_data = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else "unknown"
        }
        if self.include_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Attempt to read body without consuming it permanently
                body = await request.body()
                request_log_data["body"] = body.decode('utf-8')
                request._body = body # Re-attach body for downstream handlers
            except Exception as e:
                request_log_data["body_read_error"] = str(e)

        logger.log(self.log_level, f"Request: {json.dumps(request_log_data)}")

        response = await call_next(request)
        process_time = time.time() - start_time

        # Log response details
        response_log_data = {
            "request_id": request_id,
            "status_code": response.status_code,
            "process_time_ms": round(process_time * 1000, 2),
            "headers": dict(response.headers)
        }

        # Note: Reading response body is complex and can consume stream, 
        # potentially preventing client from receiving it. 
        # Only include if absolutely necessary and with caution.
        # For streaming responses (like LLM outputs), it's generally avoided.
        # if self.include_body and response.media_type and "application/json" in response.media_type:
        #     try:
        #         response_body = [chunk async for chunk in response.body_iterator]
        #         response_log_data["body"] = (b"".join(response_body)).decode('utf-8')
        #         response = Response(content=b"".join(response_body), status_code=response.status_code, headers=dict(response.headers), media_type=response.media_type)
        #     except Exception as e:
        #         response_log_data["body_read_error"] = str(e)


        logger.log(self.log_level, f"Response: {json.dumps(response_log_data)}")
        return response
