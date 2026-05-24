# ====================================================================================================
# server/db/session.py — FINAL COMPLETE
# ====================================================================================================
"""
HDM AI - MongoDB Connection Manager
Motor 3.7.1 + Beanie 1.27.0
All 7 projects registered
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
from loguru import logger
from typing import Optional, Dict

from config import settings

client: Optional[AsyncIOMotorClient] = None
databases: Dict[str, AsyncIOMotorDatabase] = {}


async def init_db():
    global client, databases
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)

        databases["general"] = client.hdm_ai_general
        databases["smartpos"] = client.hdm_ai_smartpos
        databases["spark"] = client.hdm_ai_spark
        databases["vibe"] = client.hdm_ai_vibe
        databases["vault"] = client.hdm_ai_vault
        databases["erp"] = client.hdm_ai_erp
        databases["widget"] = client.hdm_ai_widget

        # General AI
        from models.core import User, APIKey, ThirdPartyKey, UsageLog
        from models.general.conversation import Conversation, Message
        from models.general.learn_session import LearnSession
        from models.general.code_execution import CodeExecution
        from models.general.file_upload import FileUpload
        await init_beanie(database=databases["general"], document_models=[
            User, APIKey, ThirdPartyKey, UsageLog,
            Conversation, Message, LearnSession, CodeExecution, FileUpload,
        ])

        # SmartPOS
        from models.smartpos.conversation import Conversation as SC, Message as SM
        from models.smartpos.alert import Alert as SA
        from models.smartpos.analytics_cache import AnalyticsCache
        await init_beanie(database=databases["smartpos"], document_models=[SC, SM, SA, AnalyticsCache])

        # Spark
        from models.spark.moderation_log import ModerationLog as SModLog
        from models.spark.safety_incident import SafetyIncident
        from models.spark.embedding_cache import EmbeddingCache
        from models.spark.voice_session import VoiceSession
        await init_beanie(database=databases["spark"], document_models=[SModLog, SafetyIncident, EmbeddingCache, VoiceSession])

        # Vibe
        from models.vibe.moderation_log import ModerationLog as VModLog
        from models.vibe.content_cache import ContentCache
        from models.vibe.feed_interaction import FeedInteraction
        from models.vibe.report_record import ReportRecord
        from models.vibe.accessibility_cache import AccessibilityCache as VAccCache
        await init_beanie(database=databases["vibe"], document_models=[VModLog, ContentCache, FeedInteraction, ReportRecord, VAccCache])

        # Vault
        from models.vault.security_scan import SecurityScan
        from models.vault.report import VaultReport
        from models.vault.threat_cache import ThreatCache
        await init_beanie(database=databases["vault"], document_models=[SecurityScan, VaultReport, ThreatCache])

        # ERP
        from models.erp.usage_log import ERPUsageLog
        from models.erp.file_extraction import FileExtraction
        from models.erp.alert_schedule import AlertSchedule
        await init_beanie(database=databases["erp"], document_models=[ERPUsageLog, FileExtraction, AlertSchedule])

        # Widget
        from models.widget.conversation import Conversation as WC, Message as WM
        from models.widget.context_cache import ContextCache as WCC
        await init_beanie(database=databases["widget"], document_models=[WC, WM, WCC])

        logger.info("MongoDB connected — 7 databases, ALL models registered (General, SmartPOS, Spark, Vibe, Vault, ERP, Widget)")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise


async def close_db():
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")


def get_database(db_name: str) -> AsyncIOMotorDatabase:
    db = databases.get(db_name)
    if db is None:
        raise ValueError(f"Database '{db_name}' not found")
    return db