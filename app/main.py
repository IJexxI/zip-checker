from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
from app.api.routes import router
from app.storage.database import init_db, start_cleanup_scheduler
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="http://localhost:8080/realms/zip-checker/protocol/openid-connect/token"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Lifespan: Starting initialization")
    await init_db()
    logger.info("Lifespan: init_db called")
    start_cleanup_scheduler()
    logger.info("Lifespan: scheduler started")
    yield
    logger.info("Lifespan: Shutting down")

app = FastAPI(
    title="ZIP Checker",
    description="API для проверки ZIP-архивов с авторизацией",
    version="1.0",
    lifespan=lifespan
)

app.include_router(router)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="ZIP Checker API",
        version="1.0",
        description="API с авторизацией через Keycloak",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "http://localhost:8080/realms/zip-checker/protocol/openid-connect/token",
                    "scopes": {"openid": "OpenID Connect scope"}
                }
            }
        }
    }
    # Убери глобальную авторизацию
    # openapi_schema["security"] = [{"OAuth2PasswordBearer": ["openid"]}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi