# مصفوفة الاختبارات

تاريخ نافذة الاختبارات الرئيسية: **19 يوليو 2026**.

## Network

| الاختبار | النتيجة |
|---|---|
| DNS إلى Vercel | نجاح |
| TLS 1.3 | نجاح |
| HTTP/1.1 | نجاح |
| HTTP/2 | نجاح |
| HSTS | موجود |
| `server: Vercel` | موجود |
| CORS preflight | `204` |
| `Access-Control-Allow-Origin` | `*` |

## Authentication

| الحالة | `/llm/text` أو Text Legacy |
|---|---|
| بدون auth | `200` |
| Bearer وهمي | `200` |
| Cookie وهمية | `200` |
| Origin Rork | `200` |
| Origin غير موثوق | `200` |

هذه النتائج تصف السلوك وقت الاختبار فقط.

## `/llm/text`

| الاختبار | النتيجة |
|---|---|
| minimal user message | `200` + `{completion}` |
| system + user | نجاح |
| image raw Base64 | نجاح |
| image Data URI | نجاح |
| malformed JSON | `400` |
| missing messages | `400` |
| `messages: []` | `500` |
| invalid model/options | قُبلت دون أثر واضح |
| `stream: true` | لم يتحول لبروتوكول streaming |

## `/llm/object`

| الاختبار | النتيجة |
|---|---|
| valid object schema | `200` + `{object}` |
| assistant + user history | نجاح |
| system role | `400` |
| missing schema | `200` مع Object generic |
| invalid schema value | `200` |
| impossible/weak schema | قد يرجع Object لا يحقق intent |
| missing messages | `400` |
| empty messages | `500` |

## `/agent/chat`

| الاختبار | النتيجة |
|---|---|
| UIMessage text | نجاح |
| invalid UI part | `400` text error |
| conversation history | نجاح |
| system role | نجاح في model-message path المختبر |
| streaming header v1 | موجود |
| text deltas | نجاح |
| tool with `jsonSchema` | نجاح |
| tool with `inputSchema` | `400` |
| tool call event | نجاح |
| tool result follow-up | نجاح |
| file image part | نجاح |
| old image UI shape | رفض |
| unknown top-level fields | تم تجاهلها في العينة |
| invalid model/provider options | تم تجاهلها في العينة |

## Legacy `/text/llm/`

| الاختبار | النتيجة |
|---|---|
| text | نجاح |
| system/user/assistant | نجاح |
| vision | نجاح |
| raw Base64 | نجاح |
| Data URI | نجاح |
| structured prompt | ممكن لكن غير مضمون |
| model invalid | قُبل |
| max tokens غير منطقي | قُبل |
| stop | لم يظهر تطبيق موثوق |
| OpenAI tools | ignored كأدوات |
| stream true | JSON عادي |
| empty messages | `500` |

## Images

| الاختبار | النتيجة |
|---|---|
| safe generation | نجاح |
| missing prompt | `400` |
| requested 512×512 | returned 1024×1024 في عينة |
| invalid size | قُبل وأعاد أبعادًا أخرى |
| invalid model | قُبل |
| image edit | نجاح |
| edit missing prompt/images | `400` |

## STT

| الاختبار | النتيجة |
|---|---|
| field `audio` | مقبول |
| field `file` | `400` |
| missing file | `400` |
| WAV | مقبول |
| Arabic samples | جودة ضعيفة/لغة خاطئة |
| `language=ar` | لم يظهر أثر موثوق |
| invalid bytes باسم WAV | `200` ونص فارغ في عينة |

## Limits

| الاختبار | النتيجة |
|---|---|
| 4,492,108-byte body | وصل إلى التطبيق |
| 4,494,108-byte body | `413 FUNCTION_PAYLOAD_TOO_LARGE` |
| 12 concurrent text requests | كلها `200` |
| rate-limit headers | لم تظهر |

## إعادة الاختبار

أعد الاختبارات عند:

- تحديث `@rork-ai/toolkit-sdk`.
- ظهور response shape جديد.
- فشل Chatwoot tool round-trip.
- تغيير DNS/headers.
- إضافة Rork authentication أو Cloud Credits enforcement.
