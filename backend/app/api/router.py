from fastapi import APIRouter

from app.api.routes import auth, chat, documents, health, students

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
