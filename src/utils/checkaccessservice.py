from functools import wraps
from fastapi import HTTPException

def check_access(access_needed: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            print(request, kwargs)
            if not request:
                raise HTTPException(status_code=400, detail="Request object is missing")
            roles = request.get("roles")
            user = request.user
            if not user or not user.is_active:
                raise HTTPException(status_code=400, detail="User is not present / active")
            if (not roles or access_needed not in roles):
                raise HTTPException(status_code=400, detail="User is not authorized to do this action")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
