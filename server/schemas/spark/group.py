# ====================================================================================================
# 5. server/schemas/spark/group.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import List, Optional

class GroupSummaryRequest(BaseModel):
    messages: List[dict]
    max_length: int = 300
    data: Optional[dict] = None

class GroupHighlightsRequest(BaseModel):
    messages: List[dict]
    count: int = 5
    data: Optional[dict] = None

class GroupPollResultsRequest(BaseModel):
    poll_data: dict
    data: Optional[dict] = None

class GroupMentionRequest(BaseModel):
    partial_name: str
    group_members: List[str]
    data: Optional[dict] = None

class GroupRecapRequest(BaseModel):
    messages: List[dict]
    period: str = "last_24h"
    data: Optional[dict] = None