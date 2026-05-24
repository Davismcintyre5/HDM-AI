# ====================================================================================================
# server/services/widget/context_service.py
# ====================================================================================================
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from models.widget.context_cache import ContextCache
from loguru import logger

class WidgetContextService:
    DEFAULT_CONTEXTS = {
        "hdm_portfolio": {
            "company": "HDM AI",
            "services": "AI Development, POS Systems, Cybersecurity, ERP Solutions",
            "apps": "SmartPOS, Spark Messenger, Vibe Social, HDM Vault, ERP Gateway, DocuSoft, Portfolio",
            "projects": "Enterprise AI, Cloud Infrastructure, Mobile Apps, Web Platforms",
            "contact": "contact@hdmai.com",
        },
        "docusoft": {
            "features": "PDF Editing, E-Signatures, Document Management, Cloud Storage, OCR, File Conversion",
            "pricing": "Free tier available, Pro at $9.99/month, Enterprise custom",
            "support": "support@docusoft.com",
        },
    }

    async def get_context(self, source: str) -> Dict[str, Any]:
        # Check cache
        cached = await ContextCache.find_one(ContextCache.source == source)
        if cached and cached.expires_at and cached.expires_at > datetime.utcnow():
            return cached.context_data

        # Return defaults
        context = self.DEFAULT_CONTEXTS.get(source, {})
        await ContextCache(source=source, context_data=context, expires_at=datetime.utcnow() + timedelta(hours=24)).insert()
        return context

    async def update_context(self, source: str, context_data: Dict[str, Any]) -> None:
        await ContextCache.find_one(ContextCache.source == source).delete()
        await ContextCache(source=source, context_data=context_data, expires_at=datetime.utcnow() + timedelta(hours=24)).insert()

widget_context_service = WidgetContextService()