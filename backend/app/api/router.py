from fastapi import APIRouter

from app.api.routes import analytics, auth, chat, documents, graph, health, i18n, students, tenant, workflows

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(graph.router, prefix="/graph", tags=["graph"])
api_router.include_router(tenant.router, prefix="/tenants", tags=["tenants"])
api_router.include_router(i18n.router, prefix="/i18n", tags=["i18n"])
