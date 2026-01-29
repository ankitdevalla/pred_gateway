import logging
import uuid
from _contextvars import ContextVar

request_id_ctx_var: ContextVar[str | None] = ContextVar("request_id", default=None)

class RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx_var.get() or "unknown"
        return True

def setup_logging():
    logging.basicConfig(level=logging.INFO,
        format="%(asctime)s | %(levelname)s | request_id=%(request_id)s | %(message)s",
    )
    logger = logging.getLogger()
    logger.addFilter(RequestIDFilter())