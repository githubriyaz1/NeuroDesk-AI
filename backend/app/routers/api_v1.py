from fastapi import APIRouter
from app.routers import health, auth, users, assets, workspace, ai_studio, project_generator, chat, workflow

api_v1_router = APIRouter()

# Include feature domain routers
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(users.router)
api_v1_router.include_router(assets.router)
api_v1_router.include_router(workspace.router)
api_v1_router.include_router(ai_studio.router)
api_v1_router.include_router(project_generator.router)
api_v1_router.include_router(chat.router)
api_v1_router.include_router(workflow.router)
