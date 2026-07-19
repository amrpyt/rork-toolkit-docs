# المصادر ودرجات الثقة

## تصنيف الأدلة

| العلامة | المعنى |
|---|---|
| **OFFICIAL** | منشور في توثيق الجهة الرسمية |
| **SDK** | مستخرج من حزمة `@rork-ai/toolkit-sdk` المنشورة |
| **MEASURED** | تم قياسه بطلب HTTP فعلي |
| **INFERENCE** | استنتاج هندسي تدعمه الأدلة لكنه غير مثبت من كود السيرفر |

## مصادر Rork

- الموقع: <https://rork.com/>
- التوثيق: <https://docs.rork.com/>
- Documentation index: <https://docs.rork.com/llms.txt>
- Backend/Toolkit overview: <https://docs.rork.com/building-complex-apps/backend/what-is-rork-toolkit>
- Build vs Cloud credits: <https://docs.rork.com/billing/build-credits-vs-cloud-credits>
- npm package: <https://www.npmjs.com/package/@rork-ai/toolkit-sdk>

## مصادر Vercel AI SDK

- AI SDK documentation: <https://ai-sdk.dev/docs>
- UI stream protocol: <https://ai-sdk.dev/docs/ai-sdk-ui/stream-protocol>
- `useChat`: <https://ai-sdk.dev/docs/reference/ai-sdk-ui/use-chat>
- Core reference: <https://ai-sdk.dev/docs/reference/ai-sdk-core>
- GitHub source: <https://github.com/vercel/ai>

## مصادر Chatwoot

- Chatwoot documentation: <https://www.chatwoot.com/docs/>
- GitHub repository: <https://github.com/chatwoot/chatwoot>
- Captain documentation: <https://www.chatwoot.com/hc/user-guide-captain>

راجع نسخة Chatwoot المثبتة عندك لأن دعم custom endpoints وcustom tools يتطور بين الإصدارات.

## ما هو مؤكد بدرجة عالية؟

| المعلومة | المصدر | الثقة |
|---|---|---:|
| Toolkit تابع رسميًا لـRork | OFFICIAL + site traffic | 100% |
| الاستضافة على Vercel | DNS + headers | 100% |
| Agent client يستخدم Vercel AI SDK | SDK imports/code | 100% |
| `/agent/chat` يستخدم UI Message Stream v1 | SDK + MEASURED | 100% |
| Rork external tool schema تستخدم `jsonSchema` | SDK + MEASURED | 100% |
| Current SDK uses `/llm/text` and `/llm/object` | SDK + MEASURED | 100% |
| `/text/llm/` Legacy ما زال يعمل | MEASURED | 100% وقت الاختبار |
| Rork ليس OpenAI-compatible مباشرة | MEASURED | 100% |
| Chatwoot يحتاج Adapter | protocol comparison | 100% |

## ما هو مرجح وليس مؤكدًا بالكامل؟

| المعلومة | الثقة |
|---|---:|
| Backend text/object يستخدم AI SDK Core داخليًا | 90–95% |
| Rork يمر عبر Vercel AI Gateway | 60–75% |
| Body limit ثابت دائمًا عند ~4.493 MB | متوسط؛ قد يتغير مع Vercel/runtime |
| الموديل المعلن لكل function لن يتغير | منخفض على المدى الطويل |

## ما لم يتم إثباته؟

- كود Backend الداخلي الكامل.
- SLA رسمي للاستخدام الخارجي.
- rate limits طويلة المدى.
- privacy/data retention/DPA.
- region pinning.
- provider route الفعلي لكل request.
- embeddings endpoint.
- ضمان استمرار Legacy endpoints.

## منهجية Black-box

تم اختبار:

- HTTP methods وpreflight.
- auth/no-auth variants.
- valid وinvalid JSON.
- schema boundaries.
- roles وcontent parts.
- streaming frame sequence.
- Tool call وTool result round-trip.
- vision inputs.
- image generation/editing.
- STT inputs.
- concurrency.
- payload size threshold.
- latency samples.

## قاعدة كتابة الوثائق

أي claim داخل هذا المشروع يجب أن يكون واحدًا من:

1. موثقًا رسميًا.
2. ظاهرًا في SDK منشور.
3. قابلاً لإعادة القياس.
4. معلّمًا بوضوح كـInference.

لا تحوّل inference إلى fact، ولا تعتبر `200 OK` دليلًا أن كل request option تم احترامه.
