from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SUPPORTED_LANGUAGES = ["en", "ar", "zh", "es", "fr", "hi", "bn"]
DEFAULT_LANGUAGE = "en"

_TRANSLATIONS_DIR = Path(__file__).parent.parent / "i18n"


class I18nService:
    def __init__(self) -> None:
        self._cache: dict[str, dict[str, str]] = {}

    def _load(self, lang: str) -> dict[str, str]:
        if lang in self._cache:
            return self._cache[lang]
        path = _TRANSLATIONS_DIR / f"{lang}.json"
        if not path.exists():
            self._cache[lang] = {}
            return {}
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self._cache[lang] = data
        return data

    def detect_language(self, text: str) -> str:
        # Simple heuristic — production would use langdetect or LLM
        if any("\u0600" <= c <= "\u06ff" for c in text):
            return "ar"
        if any("\u4e00" <= c <= "\u9fff" for c in text):
            return "zh"
        if any("\u0900" <= c <= "\u097f" for c in text):
            return "hi"
        if any("\u0980" <= c <= "\u09ff" for c in text):
            return "bn"
        return DEFAULT_LANGUAGE

    def translate(self, key: str, lang: str = DEFAULT_LANGUAGE, **kwargs: Any) -> str:
        translations = self._load(lang)
        if key not in translations and lang != DEFAULT_LANGUAGE:
            translations = self._load(DEFAULT_LANGUAGE)
        template = translations.get(key, key)
        try:
            return template.format(**kwargs)
        except (KeyError, ValueError):
            return template

    def translate_response(self, message: str, lang: str) -> str:
        if lang == DEFAULT_LANGUAGE:
            return message
        prefix = self.translate("agent.response_prefix", lang)
        return f"{prefix}\n\n{message}"


i18n_service = I18nService()
