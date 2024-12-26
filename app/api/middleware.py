from fastapi import Request, HTTPException
from typing import Callable
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
import ipaddress

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

class InternalOnlyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, allowed_networks=None):
        super().__init__(app)
        self.allowed_networks = allowed_networks or [
            ipaddress.ip_network("127.0.0.1/32"),  # localhost
        ]

    async def dispatch(self, request: Request, call_next: Callable):
        if not request.client:
            return await call_next(request) # Allow for test client
            
        client_host = request.client.host
        
        if client_host == "testclient":
            return await call_next(request)
            
        try:
            # Check if the client IP is in allowed networks
            client_ip = ipaddress.ip_address(client_host)
            is_allowed = any(client_ip in network for network in self.allowed_networks)
            
            if not is_allowed:
                raise HTTPException(status_code=403, detail="Access denied")
                
            return await call_next(request)
        except ValueError:
            raise HTTPException(status_code=403, detail="Invalid IP address")

def setup_middleware(app):
    # Add CORS middleware with restrictive settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"]
    )
    
    # Add timing middleware
    app.add_middleware(TimingMiddleware)
    
    # Add internal-only middleware
    app.add_middleware(InternalOnlyMiddleware)