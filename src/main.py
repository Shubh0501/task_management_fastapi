from fastapi import FastAPI, Depends
from src.config import settings, app_configs
from src.authentication.router import router as auth_router
from src.taskmanager.router import router as task_router
from src.middlewares import AuthenticationMiddleware
from models.role import Role, RoleList
from src.database import get_db_session
from sqlmodel import Session

app = FastAPI(**app_configs)

@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    return {
        "status": "ok",
        "message": "Atlys Task Management application is up and running!",
    }

@app.get("/run-startup-script")
async def run_startup_script(session: Session = Depends(get_db_session)) -> dict[str, str]:
    roles = RoleList._member_names_
    print(roles)
    for key in roles:
        role = Role(
            name= key,
            description = key,
            code= key
        )
        session.add(role)
    await session.commit()
    return {
        "status": "true",
        "description": "Roles have been created"
    }

task_app = FastAPI(title="Task Management", docs_url="/docs", openapi_url="/openapi.json")
task_app.add_middleware(AuthenticationMiddleware)

auth_app = FastAPI(title="Authentication System", docs_url="/docs", openapi_url="/openapi.json")

auth_app.include_router(auth_router)
task_app.include_router(task_router)

app.mount(settings.AUTH_API_PREFIX, auth_app)
app.mount(settings.TASK_API_PREFIX, task_app)