from services.ai_service import ai_service
import json

class VerificationService:
    async def scan_document(self, imageUrl: str) -> dict:
        prompt = f"""Analyze this student ID document image: {imageUrl}
Extract: full name, registration number (format: RVNP/YYYY/XXXXX), document type, expiry date.
Check if it's a valid student ID.
Return JSON: {{"valid": true/false, "extractedName": "string or null", "extractedRegNo": "string or null", "confidence": 0.0-1.0, "documentType": "student_id/unknown", "expiryDate": "string or null", "reason": "not_a_student_id/expired/unreadable/fake_document or null", "warnings": []}}"""

        result = await ai_service.groq_chat([{"role": "user", "content": prompt}], temperature=0.1, max_tokens=300, module="rvnp")
        try:
            return json.loads(result.get("reply", "{}"))
        except:
            return {"valid": False, "extractedName": None, "extractedRegNo": None, "confidence": 0, "documentType": "unknown", "reason": "unreadable", "warnings": ["ai_parse_failed"]}

verification_service = VerificationService()