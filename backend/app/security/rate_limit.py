import time
from collections import defaultdict
from typing import Dict, List
from fastapi import Request, HTTPException, status

class InMemoryRateLimiter:
    def __init__(self, max_requests: int = 120, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        timestamps = self.clients[client_ip]
        
        # Filter out timestamps older than the window
        valid_timestamps = [ts for ts in timestamps if now - ts < self.window_seconds]
        self.clients[client_ip] = valid_timestamps
        
        if len(valid_timestamps) >= self.max_requests:
            return False
            
        valid_timestamps.append(now)
        return True

rate_limiter = InMemoryRateLimiter()

async def rate_limit_middleware(request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please slow down requests."
        )
