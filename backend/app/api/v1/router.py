from fastapi import APIRouter

from app.api.v1.routes import auth, chat, cicd, health, incidents, kubernetes, logs, metrics, security, terraform

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(chat.router)
api_router.include_router(metrics.router)
api_router.include_router(logs.router)
api_router.include_router(incidents.router)
api_router.include_router(kubernetes.router)
api_router.include_router(terraform.router)
api_router.include_router(cicd.router)
api_router.include_router(security.router)
