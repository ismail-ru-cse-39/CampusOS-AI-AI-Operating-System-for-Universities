from __future__ import annotations

from fastapi import APIRouter

from app.services.i18n import SUPPORTED_LANGUAGES, i18n_service

router = APIRouter()


@router.get("/languages")
async def list_languages():
    return {"languages": SUPPORTED_LANGUAGES, "default": "en"}


@router.get("/translate/{key}")
async def translate_key(key: str, lang: str = "en"):
    return {"key": key, "lang": lang, "text": i18n_service.translate(key, lang)}
