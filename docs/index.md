# Rork Toolkit API

مرجع هندسي غير رسمي ومبني على الأدلة لفهم **Rork Toolkit** وربطه بأنظمة خارجية، خصوصًا Chatwoot Captain.

## ما الذي تم إثباته؟

- الـSDK الرسمي الحالي يستخدم `/llm/text` و`/llm/object` و`/agent/chat`.
- `/agent/chat` مبني مباشرة على Vercel AI SDK client primitives ويستخدم UI Message Stream v1.
- Tool Calling يعمل فعليًا، بما يشمل Tool Input وTool Result round-trip.
- تم تنفيذ 846 طلبًا من تسعة عناوين IP مختلفة، حتى 96 طلبًا متزامنًا، دون `429` أو `5xx`.
- `/text/llm/` مسار Legacy ما زال يعمل لكنه ليس المسار الحالي في الـSDK المنشور.
- Rork ليس OpenAI-compatible API.
- لا يوجد Embeddings endpoint مكتشف حتى تاريخ الاختبار.
- الـEndpoints المختبرة لم تطلب API key ظاهرًا، لذلك يجب عدم كشفها مباشرة داخل Production بدون Gateway داخلي.

## أقصر طريق حسب هدفك

| هدفك | اقرأ |
|---|---|
| استخدام Text Generation | [Text وObject](03-text-and-object.md) |
| بناء Agent بأدوات | [Agent والتولز](04-agent-tools-streaming.md) |
| ربطه مع Chatwoot | [Chatwoot Adapter](07-chatwoot-captain-adapter.md) |
| معرفة المخاطر | [الأمن والإنتاج](08-security-production.md) |
| مراجعة ما تم اختباره فعلًا | [مصفوفة الاختبارات](09-test-matrix.md) |
| مراجعة اختبارات IPs منفصلة والقدرة | [نتائج Remote](11-remote-capacity-results.md) |

## Base URL

```text
https://toolkit.rork.com
```

## المسارات الأساسية

```text
POST /llm/text
POST /llm/object
POST /agent/chat
POST /images/generate/
POST /images/edit/
POST /stt/transcribe/
```

## Legacy

```text
POST /text/llm/
```

## تحذير

هذه الوثائق ليست Contract رسميًا من Rork. أي سلوك تم اكتشافه بالاختبار فقط قد يتغير. لذلك كل Integration إنتاجي يجب أن يحتوي على validation، timeouts، retries، monitoring، وfallback provider.
