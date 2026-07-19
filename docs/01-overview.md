# نظرة عامة

## ما هو Rork Toolkit؟

Rork Toolkit هو AI runtime تستخدمه التطبيقات التي تُبنى على منصة Rork. وهو منفصل عن:

1. **Rork Editor:** الـAgent الذي يكتب التطبيق.
2. **Rork Cloud:** Backend وقاعدة بيانات وخدمات Cloud.
3. **Rork Toolkit / AI runtime:** Text، Object extraction، Agent، Tools، Images، وSpeech.

## المعمارية الأقرب للأدلة

```text
Rork-generated app أو External integration
                  |
                  v
@rork-ai/toolkit-sdk أو HTTP client
                  |
                  v
https://toolkit.rork.com
  - Vercel hosting
  - Nitro-style service
  - Rork schemas/adapters
  - Vercel AI SDK protocol/core
                  |
                  v
Anthropic / OpenAI / Google
```

## الموديلات المعلنة رسميًا

وفق توثيق Rork الذي تمت مراجعته وقت إعداد المرجع:

| الوظيفة | الموديل المعلن | المزوّد |
|---|---|---|
| Agent / Assistant | Claude Sonnet 4.5 | Anthropic |
| Text Generation | GPT-5 Chat | OpenAI |
| Structured Object | GPT-4.1 | OpenAI |
| Image Generation | GPT-Image-1.5 | OpenAI |
| Image Editing | Gemini 2.5 Flash Image | Google |
| Speech-to-Text | Whisper-1 | OpenAI |
| Tool Result Summarization | Gemini 2.5 Flash | Google |

هذه الأسماء قد تتغير في Rork مع تحديث المنصة. تعامل معها كبيانات تاريخية موثقة بتاريخ الاختبار، لا كضمان دائم.

## Vercel: ما المؤكد وما غير المؤكد؟

### مؤكد

- DNS وHTTP headers يثبتان الاستضافة على Vercel.
- الـSDK المنشور يعتمد مباشرة على `ai` و`@ai-sdk/react`.
- `/agent/chat` يستخدم Vercel AI SDK UI Message Stream v1.

### غير مثبت نهائيًا

- هل Backend يمر عبر **Vercel AI Gateway** أم يتصل بالمزوّدين مباشرة.
- Runtime الداخلي الكامل لكل Endpoint.
- سياسات SLA، retention، والquotas.

## Current مقابل Legacy

### Current SDK paths

```text
POST /llm/text
POST /llm/object
POST /agent/chat
```

### Legacy path

```text
POST /text/llm/
```

المسار Legacy ما زال يعمل في الاختبارات، لكن لا يجب بدء Integration جديد عليه ما لم تكن مضطرًا للتوافق مع تطبيق قديم.

## هل API عامة ومستقرة؟

لا يوجد ما يثبت أنها Public API بعقد versioned وثابت للاستخدام الخارجي. هي خدمة رسمية داخل منظومة Rork، لكن كثيرًا من تفاصيلها تم استنتاجها من SDK والاختبارات. لذلك:

- لا تربط Production بها مباشرة من الـfrontend.
- ضع Adapter داخليًا تحت سيطرتك.
- سجّل contract tests دورية.
- جهّز fallback provider.
