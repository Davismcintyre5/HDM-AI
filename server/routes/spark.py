# ====================================================================================================
# 15. server/routes/spark.py — COMPLETE (46 endpoints)
# ====================================================================================================
from fastapi import APIRouter, Depends
from middleware.auth import get_project_auth
from services.spark.chat_service import spark_chat_service
from services.spark.smart_reply_service import smart_reply_service
from services.spark.intelligence_service import intelligence_service
from services.spark.moderation_service import moderation_service
from services.spark.group_service import group_service
from services.spark.privacy_service import privacy_service
from services.spark.search_service import spark_search_service
from services.spark.system_service import system_service

from schemas.spark.chat import *
from schemas.spark.smart_reply import *
from schemas.spark.intelligence import *
from schemas.spark.moderation import *
from schemas.spark.group import *
from schemas.spark.privacy import *
from schemas.spark.search import *

router = APIRouter(prefix="/spark", tags=["Spark AI"])
A = Depends(get_project_auth("spark"))

# A1 — Chat with HDM AI (15)
@router.post("/chat/ask")
async def c_ask(r: ChatAskRequest, auth=A):
    return {"success": True, "data": await spark_chat_service.ask(r.user_id, r.message, r.language, r.data)}

@router.post("/chat/translate")
async def c_translate(r: ChatTranslateRequest, auth=A):
    return {"success": True, "data": await spark_chat_service.translate(r.text, r.target_language, r.data)}

@router.post("/chat/rewrite")
async def c_rewrite(r: ChatRewriteRequest, auth=A):
    return {"success": True, "data": await spark_chat_service.rewrite(r.text, r.style, r.data)}

@router.post("/chat/draft")
async def c_draft(r: ChatDraftRequest, auth=A):
    return {"success": True, "data": await spark_chat_service.draft(r.prompt, r.tone, r.data)}

@router.post("/chat/explain")
async def c_explain(r: ChatExplainRequest, auth=A):
    return {"success": True, "data": await spark_chat_service.explain(r.text, r.level, r.data)}

@router.post("/chat/summarize")
async def c_summarize(r: ChatSummarizeRequest, auth=A):
    return {"success": True, "data": await spark_chat_service.summarize(r.text, r.max_length, r.data)}

@router.post("/chat/summarize-unread")
async def c_summarize_unread(r: dict, auth=A):
    return {"success": True, "data": await spark_chat_service.summarize_unread(r.get("messages", []), r.get("data"))}

@router.post("/chat/voice")
async def c_voice(r: ChatVoiceRequest, auth=A):
    return {"success": True, "data": await spark_chat_service.voice_chat(r.audio_base64, r.language, r.data)}

@router.post("/chat/emoji-suggest")
async def c_emoji(r: ChatEmojiRequest, auth=A):
    return {"success": True, "data": await spark_chat_service.emoji_suggest(r.message, r.count, r.data)}

@router.post("/chat/autocomplete")
async def c_autocomplete(r: ChatAutocompleteRequest, auth=A):
    return {"success": True, "data": await spark_chat_service.autocomplete(r.partial_text, r.max_suggestions, r.data)}

@router.post("/chat/tone-detect")
async def c_tone(r: ChatToneRequest, auth=A):
    return {"success": True, "data": await spark_chat_service.tone_detect(r.text, r.data)}

@router.post("/chat/format")
async def c_format(r: ChatFormatRequest, auth=A):
    return {"success": True, "data": await spark_chat_service.format_message(r.text, r.format_type, r.data)}

@router.post("/chat/quote-reply")
async def c_quote(r: ChatQuoteRequest, auth=A):
    return {"success": True, "data": await spark_chat_service.quote_reply(r.original_message, r.reply, r.data)}

@router.post("/chat/poll-generate")
async def c_poll(r: ChatPollRequest, auth=A):
    return {"success": True, "data": await spark_chat_service.poll_generate(r.topic, r.options_count, r.data)}

@router.post("/chat/context-reply")
async def c_context(r: ChatContextReplyRequest, auth=A):
    return {"success": True, "data": await spark_chat_service.context_reply(r.message, r.context_messages, r.data)}

# A2 — Smart Reply (5)
@router.post("/smart/reply")
async def s_reply(r: SmartReplyRequest, auth=A):
    return {"success": True, "data": await smart_reply_service.reply(r.message, r.count, r.tone, r.data)}

@router.post("/smart/quick-reply")
async def s_quick(r: SmartQuickReplyRequest, auth=A):
    return {"success": True, "data": await smart_reply_service.quick_reply(r.message, r.count, r.data)}

@router.post("/smart/reply-context")
async def s_ctx(r: SmartReplyContextRequest, auth=A):
    return {"success": True, "data": await smart_reply_service.reply_with_context(r.message, r.previous_messages, r.data)}

@router.post("/smart/reply-tone")
async def s_tone(r: SmartReplyToneRequest, auth=A):
    return {"success": True, "data": await smart_reply_service.reply_with_tone(r.message, r.target_tone, r.data)}

@router.post("/smart/reply-language")
async def s_lang(r: SmartReplyLanguageRequest, auth=A):
    return {"success": True, "data": await smart_reply_service.reply_in_language(r.message, r.language, r.data)}

