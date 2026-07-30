require('./dnsSet');
require('dotenv').config();

const mongoose = require('mongoose');
const SupportContent = require('../models/SupportContent');

const data = {
  supportEmail: 'info@hdmdevelopers.com',
  supportPhone: '+254768784909',
  supportWhatsApp: '+254768784909',
  appDownloadUrl: 'https://github.com/Davismcintyre5/docusoft-files/releases/download/HDM-Apps/HDM.AI.apk',
  docsUrl: 'https://hdmai.pxxl.click/docs',
  faq: [
    { question: 'What is HDM AI?', answer: 'HDM AI is a central intelligence platform that provides chat, content analysis, code execution, image generation, and learning tools through one unified API.' },
    { question: 'How do I create an API key?', answer: 'Go to Settings > API Keys tab > Outbound section. Click New Key, give it a name, and save. The full key is shown only once — copy it immediately.' },
    { question: 'What are the rate limits?', answer: 'Each API key allows 1,440 requests per day (approximately 1 per minute). Burst up to 30 requests per minute is supported.' },
    { question: 'Can I upload files for analysis?', answer: 'Yes. In the Chat page, click the paperclip icon to attach files. Supported formats: PDF, TXT, CSV, JSON, HTML, and code files.' },
    { question: 'How does the Learning Studio work?', answer: 'Create a topic and AI generates a structured curriculum with subtopics. Learn each subtopic, take quizzes, review flashcards, and track your progress. Your session is saved automatically.' },
    { question: 'What is the Public Chat API?', answer: 'It allows you to create a custom-branded AI assistant by providing a system prompt. Use endpoint POST /projects/general/public-chat with your API key.' },
    { question: 'How do I connect my business system?', answer: 'Use your project API key to call the chat endpoint. Send your business data in the data field and the AI will analyze it in real time.' },
    { question: 'Is there a mobile app?', answer: 'Yes. Download the Android APK from the Support > Links page, or scan the QR code on the landing page.' },
    { question: 'How do I change my password?', answer: 'Go to Settings > Profile > Change Password. Enter your current password and your new password.' },
    { question: 'How do I get help or report an issue?', answer: 'Contact us via email, phone, or WhatsApp. All contact details are on the Support > Contact page. We respond within 24 hours.' },
  ],
  apiGuide: `# HDM AI — API Integration Guide

## Base URL
https://hdmaiserver.pxxl.click/api/v1

## Authentication
All requests require an API key in the Authorization header:
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

## Public Chat API
Create a custom-branded AI assistant with a system prompt.

Endpoint: POST /projects/general/public-chat

Request:
{
  "message": "What do you offer?",
  "system_prompt": "You are MyShop Assistant. We sell shoes, bags, and watches."
}

Response:
{
  "success": true,
  "data": {
    "reply": "We sell shoes, bags, and watches!",
    "tokens_used": 45,
    "provider": "hdm-ai"
  }
}

## Examples

Real Estate:
{
  "message": "What properties are available?",
  "system_prompt": "You are Prime Properties. We have 3 listings: Westlands 8M, Kilimani 3.5M, Karen 25M."
}

Restaurant:
{
  "message": "What is on the menu?",
  "system_prompt": "You are Mamma Mia Restaurant. Menu: Pizza 800, Pasta 950, Tiramisu 450. Open 10am-10pm."
}

## Error Handling
All errors return:
{
  "success": false,
  "error": "Error message"
}

Common status codes:
- 200: Success
- 401: Invalid API key
- 429: Rate limit exceeded
- 500: AI engine unavailable

## Rate Limits
- 1,440 requests per day per API key
- 30 requests per minute burst
- 60-second timeout per request

## Need Help?
Contact support through the Contact tab above.`,
};

mongoose.connect(process.env.MONGODB_URL).then(async () => {
  await SupportContent.findOneAndUpdate({ type: 'support_content' }, data, { upsert: true, new: true });
  console.log('Support content seeded');
  process.exit();
});