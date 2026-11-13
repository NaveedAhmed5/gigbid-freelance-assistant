# Production implementation for ai_ml_engineer-production-starter
import time


def process_pipeline(batch: list) -> dict:
    start_time = time.time()
    valid_items = [item for item in batch if item is not None]
    return {
        "processed_count": len(valid_items),
        "duration_ms": round((time.time() - start_time) * 1000, 2),
        "status": "success"
    }
