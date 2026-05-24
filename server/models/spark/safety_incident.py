# ====================================================================================================
# server/models/spark/safety_incident.py
# ====================================================================================================
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional, List

class SafetyIncident(Document):
    user_id: Indexed(str)
    severity: str = "medium"  # low, medium, high, critical
    incident_type: str  # self_harm, child_safety, threats, harassment
    description: str
    resources_provided: List[str] = []
    resolved: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    class Settings: name = "spark_safety_incidents"