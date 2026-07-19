# الأخطاء، الحدود، والأداء المقاس

## Network وTransport

### DNS وTLS

الاختبارات أثبتت:

- النطاق يُحل إلى Vercel infrastructure.
- TLS 1.3 مدعوم.
- HTTP/1.1 وHTTP/2 مدعومان.
- `server: Vercel` ظاهر في الردود.
- HSTS مفعّل.

## CORS

`OPTIONS` على المسارات المختبرة أعاد:

```http
204 No Content
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: content-type,authorization
Access-Control-Allow-Methods: GET,HEAD,PUT,POST,DELETE,PATCH
```

وجود CORS مفتوح لا يعني أن الخدمة مصممة كـPublic production API. لا تستخدمه كبديل للمصادقة.

## Authentication الظاهر

الاختبارات التالية أعادت نجاحًا في Text endpoints:

- بدون Authorization.
- Bearer token وهمي.
- Cookie وهمية.
- Origin مختلف.

لم يظهر API key requirement أو session requirement على المسارات العامة المختبرة.

## Cache وRate-limit headers

- `X-Vercel-Cache: MISS` ظهر في العينات المتكررة.
- لم تظهر `RateLimit-*` headers.
- لم يظهر `Retry-After` في الاختبارات العادية.
- عدم ظهور rate limit لا يثبت عدم وجوده.

## حد حجم الـRequest

تم تضييق حد Vercel body الخارجي تقريبًا إلى:

```text
4.493 MB decimal تقريبًا
```

عينات القياس:

```text
4,492,108 bytes -> وصلت إلى التطبيق
4,494,108 bytes -> 413 قبل التطبيق
```

الرد فوق الحد:

```http
413 Payload Too Large
X-Vercel-Error: FUNCTION_PAYLOAD_TOO_LARGE
```

### أثر ذلك على الصور

Base64 يزيد الحجم عن الملف الأصلي بنحو الثلث تقريبًا، بالإضافة إلى JSON overhead. استخدم ضغطًا قويًا، واعتبر 2.5–3 MB للصورة الأصلية حدًا تشغيليًا محافظًا، لا ضمانًا رسميًا.

## Context size

`/text/llm/` Legacy قبل نصوصًا متكررة حتى 256K characters في الاختبارات، مع استرجاع markers من البداية والنهاية.

هذا لا يثبت:

- token context النهائي.
- جودة reasoning على سياق كبير.
- حد `/llm/text` الحالي.
- عدم وجود truncation في حالات أخرى.

## Latency المقاسة

| العملية | النطاق/النتيجة التقريبية |
|---|---|
| Text core requests | median قرابة 640ms |
| Text parameter tests | median قرابة 715ms |
| Agent TTFB | قرابة 187–204ms |
| Agent simple completion | قرابة 624–806ms |
| Vision text | قرابة 1.6–2.5s |
| Image generation | قرابة 5–8s |
| Image editing | قرابة 8.8s |
| STT | قرابة 1.2–3.5s |

هذه قياسات من نافذة محدودة وليست SLA.

## Concurrency

- 8 طلبات متتالية متقاربة: كلها `200`.
- 12 طلبًا متوازيًا: كلها `200`.
- wall time في عينة التوازي قرابة 1.58s.
- لم تظهر rate-limit headers.

لا تستنتج من ذلك أن concurrency غير محدود.

## Known bugs وQuirks

### 1. Empty messages -> 500

يظهر في:

```text
/llm/text
/llm/object
/text/llm/
```

امنع `messages: []` محليًا.

### 2. خيارات مقبولة لكن ignored

في Text endpoints تم قبول `model` و`max_tokens` و`stream` وقيم غير منطقية دون أثر بروتوكولي واضح.

### 3. `/llm/object` لا يضمن Schema وحده

Schema ناقصة أو غير صالحة قد تستمر وتعيد Object generic. Local validation إلزامي.

### 4. Image size غير صارم

قيمة `size` لا تضمن الأبعاد الفعلية.

### 5. STT validation ضعيف

ملف غير صوتي قد يرجع `200` مع نص فارغ.

### 6. Agent قد يقترح Tool غير متاح

في اختبار Vision حاول الـAgent استدعاء Tool داخلي غير مقدم من العميل، ثم أرسل tool errors. يجب رفض أي tool name غير موجود في allowlist.

### 7. لا يوجد versioning ظاهر للمسارات

لا توجد صيغة مثل `/v1`. ضع contract tests حتى تكتشف breaking changes مبكرًا.

## Error policy المقترحة

### Retryable

```text
408
429
500
502
503
504
network reset
timeout قبل اكتمال الاستجابة
```

### Non-retryable غالبًا

```text
400 validation error
401/403 إن ظهرت
413 payload too large
invalid local schema
unknown tool
```

### Backoff

```text
attempt 1: 500ms + jitter
attempt 2: 1s + jitter
attempt 3: 2s + jitter
```

لا تعِد Tool له side effect دون idempotency protection.
