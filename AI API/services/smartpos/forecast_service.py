from typing import Dict, Any
from services.ai_service import ai_service
import json

class ForecastService:
    async def forecast(self, business_id: str, forecast_type: str, period: str = "next_month", data: dict = None, product_ids: list = None) -> Dict[str, Any]:
        if not data:
            return {"type": forecast_type, "forecast": [], "summary": "No historical data provided."}

        parts = [f"You are a POS forecasting AI. Based on REAL historical data, forecast {forecast_type} for {period}.", "", "--- REAL HISTORICAL DATA ---"]
        if "current_stock" in data:
            parts.append(f"\nCURRENT STOCK LEVELS:")
            for item in data["current_stock"][:10]: parts.append(f"  • {item.get('product','?')}: Stock {item.get('stock',0)}, Daily Sales {item.get('daily_sales',0)}")
        if "historical_sales" in data:
            parts.append(f"\nHISTORICAL SALES:")
            for sale in data["historical_sales"][:30]: parts.append(f"  • {sale.get('date','?')}: {sale.get('sales',0)}")
        parts.append("\n\nReturn JSON: {\"forecast\": [{\"item\": \"name\", \"prediction\": \"...\", \"confidence\": 0.0}], \"summary\": \"...\"}")

        prompt = "\n".join(parts)
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.3, max_tokens=600, module="smartpos")
        try:
            parsed = json.loads(result.get("reply", "{}"))
            return {"type": forecast_type, "forecast": parsed.get("forecast", []), "summary": parsed.get("summary", "")}
        except:
            return {"type": forecast_type, "forecast": [], "summary": "Could not generate forecast."}

forecast_service = ForecastService()