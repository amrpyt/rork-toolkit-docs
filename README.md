# Rork Toolkit API — Unofficial Engineering Reference

[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://amrpyt.github.io/rork-toolkit-docs/)
[![Evidence](https://img.shields.io/badge/evidence-official%20%2B%20SDK%20%2B%20measured-brightgreen)](./docs/10-sources-and-confidence.md)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.1-orange)](./openapi/rork-toolkit-unofficial.yaml)
[![Remote tests](https://img.shields.io/badge/remote%20tests-846%20requests%20%7C%2096%20concurrent-success)](./docs/11-remote-capacity-results.md)

مرجع هندسي غير رسمي لـ **Rork Toolkit API**، مبني على:

- توثيق Rork الرسمي المنشور.
- فحص الحزمة العامة `@rork-ai/toolkit-sdk`.
- اختبارات Black-box فعلية على `https://toolkit.rork.com`.
- مقارنة البروتوكول مع Vercel AI SDK.
- تحليل عملي لربطه مع Chatwoot Captain.

> هذا المشروع ليس تابعًا لـRork ولا يمثل دعمًا رسميًا منها. السلوك غير الموثق قد يتغير دون إشعار.

## الزتونة

المسارات الحالية التي يستخدمها الـSDK الرسمي:

```text
POST /llm/text
POST /llm/object
POST /agent/chat
```

المسار التالي ما زال يعمل، لكنه Legacy:

```text
POST /text/llm/
```

### أهم نتيجة للتولز

Tool Calling الحقيقي موجود في:

```text
POST https://toolkit.rork.com/agent/chat
```

والأدوات تُرسل هكذا:

```json
{
  "tools": {
    "lookup_order": {
      "description": "Look up an order by ID",
      "jsonSchema": {
        "type": "object",
        "properties": {
          "orderId": { "type": "string" }
        },
        "required": ["orderId"],
        "additionalProperties": false
      }
    }
  }
}
```

الـAgent يستخدم **Vercel AI SDK UI Message Stream v1**. لذلك Rork ليس OpenAI-compatible endpoint، ولا يمكن وضعه مباشرة كـOpenAI Base URL داخل Chatwoot Captain. يلزم Adapter يترجم الرسائل والـstream والـtool calls.

## ابدأ من هنا

- [نظرة عامة ومعمارية الخدمة](./docs/01-overview.md)
- [الـSDK الرسمي والبروتوكولات](./docs/02-sdk-and-architecture.md)
- [`/llm/text` و`/llm/object`](./docs/03-text-and-object.md)
- [`/agent/chat`، Streaming، Tool Calling](./docs/04-agent-tools-streaming.md)
- [الصور، الصوت، والـConnections](./docs/05-images-audio-connections.md)
- [الأخطاء، الحدود، والأداء المقاس](./docs/06-errors-limits-performance.md)
- [دليل ربط Chatwoot Captain](./docs/07-chatwoot-captain-adapter.md)
- [الأمن والاستعداد للإنتاج](./docs/08-security-production.md)
- [مصفوفة الاختبارات](./docs/09-test-matrix.md)
- [المصادر ودرجات الثقة](./docs/10-sources-and-confidence.md)
- [نتائج الاختبارات من IPs منفصلة](./docs/11-remote-capacity-results.md)

## Quick start

### Text

```bash
curl -sS https://toolkit.rork.com/llm/text \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [
      {"role":"user","content":"Reply exactly: OK"}
    ]
  }'
```

Response:

```json
{"completion":"OK"}
```

### Structured object

```bash
curl -sS https://toolkit.rork.com/llm/object \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [
      {"role":"user","content":"Return Alice, age 30"}
    ],
    "schema": {
      "type":"object",
      "properties": {
        "name":{"type":"string"},
        "age":{"type":"number"}
      },
      "required":["name","age"],
      "additionalProperties":false
    }
  }'
```

> طبّق validation محليًا دائمًا. الاختبارات أثبتت أن السيرفر قد يرجع Object لا يطابق Schema غير الصالحة أو الناقصة.

## حالة التوافق مع Chatwoot

| السيناريو | الحكم |
|---|---|
| Text replies فقط | ممكن عبر Adapter بسيط |
| Tool Calling كامل | ممكن عبر `/agent/chat` وAdapter stateful |
| وضع Rork مباشرة كـOpenAI endpoint | غير ممكن |
| Embeddings/Knowledge Base | لا يوجد endpoint مكتشف؛ استخدم مزودًا منفصلًا |
| الاعتماد عليه وحده في Production | غير موصى به دون Gateway وفallback |

المعمارية الموصى بها:

```text
Chatwoot Captain
      |
      v
Internal Rork Adapter
  - auth
  - schema validation
  - stream parser
  - tool executor
  - state store
  - retries/fallback
      |
      v
Rork /agent/chat
```

## Repository status

- **Canonical docs:** `docs/`
- **OpenAPI:** `openapi/rork-toolkit-unofficial.yaml`
- **Examples:** `examples/`
- **Last measured:** 20 July 2026
- **Remote harness:** `remote-runner/`
- **Documentation revision:** 20 July 2026

## License and disclaimer

Documentation and examples are provided under the MIT License. Product names and trademarks belong to their respective owners. See [DISCLAIMER.md](./DISCLAIMER.md).
