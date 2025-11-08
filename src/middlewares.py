from fastapi import status, Request
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.base import BaseHTTPMiddleware
from models.user import User
from models.role import Role, UserRoleLink
from src.database import SessionLocal
from sqlmodel import select
from src.config import settings
from typing import Optional

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        public_paths = {
            "/auth/login",
            "/auth/register",
            "/docs",
            "/openapi.json",
            "/tasks/docs",
            "/tasks/openapi.json",
            "/auth/docs",
            "/auth/openapi.json",
            "/run-startup-script",
            "/healthcheck",
        }

        if any(request.url.path.startswith("/task"+path) for path in public_paths):
            return await call_next(request)
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Unable to validate credentials."},
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Unable to validate credentials."},
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except JWTError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Unable to validate credentials."},
                headers={"WWW-Authenticate": "Bearer"},
            )
        async with SessionLocal() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user: Optional[User] = result.scalars().first()
            if not user:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Unable to validate credentials."},
                    headers={"WWW-Authenticate": "Bearer"},
                )
            result = await db.execute(select(Role.code).join(UserRoleLink, UserRoleLink.role_id == Role.id).where(UserRoleLink.user_id == user_id, Role.is_active == True, UserRoleLink.is_active == True))
            roles = result.scalars().all()
            request.scope["user"] = user
            request.scope["roles"] = roles
            response = await call_next(request)
            return response