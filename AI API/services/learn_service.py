# ====================================================================================================
# HDM AI Engine — Learn Service (/v1/learn/chat)
# Learning Studio | Key 2
# ====================================================================================================

import json
from typing import Dict, Any, List, Optional
from services.ai_service import ai_service, PUBLIC_PROVIDER, PUBLIC_MODEL


class LearnService:
    MAX_HISTORY = 20

    async def chat(
        self, user_id: str, message: str,
        messages: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.5, max_tokens: int = 4096,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        messages_list = []
        prompt = system_prompt or "You are HDM AI Learning Assistant. Teach, explain, and guide the student step by step."

        if data:
            data_str = json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)
            prompt += f"\n\n[CONTEXT]\n{data_str[:4000]}"

        messages_list.insert(0, {"role": "system", "content": prompt})

        if messages:
            messages_list.extend(messages[-self.MAX_HISTORY:])

        if not messages or messages[-1].get("content") != message:
            messages_list.append({"role": "user", "content": message})

        result = await ai_service.groq_chat(
            messages_list, bucket="learn",
            temperature=temperature, max_tokens=max_tokens,
        )

        return {
            "reply": result.get("reply", "Sorry, I couldn't process that."),
            "model": PUBLIC_MODEL,
            "tokens_used": result.get("tokens_used", 0),
            "provider": PUBLIC_PROVIDER,
        }


learn_service = LearnService()