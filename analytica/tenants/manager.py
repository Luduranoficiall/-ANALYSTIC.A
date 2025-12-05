from fastapi import Request


async def tenant_middleware(request: Request, call_next):
    tenant = request.headers.get("X-TENANT")
    if not tenant:
        request.state.tenant = "default"
    else:
        request.state.tenant = tenant
    return await call_next(request)
