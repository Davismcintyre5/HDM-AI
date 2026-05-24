"""
HDM AI - ERP Query Service
Analyzes REAL data from ERP system with rate limiting
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from services.ai_service import ai_service
from models.erp.usage_log import ERPUsageLog
from loguru import logger
import json
import hashlib
import asyncio

# Simple in-memory cache
_cache: Dict[str, tuple] = {}  # key -> (response, expiry_time)
CACHE_DURATION = timedelta(minutes=5)
MIN_REQUEST_INTERVAL = 2.0  # seconds between requests
_last_request_time = 0.0


class ERPQueryService:

    async def process_query(
        self,
        tenant_id: str,
        query: str,
        provider: str = "groq",
        context: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        
        global _last_request_time
        
        # Generate cache key from query + context + data
        cache_key = hashlib.md5(
            f"{tenant_id}:{query}:{json.dumps(context or {}, sort_keys=True)}:{json.dumps(data or {}, sort_keys=True)}".encode()
        ).hexdigest()
        
        # Check cache
        if cache_key in _cache:
            cached_response, expiry = _cache[cache_key]
            if datetime.utcnow() < expiry:
                logger.info(f"ERP cache hit for tenant={tenant_id}")
                return cached_response
        
        # Rate limiting — ensure minimum interval between requests
        now = datetime.utcnow().timestamp()
        time_since_last = now - _last_request_time
        if time_since_last < MIN_REQUEST_INTERVAL:
            wait_time = MIN_REQUEST_INTERVAL - time_since_last
            logger.info(f"ERP rate limiting — waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
        _last_request_time = datetime.utcnow().timestamp()
        
        # Build simple system prompt
        system_parts = ["You are an ERP AI assistant. Answer the user's question based on the provided context. Be concise."]

        # Add context if available
        if context:
            if context.get("source") == "landing":
                info = []
                if context.get("payment_methods"):
                    info.append(f"Payment methods: {context['payment_methods']}")
                if context.get("locations"):
                    info.append(f"Locations: {context['locations']}")
                if context.get("contacts"):
                    info.append(f"Contacts: {context['contacts']}")
                if context.get("features"):
                    info.append(f"Features: {context['features']}")
                if info:
                    system_parts.append("Business information:\n" + "\n".join(info))
            
            if context.get("source") == "tenant" and context.get("tenant_info"):
                system_parts.append(f"Tenant: {context['tenant_info']}")

        # Add data if available
        if data:
            data_str = json.dumps(data, indent=2)[:2000]  # Shorter context
            system_parts.append(f"Data for analysis:\n{data_str}")

        system_prompt = "\n\n".join(system_parts)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        logger.info(f"ERP query: tenant={tenant_id}, query='{query[:50]}', context={'yes' if context else 'no'}, data={'yes' if data else 'no'}")

        result = await ai_service.groq_chat(messages, max_tokens=500)  # Shorter responses
        
        reply = result.get("reply", "")
        if not reply and result.get("error"):
            reply = f"Service busy. Please try again shortly."
        elif not reply:
            reply = "Could not process query."

        response_data = {
            "reply": reply,
            "provider": provider,
            "tokens_used": result.get("tokens_used", 0),
            "data_analyzed": data is not None,
        }
        
        # Cache successful responses
        if result.get("success"):
            _cache[cache_key] = (response_data, datetime.utcnow() + CACHE_DURATION)

        await ERPUsageLog(
            tenant_id=tenant_id,
            endpoint="/query",
            provider=provider,
            tokens_used=result.get("tokens_used", 0),
            status="success" if result.get("success") else "error",
        ).insert()

        return response_data


erp_query_service = ERPQueryService()