# ====================================================================================================
# server/schemas/spark/group.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import List, Optional

class GroupSummaryRequest(BaseModel):
    messages: List[dict]
    max_length: int = 300

class GroupHighlightsRequest(BaseModel):
    messages: List[dict]
    count: int = 5

class GroupPollResultsRequest(BaseModel):
    poll_data: dict

class GroupMentionRequest(BaseModel):
    partial_name: str
    group_members: List[str]

class GroupRecapRequest(BaseModel):
    messages: List[dict]
    period: str = "last_24h"