# A3 — Message Intelligence (6)
@router.post("/intel/sentiment")
async def i_sent(r: IntelSentimentRequest, auth=A):
    return {"success": True, "data": await intelligence_service.sentiment(r.text, r.data)}

@router.post("/intel/keywords")
async def i_kw(r: IntelKeywordsRequest, auth=A):
    return {"success": True, "data": await intelligence_service.keywords(r.text, r.count, r.data)}

@router.post("/intel/entities")
async def i_ent(r: IntelEntitiesRequest, auth=A):
    return {"success": True, "data": await intelligence_service.entities(r.text, r.data)}

@router.post("/intel/read-receipt")
async def i_read(r: IntelReadReceiptRequest, auth=A):
    return {"success": True, "data": await intelligence_service.read_receipt_prediction(r.message, r.sender_history, r.data)}

@router.post("/intel/urgency")
async def i_urg(r: IntelUrgencyRequest, auth=A):
    return {"success": True, "data": await intelligence_service.urgency(r.message, r.data)}

@router.post("/intel/language-detect")
async def i_lang(r: IntelLanguageRequest, auth=A):
    return {"success": True, "data": await intelligence_service.language_detect(r.text, r.data)}

# A4 — Safety & Moderation (7)
@router.post("/safety/spam")
async def sf_spam(r: SafetySpamRequest, auth=A):
    return {"success": True, "data": await moderation_service.check_spam(r.text, r.user_id, r.data)}

@router.post("/safety/hate-speech")
async def sf_hate(r: SafetyHateRequest, auth=A):
    return {"success": True, "data": await moderation_service.check_hate_speech(r.text, r.data)}

@router.post("/safety/nsfw")
async def sf_nsfw(r: SafetyNSFWRequest, auth=A):
    return {"success": True, "data": await moderation_service.check_nsfw(r.content, r.content_type, r.data)}

@router.post("/safety/child-safety")
async def sf_child(r: SafetyChildRequest, auth=A):
    return {"success": True, "data": await moderation_service.check_child_safety(r.content, r.data)}

@router.post("/safety/impersonation")
async def sf_imp(r: SafetyImpersonationRequest, auth=A):
    return {"success": True, "data": await moderation_service.check_impersonation(r.text, r.claimed_identity, r.data)}

@router.post("/safety/self-harm")
async def sf_self(r: SafetySelfHarmRequest, auth=A):
    return {"success": True, "data": await moderation_service.check_self_harm(r.text, r.user_id, r.data)}

@router.post("/safety/link-check")
async def sf_link(r: SafetyLinkRequest, auth=A):
    return {"success": True, "data": await moderation_service.check_link(r.url, r.data)}

# A5 — Group Chat AI (5)
@router.post("/group/summary")
async def g_sum(r: GroupSummaryRequest, auth=A):
    return {"success": True, "data": await group_service.summarize(r.messages, r.max_length, r.data)}

@router.post("/group/highlights")
async def g_high(r: GroupHighlightsRequest, auth=A):
    return {"success": True, "data": await group_service.highlights(r.messages, r.count, r.data)}

@router.post("/group/poll-results")
async def g_poll(r: GroupPollResultsRequest, auth=A):
    return {"success": True, "data": await group_service.poll_results(r.poll_data, r.data)}

@router.post("/group/mention-suggest")
async def g_ment(r: GroupMentionRequest, auth=A):
    return {"success": True, "data": await group_service.mention_suggest(r.partial_name, r.group_members, r.data)}

@router.post("/group/activity-recap")
async def g_recap(r: GroupRecapRequest, auth=A):
    return {"success": True, "data": await group_service.activity_recap(r.messages, r.period, r.data)}

# A6 — Privacy & Security (4)
@router.post("/privacy/advisor")
async def p_adv(r: PrivacyAdvisorRequest, auth=A):
    return {"success": True, "data": await privacy_service.advisor(r.concern, r.context, r.data)}

@router.post("/privacy/data-leak")
async def p_leak(r: PrivacyLeakRequest, auth=A):
    return {"success": True, "data": await privacy_service.data_leak_check(r.message, r.scan_type, r.data)}

@router.post("/privacy/encrypt-suggest")
async def p_enc(r: PrivacyEncryptRequest, auth=A):
    return {"success": True, "data": await privacy_service.encrypt_suggest(r.message, r.data)}

@router.post("/privacy/audit-log")
async def p_audit(r: PrivacyAuditRequest, auth=A):
    return {"success": True, "data": await privacy_service.audit_log(r.user_id, r.period, r.data)}

# A7 — Smart Search (3)
@router.post("/search/semantic")
async def sr_sem(r: SemanticSearchRequest, auth=A):
    return {"success": True, "data": await spark_search_service.semantic_search(r.query, r.documents, r.limit, r.data)}

@router.post("/search/messages")
async def sr_msg(r: MessageSearchRequest, auth=A):
    return {"success": True, "data": await spark_search_service.message_search(r.query, r.user_id, r.limit, r.data)}

@router.post("/search/contacts")
async def sr_con(r: ContactSearchRequest, auth=A):
    return {"success": True, "data": await spark_search_service.contact_search(r.query, r.user_id, r.limit, r.data)}

# System (2)
@router.get("/health")
async def sys_health():
    return {"success": True, "data": await system_service.health()}

@router.get("/stats")
async def sys_stats(auth=A):
    return {"success": True, "data": await system_service.stats()}