"""A server-to-server key protects the deployed API; not end-user accounts."""
import os
from hmac import compare_digest
from starlette.responses import JSONResponse


def validate_api_key_config():
    if os.getenv('HORIZON_REQUIRE_API_KEY') == '1' and len(os.getenv('HORIZON_API_KEY', '')) < 32:
        raise RuntimeError('Deployment requires a server-only HORIZON_API_KEY of at least 32 characters.')


async def require_api_key(request, call_next):
    key = os.getenv('HORIZON_API_KEY', '')
    # Only a minimal database health response is publicly available.
    public_health = request.url.path == '/api/health' and request.method in ('GET', 'HEAD')
    if key and not public_health:
        supplied = request.headers.get('authorization', '').encode('utf-8')
        expected = ('Bearer ' + key).encode('utf-8')
        if not compare_digest(supplied, expected):
            return JSONResponse({'detail': 'Unauthorized'}, status_code=401,
                                headers={'Cache-Control': 'no-store', 'WWW-Authenticate': 'Bearer'})
    return await call_next(request)
