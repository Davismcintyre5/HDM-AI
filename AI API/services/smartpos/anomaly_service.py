from typing import Dict, Any, List
from services.ai_service import ai_service
import json

class AnomalyService:
    async def detect(self, business_id: str, data: List[dict] = None) -> Dict[str, Any]:
        if not data:
            return {"anomalies": [], "count": 0, "message": "No data provided."}

        parts = ["You are a POS anomaly detection AI. Analyze this REAL transaction data for anomalies.", "", "--- REAL TRANSACTION DATA ---"]
        for i, entry in enumerate(data[:50]): parts.append(f"  [{i+1}] {json.dumps(entry)}")
        parts.append(f"\n\nTotal records: {len(data)}")
        parts.append('\n\nReturn JSON: {"anomalies": [{"description": "specific anomaly", "severity": "low/medium/high", "data_point": {...}}]}')

        prompt = "\n".join(parts)
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.2, max_tokens=400, module="smartpos")
        try:
            parsed = json.loads(result.get("reply", "{}"))
            anomalies = parsed.get("anomalies", [])
            return {"anomalies": anomalies, "count": len(anomalies)}
        except:
            return {"anomalies": [], "count": 0}

anomaly_service = AnomalyService()