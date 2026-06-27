from typing import Dict, Any
from services.ai_service import ai_service

class ReportService:
    async def generate(self, business_id: str, report_type: str, period: str = "this_month") -> Dict[str, Any]:
        prompt = f"""You are a POS report generator. Generate a {report_type} report for {period}.
Format as a professional business report with sections: Overview, Key Metrics, Details, Recommendations."""
        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.4, max_tokens=1500, module="smartpos")
        return {"report_text": result.get("reply", ""), "format": "text"}

report_service = ReportService()