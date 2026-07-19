# الأمن والاستعداد للإنتاج

## لماذا لا نربط التطبيقات مباشرة بـRork؟

الاختبارات لم تُظهر API key أو authentication requirement على AI endpoints. كذلك CORS كان مفتوحًا. لو وضعت الاستدعاء مباشرة في browser أو mobile client، فأنت تفقد التحكم في:

- من يستهلك الخدمة.
- حجم الطلبات.
- الأدوات التي يمكن استدعاؤها.
- تسريب بيانات العملاء.
- مراقبة التكلفة.
- التوقف أو تغيّر الـcontract.

الحل: Gateway داخلي تحت سيطرتك.

## طبقات الحماية المطلوبة

```text
Client / Chatwoot
      |
      v
Your Gateway
  1. Authentication
  2. Authorization
  3. Tenant isolation
  4. Input validation
  5. Tool allowlist
  6. Rate limiting
  7. Size limits
  8. Timeout and cancellation
  9. Safe logging
 10. Fallback and circuit breaker
      |
      v
Rork Toolkit
```

## Authentication

- لا تجعل `toolkit.rork.com` endpoint ظاهرًا كاعتماد أساسي في frontend.
- استخدم service-to-service secret بين Chatwoot والـAdapter.
- دوّر secrets دوريًا.
- افصل secrets لكل environment.
- لا ترسل secrets داخل prompts أو tool outputs.

## Tenant isolation

كل request يجب أن يرتبط بـ:

```text
account_id
conversation_id
inbox_id
request_id
```

لا تستخدم conversation ID وحده إن كان يمكن أن يتكرر بين tenants.

## Tool security

### قواعد إلزامية

- Allowlist ثابتة للأدوات.
- Validation صارم للـinput.
- Authorization داخل كل Tool، لا عند الـAgent فقط.
- Idempotency للأدوات ذات side effects.
- Timeout مستقل.
- Maximum output size.
- Redaction قبل إعادة النتيجة إلى الموديل.

### تصنيف المخاطر

| المستوى | أمثلة | السياسة |
|---|---|---|
| Read-only منخفض | حالة أوردر، رصيد مخزون | يمكن التنفيذ تلقائيًا بعد auth |
| Read-only حساس | بيانات عميل، كشف حساب | يحتاج tenant/role checks قوية |
| Write قابل للعكس | إضافة note، إنشاء draft | audit + idempotency |
| Write مالي/حرج | refund، اعتماد، صرف مخزون | confirmation أو policy engine |
| مدمر | delete، إلغاء نهائي | human approval إلزامي |

## Prompt injection

اعتبر رسائل العملاء، الملفات، ومخرجات الأدوات بيانات غير موثوقة.

- لا تسمح للنص بتغيير allowlist.
- لا تجعل tool output تعليمات System.
- افصل policy عن prompt.
- لا تنفذ أوامر shell أو URLs اقترحها النموذج دون validation.
- لا تسمح للـAgent باختيار tenant أو user ID من النص.

## Logging

سجّل metadata بدل المحتوى الكامل افتراضيًا:

```json
{
  "requestId": "req-123",
  "conversationId": "conv-55",
  "endpoint": "/agent/chat",
  "status": 200,
  "latencyMs": 812,
  "toolNames": ["lookup_order"],
  "finishReason": "tool-calls",
  "errorClass": null
}
```

لا تسجل:

- Authorization headers.
- Cookies.
- Full customer messages بدون سياسة retention.
- Base64 images/audio.
- Tool outputs التي تحتوي PII أو secrets.

## Resilience

### Circuit breaker

افتح circuit عند تكرار:

```text
5xx
timeouts
malformed streams
schema failures
```

### Fallback

مسار مقترح:

```text
Rork unavailable
      |
      +--> fallback OpenAI-compatible provider
      |
      +--> non-AI deterministic response
      |
      +--> human handoff
```

### Contract tests

شغّل tests دورية للتحقق من:

- `/llm/text` response shape.
- `/llm/object` validation behavior.
- UI stream header.
- Tool event names.
- Tool result round-trip.
- body limit assumptions.
- CORS/auth changes.

## Privacy questions غير المحسومة

لم يتم إثبات من الخارج:

- Data retention.
- Training usage.
- Region guarantees.
- DPA/SLA.
- Provider routing لكل request.

قبل استخدام بيانات عملاء حقيقية، اطلب اتفاقًا مكتوبًا أو توثيقًا رسميًا يغطي ذلك.

## Production checklist

### Pilot

- [ ] Gateway داخلي.
- [ ] Authentication وtenant isolation.
- [ ] Read-only tools فقط.
- [ ] Zod/JSON Schema validation.
- [ ] Timeouts وcancellation.
- [ ] Redacted logs.
- [ ] Human handoff.
- [ ] Contract tests.

### Production كامل

- [ ] اتفاق Privacy/SLA مناسب.
- [ ] Rate limits معروفة أو budget guards.
- [ ] Fallback provider.
- [ ] Distributed state store.
- [ ] Idempotency لكل write tool.
- [ ] Approval policy للأفعال الحساسة.
- [ ] Alerts على latency/errors/schema drift.
- [ ] Runbook للحوادث.
- [ ] مراجعة أمنية مستقلة.
