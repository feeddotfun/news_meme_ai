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
            ipaddress.ip_network("172.17.0.0/16"),    # docker0
            ipaddress.ip_network("172.18.0.0/16"),    # docker bridge network
            ipaddress.ip_network("172.19.0.0/16"),    # docker bridge network
            ipaddress.ip_network("10.116.0.0/20"),    # eth1 private network
        ]

    async def dispatch(self, request: Request, call_next: Callable):
        if not request.client:
            return await call_next(request) # Allow for test client
            
        client_host = request.client.host

        forwarded_for = request.headers.get('x-forwarded-for')
        real_ip = request.headers.get('x-real-ip')

        if forwarded_for or real_ip:
            return await call_next(request)
        
        if client_host == "testclient":
            return await call_next(request)
            
        try:
            # Check if the client IP is in allowed networks
            client_ip = ipaddress.ip_address(client_host)
            is_allowed = any(client_ip in network for network in self.allowed_networks)
            
            if not is_allowed:
                print(f"Access denied for IP: {client_ip}")
                raise HTTPException(status_code=403, detail="Access denied")
                
            return await call_next(request)
        except ValueError:
            print(f"Invalid IP error")
            raise HTTPException(status_code=403, detail="Invalid IP address")

def setup_middleware(app):
    # Add CORS middleware with restrictive settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://test.feed.fun", "https://devnet.feed.fun", "https://feed.fun"],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time"]
        
    )
    
    # Add timing middleware
    app.add_middleware(TimingMiddleware)
    
    # Add internal-only middleware
    app.add_middleware(InternalOnlyMiddleware)