from fastapi import APIRouter
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

@router.post("/chat/ask")
async def c_ask(r: ChatAskRequest): return {"success": True, "data": await spark_chat_service.ask(r.user_id, r.message, r.language, r.data)}
@router.post("/chat/translate")
async def c_translate(r: ChatTranslateRequest): return {"success": True, "data": await spark_chat_service.translate(r.text, r.target_language, r.data)}
@router.post("/chat/rewrite")
async def c_rewrite(r: ChatRewriteRequest): return {"success": True, "data": await spark_chat_service.rewrite(r.text, r.style, r.data)}
@router.post("/chat/draft")
async def c_draft(r: ChatDraftRequest): return {"success": True, "data": await spark_chat_service.draft(r.prompt, r.tone, r.data)}
@router.post("/chat/explain")
async def c_explain(r: ChatExplainRequest): return {"success": True, "data": await spark_chat_service.explain(r.text, r.level, r.data)}
@router.post("/chat/summarize")
async def c_summarize(r: ChatSummarizeRequest): return {"success": True, "data": await spark_chat_service.summarize(r.text, r.max_length, r.data)}
@router.post("/chat/summarize-unread")
async def c_summarize_unread(r: dict): return {"success": True, "data": await spark_chat_service.summarize_unread(r.get("messages", []), r.get("data"))}
@router.post("/chat/voice")
async def c_voice(r: ChatVoiceRequest): return {"success": True, "data": await spark_chat_service.voice_chat(r.audio_base64, r.language, r.data)}
@router.post("/chat/emoji-suggest")
async def c_emoji(r: ChatEmojiRequest): return {"success": True, "data": await spark_chat_service.emoji_suggest(r.message, r.count, r.data)}
@router.post("/chat/autocomplete")
async def c_autocomplete(r: ChatAutocompleteRequest): return {"success": True, "data": await spark_chat_service.autocomplete(r.partial_text, r.max_suggestions, r.data)}
@router.post("/chat/tone-detect")
async def c_tone(r: ChatToneRequest): return {"success": True, "data": await spark_chat_service.tone_detect(r.text, r.data)}
@router.post("/chat/format")
async def c_format(r: ChatFormatRequest): return {"success": True, "data": await spark_chat_service.format_message(r.text, r.format_type, r.data)}
@router.post("/chat/quote-reply")
async def c_quote(r: ChatQuoteRequest): return {"success": True, "data": await spark_chat_service.quote_reply(r.original_message, r.reply, r.data)}
@router.post("/chat/poll-generate")
async def c_poll(r: ChatPollRequest): return {"success": True, "data": await spark_chat_service.poll_generate(r.topic, r.options_count, r.data)}
@router.post("/chat/context-reply")
async def c_context(r: ChatContextReplyRequest): return {"success": True, "data": await spark_chat_service.context_reply(r.message, r.context_messages, r.data)}

@router.post("/smart/reply")
async def s_reply(r: SmartReplyRequest): return {"success": True, "data": await smart_reply_service.reply(r.message, r.count, r.tone, r.data)}
@router.post("/smart/quick-reply")
async def s_quick(r: SmartQuickReplyRequest): return {"success": True, "data": await smart_reply_service.quick_reply(r.message, r.count, r.data)}
@router.post("/smart/reply-context")
async def s_ctx(r: SmartReplyContextRequest): return {"success": True, "data": await smart_reply_service.reply_with_context(r.message, r.previous_messages, r.data)}
@router.post("/smart/reply-tone")
async def s_tone(r: SmartReplyToneRequest): return {"success": True, "data": await smart_reply_service.reply_with_tone(r.message, r.target_tone, r.data)}
@router.post("/smart/reply-language")
async def s_lang(r: SmartReplyLanguageRequest): return {"success": True, "data": await smart_reply_service.reply_in_language(r.message, r.language, r.data)}

@router.post("/intel/sentiment")
async def i_sent(r: IntelSentimentRequest): return {"success": True, "data": await intelligence_service.sentiment(r.text, r.data)}
@router.post("/intel/keywords")
async def i_kw(r: IntelKeywordsRequest): return {"success": True, "data": await intelligence_service.keywords(r.text, r.count, r.data)}
@router.post("/intel/entities")
async def i_ent(r: IntelEntitiesRequest): return {"success": True, "data": await intelligence_service.entities(r.text, r.data)}
@router.post("/intel/read-receipt")
async def i_read(r: IntelReadReceiptRequest): return {"success": True, "data": await intelligence_service.read_receipt_prediction(r.message, r.sender_history, r.data)}
@router.post("/intel/urgency")
async def i_urg(r: IntelUrgencyRequest): return {"success": True, "data": await intelligence_service.urgency(r.message, r.data)}
@router.post("/intel/language-detect")
async def i_lang(r: IntelLanguageRequest): return {"success": True, "data": await intelligence_service.language_detect(r.text, r.data)}

