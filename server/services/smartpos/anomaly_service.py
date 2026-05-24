# ====================================================================================================
# server/services/smartpos/anomaly_service.py
# ====================================================================================================
from typing import Dict, Any, List
from services.ai_service import ai_service
from loguru import logger
import json

class AnomalyService:
    async def detect(self, business_id: str, data: List[dict] = None) -> Dict[str, Any]:
        if data:
            prompt = f"""You are a POS anomaly detection AI. Analyze this REAL data for anomalies.

Data: {json.dumps(data)[:3000]}

Return JSON: {{"anomalies": [{{"description": "specific anomaly", "severity": "low/medium/high", "data_point": {{...}}}}]}}"""
        else:
            return {"anomalies": [], "count": 0, "message": "No data provided. Send transaction/sales data for anomaly detection."}

        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.2, max_tokens=400)
        try:
            parsed = json.loads(result.get("reply", "{}"))
            anomalies = parsed.get("anomalies", [])
            return {"anomalies": anomalies, "count": len(anomalies)}
        except:
            return {"anomalies": [], "count": 0}

anomaly_service = AnomalyService()