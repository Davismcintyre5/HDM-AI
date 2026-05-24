# ====================================================================================================
# server/routes/vibe.py (FULL - 46 endpoints)
# ====================================================================================================
from fastapi import APIRouter, Depends
from middleware.auth import get_project_auth
from services.vibe.chat_service import vibe_chat_service
from services.vibe.moderation_service import vibe_moderation_service
from services.vibe.feed_service import vibe_feed_service
from services.vibe.creation_service import vibe_creation_service
from services.vibe.monetization_service import vibe_monetization_service
from services.vibe.analytics_service import vibe_analytics_service
from services.vibe.search_service import vibe_search_service
from services.vibe.accessibility_service import vibe_accessibility_service
from services.vibe.system_service import vibe_system_service

from schemas.vibe.chat import *
from schemas.vibe.moderation import *
from schemas.vibe.feed import *
from schemas.vibe.creation import *
from schemas.vibe.monetization import *
from schemas.vibe.analytics import *
from schemas.vibe.search import *
from schemas.vibe.accessibility import *
from schemas.vibe.system import *

router = APIRouter(prefix="/vibe", tags=["Vibe AI"])
A = Depends(get_project_auth("vibe"))

# A — Chat with AI (3 endpoints, 15 features)
@router.post("/chat/message")
async def chat_msg(r: ChatMessageRequest, auth=A):
    return {"success": True, "data": await vibe_chat_service.chat_message(r.user_id, r.message, r.conversation_id)}

@router.post("/chat/assistant")
async def chat_ast(r: ChatAssistantRequest, auth=A):
    return {"success": True, "data": await vibe_chat_service.assistant(r.user_id, r.task, r.context)}

@router.post("/chat/creative")
async def chat_crt(r: ChatCreativeRequest, auth=A):
    return {"success": True, "data": await vibe_chat_service.creative(r.user_id, r.prompt, r.style)}

# B — Content Moderation (5)
@router.post("/moderation/text")
async def mod_text(r: ModTextRequest, auth=A):
    return {"success": True, "data": await vibe_moderation_service.moderate_text(r.text)}

@router.post("/moderation/image")
async def mod_img(r: ModImageRequest, auth=A):
    return {"success": True, "data": await vibe_moderation_service.moderate_image(r.image_url, r.description)}

@router.post("/moderation/video")
async def mod_vid(r: ModVideoRequest, auth=A):
    return {"success": True, "data": await vibe_moderation_service.moderate_video(r.video_url, r.description)}

@router.post("/moderation/comment")
async def mod_cmt(r: ModCommentRequest, auth=A):
    return {"success": True, "data": await vibe_moderation_service.moderate_comment(r.comment)}

@router.post("/moderation/batch")
async def mod_bat(r: ModBatchRequest, auth=A):
    return {"success": True, "data": await vibe_moderation_service.moderate_batch(r.items)}

# C — Feed & Recommendations (5)
@router.post("/feed/rank")
async def feed_rank(r: FeedRankRequest, auth=A):
    return {"success": True, "data": await vibe_feed_service.rank_feed(r.user_id, r.feed_items, r.limit)}

@router.post("/feed/personalize")
async def feed_pers(r: FeedPersonalizeRequest, auth=A):
    return {"success": True, "data": await vibe_feed_service.personalize_feed(r.user_id, r.interests)}

@router.post("/feed/trending")
async def feed_trend(r: FeedTrendingRequest, auth=A):
    return {"success": True, "data": await vibe_feed_service.trending(r.limit, r.category)}

@router.post("/recommend/users")
async def rec_users(r: RecommendUsersRequest, auth=A):
    return {"success": True, "data": await vibe_feed_service.recommend_users(r.user_id, r.limit)}

@router.post("/recommend/content")
async def rec_content(r: RecommendContentRequest, auth=A):
    return {"success": True, "data": await vibe_feed_service.recommend_content(r.user_id, r.limit)}

