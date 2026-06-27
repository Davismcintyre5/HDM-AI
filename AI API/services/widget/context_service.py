from typing import Dict, Any

class WidgetContextService:
    DEFAULT_CONTEXTS = {
        "hdm_portfolio": {
            "company": {
                "name": "HDM Developers",
                "tagline": "Building Digital Solutions for Africa",
                "description": "We are a Kenyan-based software development company specializing in web apps, mobile apps, POS systems, and AI solutions.",
                "email": "info@hdmdevelopers.com",
                "phone": "+254 700 000 000",
                "whatsapp": "+254 700 000 000",
                "address": "Nairobi, Kenya"
            },
            "services": [
                {"title": "Web Development", "description": "Full-stack web applications using modern technologies"},
                {"title": "Mobile Apps", "description": "Native and cross-platform mobile applications"},
                {"title": "AI Solutions", "description": "Custom AI integrations and chatbots"},
                {"title": "POS Systems", "description": "Point of sale systems for retail businesses"}
            ],
            "socialLinks": {
                "github": "https://github.com/hdmdevelopers",
                "linkedin": "https://linkedin.com/company/hdmdevelopers",
                "twitter": "https://twitter.com/hdmdevelopers",
                "website": "https://hdmdevelopers.com"
            }
        },
        "docusoft": {
            "business": {
                "name": "DocuSoft Store",
                "phone": "0768784909",
                "hours": {
                    "monday": "9am-5pm", "tuesday": "9am-5pm", "wednesday": "9am-5pm",
                    "thursday": "9am-5pm", "friday": "9am-5pm", "saturday": "10am-3pm", "sunday": "Closed"
                }
            },
            "pricing": {
                "priceRange": {"min": 50, "max": 5000},
                "currency": "KES"
            },
            "paymentMethods": [
                {"name": "M-Pesa STK Push", "description": "Instant payment via phone prompt"},
                {"name": "Manual Payment", "description": "Send money and upload screenshot for verification"}
            ],
            "howToPurchase": "Browse items → Select what you need → Pay if it's paid → Download instantly"
        },
    }

    async def get_context(self, source: str) -> Dict[str, Any]:
        return self.DEFAULT_CONTEXTS.get(source, {})

widget_context_service = WidgetContextService()