@router.post("/safety/spam")
async def sf_spam(r: SafetySpamRequest): return {"success": True, "data": await moderation_service.check_spam(r.text, r.user_id, r.data)}
@router.post("/safety/hate-speech")
async def sf_hate(r: SafetyHateRequest): return {"success": True, "data": await moderation_service.check_hate_speech(r.text, r.data)}
@router.post("/safety/nsfw")
async def sf_nsfw(r: SafetyNSFWRequest): return {"success": True, "data": await moderation_service.check_nsfw(r.content, r.content_type, r.data)}
@router.post("/safety/child-safety")
async def sf_child(r: SafetyChildRequest): return {"success": True, "data": await moderation_service.check_child_safety(r.content, r.data)}
@router.post("/safety/impersonation")
async def sf_imp(r: SafetyImpersonationRequest): return {"success": True, "data": await moderation_service.check_impersonation(r.text, r.claimed_identity, r.data)}
@router.post("/safety/self-harm")
async def sf_self(r: SafetySelfHarmRequest): return {"success": True, "data": await moderation_service.check_self_harm(r.text, r.user_id, r.data)}
@router.post("/safety/link-check")
async def sf_link(r: SafetyLinkRequest): return {"success": True, "data": await moderation_service.check_link(r.url, r.data)}

@router.post("/group/summary")
async def g_sum(r: GroupSummaryRequest): return {"success": True, "data": await group_service.summarize(r.messages, r.max_length, r.data)}
@router.post("/group/highlights")
async def g_high(r: GroupHighlightsRequest): return {"success": True, "data": await group_service.highlights(r.messages, r.count, r.data)}
@router.post("/group/poll-results")
async def g_poll(r: GroupPollResultsRequest): return {"success": True, "data": await group_service.poll_results(r.poll_data, r.data)}
@router.post("/group/mention-suggest")
async def g_ment(r: GroupMentionRequest): return {"success": True, "data": await group_service.mention_suggest(r.partial_name, r.group_members, r.data)}
@router.post("/group/activity-recap")
async def g_recap(r: GroupRecapRequest): return {"success": True, "data": await group_service.activity_recap(r.messages, r.period, r.data)}

@router.post("/privacy/advisor")
async def p_adv(r: PrivacyAdvisorRequest): return {"success": True, "data": await privacy_service.advisor(r.concern, r.context, r.data)}
@router.post("/privacy/data-leak")
async def p_leak(r: PrivacyLeakRequest): return {"success": True, "data": await privacy_service.data_leak_check(r.message, r.scan_type, r.data)}
@router.post("/privacy/encrypt-suggest")
async def p_enc(r: PrivacyEncryptRequest): return {"success": True, "data": await privacy_service.encrypt_suggest(r.message, r.data)}
@router.post("/privacy/audit-log")
async def p_audit(r: PrivacyAuditRequest): return {"success": True, "data": await privacy_service.audit_log(r.user_id, r.period, r.data)}

@router.post("/search/semantic")
async def sr_sem(r: SemanticSearchRequest): return {"success": True, "data": await spark_search_service.semantic_search(r.query, r.documents, r.limit, r.data)}
@router.post("/search/messages")
async def sr_msg(r: MessageSearchRequest): return {"success": True, "data": await spark_search_service.message_search(r.query, r.user_id, r.limit, r.data)}
@router.post("/search/contacts")
async def sr_con(r: ContactSearchRequest): return {"success": True, "data": await spark_search_service.contact_search(r.query, r.user_id, r.limit, r.data)}

@router.get("/health")
async def sys_health(): return {"success": True, "data": await system_service.health()}
@router.get("/stats")
async def sys_stats(): return {"success": True, "data": await system_service.stats()}

@router.post("/public/chat")
async def public_chat(r: ChatAskRequest):
    return {"success": True, "data": await spark_chat_service.ask(r.user_id or "public", r.message, r.language or "en", r.data, feature="public")}