# D — Content Creation (4)
@router.post("/create/hashtags")
async def create_hash(r: CreateHashtagsRequest, auth=A):
    return {"success": True, "data": await vibe_creation_service.hashtags(r.content, r.count)}

@router.post("/create/caption")
async def create_cap(r: CreateCaptionRequest, auth=A):
    return {"success": True, "data": await vibe_creation_service.caption(r.image_description, r.tone, r.platform)}

@router.post("/create/description")
async def create_desc(r: CreateDescriptionRequest, auth=A):
    return {"success": True, "data": await vibe_creation_service.description(r.title, r.content_type, r.length)}

@router.post("/create/thumbnail")
async def create_thumb(r: CreateThumbnailRequest, auth=A):
    return {"success": True, "data": await vibe_creation_service.thumbnail_suggestions(r.title, r.style)}

# E — Monetization & Ads (4)
@router.post("/monetize/ad-target")
async def mon_target(r: AdTargetRequest, auth=A):
    return {"success": True, "data": await vibe_monetization_service.ad_target(r.campaign_goal, r.budget, r.audience)}

@router.post("/monetize/ad-copy")
async def mon_copy(r: AdCopyRequest, auth=A):
    return {"success": True, "data": await vibe_monetization_service.ad_copy(r.product, r.target_audience, r.platform)}

@router.post("/monetize/price-suggest")
async def mon_price(r: PriceSuggestRequest, auth=A):
    return {"success": True, "data": await vibe_monetization_service.price_suggest(r.product, r.category, r.market_data)}

@router.post("/monetize/sponsor-match")
async def mon_sponsor(r: SponsorMatchRequest, auth=A):
    return {"success": True, "data": await vibe_monetization_service.sponsor_match(r.creator_profile, r.niche)}

# F — User Analytics (3)
@router.post("/analytics/engagement")
async def ana_eng(r: EngagementRequest, auth=A):
    return {"success": True, "data": await vibe_analytics_service.engagement(r.user_id, r.period)}

@router.post("/analytics/churn")
async def ana_churn(r: ChurnRequest, auth=A):
    return {"success": True, "data": await vibe_analytics_service.churn_prediction(r.user_id, r.activity_data)}

@router.post("/analytics/growth")
async def ana_growth(r: GrowthRequest, auth=A):
    return {"success": True, "data": await vibe_analytics_service.growth_projections(r.user_id, r.metrics)}

# G — Search & Discovery (3)
@router.post("/search/semantic")
async def srch_sem(r: SemanticSearchRequest, auth=A):
    return {"success": True, "data": await vibe_search_service.semantic_search(r.query, r.limit)}

@router.post("/search/visual")
async def srch_vis(r: VisualSearchRequest, auth=A):
    return {"success": True, "data": await vibe_search_service.visual_search(r.image_url, r.limit)}

@router.post("/search/voice")
async def srch_voice(r: VoiceSearchRequest, auth=A):
    return {"success": True, "data": await vibe_search_service.voice_search(r.audio_url, r.language)}

# H — Accessibility (3)
@router.post("/accessibility/alt-text")
async def acc_alt(r: AltTextRequest, auth=A):
    return {"success": True, "data": await vibe_accessibility_service.alt_text(r.image_url, r.description)}

@router.post("/accessibility/captions")
async def acc_cap(r: CaptionsRequest, auth=A):
    return {"success": True, "data": await vibe_accessibility_service.captions(r.video_url, r.language)}

@router.post("/accessibility/text-to-speech")
async def acc_tts(r: TextToSpeechRequest, auth=A):
    return {"success": True, "data": await vibe_accessibility_service.text_to_speech(r.text, r.voice, r.language)}

# System (2)
@router.get("/health")
async def sys_health():
    return {"success": True, "data": await vibe_system_service.health()}

@router.get("/stats")
async def sys_stats(auth=A):
    return {"success": True, "data": await vibe_system_service.stats()}