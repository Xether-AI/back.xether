"""Base gRPC client with retry and error handling."""

import grpc
from typing import Any, Optional
from app.core.config import get_settings

settings = get_settings()


class BaseGRPCClient:
    """Wrapper for gRPC channel management and calling logic."""

    def __init__(self, host: str, port: int):
        self.target = f"{host}:{port}"
        self.channel: Optional[grpc.Channel] = None

    def connect(self):
        """Establish insecure channel (internal services)."""
        if not self.channel:
            self.channel = grpc.insecure_channel(self.target)
        return self.channel

    def close(self):
        """Close the channel."""
        if self.channel:
            self.channel.close()
            self.channel = None

    async def call_with_retry(self, stub_call: Any, request: Any, retries: int = 3) -> Any:
        """Call a gRPC method with primitive retry logic."""
        last_error = None
        for i in range(retries):
            try:
                return await stub_call(request)
            except grpc.RpcError as e:
                last_error = e
                if e.code() not in [grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.RESOURCE_EXHAUSTED]:
                    raise e
        raise last_error
