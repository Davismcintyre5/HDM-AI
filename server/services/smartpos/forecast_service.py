# ====================================================================================================
# server/services/smartpos/forecast_service.py
# ====================================================================================================
from typing import Dict, Any
from services.ai_service import ai_service
from loguru import logger
import json

class ForecastService:
    async def forecast(self, business_id: str, forecast_type: str, period: str = "next_month", data: dict = None, product_ids: list = None) -> Dict[str, Any]:
        if data:
            prompt = f"""You are a POS forecasting AI. Based on this REAL historical data, forecast {forecast_type} for {period}.

Historical data: {json.dumps(data)[:3000]}

Return JSON: {{"forecast": [{{"item": "...", "prediction": "...", "confidence": 0.0}}], "summary": "key forecast insights"}}"""
        else:
            return {"type": forecast_type, "forecast": [], "summary": "No historical data provided. Send past sales/inventory data for forecasting."}

        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.3, max_tokens=600)
        try:
            parsed = json.loads(result.get("reply", "{}"))
            return {"type": forecast_type, "forecast": parsed.get("forecast", []), "summary": parsed.get("summary", "")}
        except:
            return {"type": forecast_type, "forecast": [], "summary": "Could not generate forecast."}

forecast_service = ForecastService()