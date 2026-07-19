# الصور، الصوت، والـConnections

# `POST /images/generate/`

## الغرض

توليد صورة من Prompt.

```text
POST https://toolkit.rork.com/images/generate/
Content-Type: application/json
```

## Request مقاس

```json
{
  "prompt": "A clean product illustration on a white background",
  "size": "512x512"
}
```

## Response مقاسة

```json
{
  "image": {
    "base64Data": "...",
    "mimeType": "image/jpeg"
  },
  "aspectRatio": "1:1"
}
```

قد تظهر aliases إضافية في بعض النسخ، لذلك تعامل مع `image.base64Data` و`image.mimeType` كالشكل المقاس، ولا تفترض أن الشكل مطابق لـOpenAI Images API.

## سلوكيات مهمة

- `prompt` مطلوب.
- `size` غير موثوق كتحكم صارم؛ طلب `512x512` أعاد صورة فعلية 1024×1024 في اختبار.
- قيمة `size` غير معتادة قُبلت ورجعت أبعادًا أخرى.
- `model` غير صالح قُبل؛ يبدو ignored أو غير قابل للتحكم من العميل.
- الاستجابة JSON تحتوي Base64، لذلك حجمها قد يكون كبيرًا.

## Error عند غياب prompt

```http
400 Bad Request
```

```json
{"error":"Prompt is required"}
```

## زمن مقاس

تقريبًا 5–8 ثوانٍ في العينات التي تم تشغيلها، مع اختلاف حسب الطلب والتحميل.

---

# `POST /images/edit/`

## الغرض

تعديل صورة باستخدام Prompt وصورة أو أكثر.

```text
POST https://toolkit.rork.com/images/edit/
Content-Type: application/json
```

## Request مقاس

```json
{
  "prompt": "Change the background to a modern office",
  "images": [
    {
      "type": "image",
      "image": "BASE64_IMAGE"
    }
  ]
}
```

## Response

الاستجابة المقاسة تحتوي صورة Base64 داخل JSON، مع MIME type للصورة الناتجة.

## Error عند البيانات الناقصة

```http
400 Bad Request
```

```json
{
  "error": "Prompt and at least one image are required"
}
```

## زمن مقاس

حوالي 8.8 ثانية في العينة التي تم اختبارها.

---

# `POST /stt/transcribe/`

## الغرض

تحويل الصوت إلى نص.

```text
POST https://toolkit.rork.com/stt/transcribe/
Content-Type: multipart/form-data
```

## اسم الحقل الصحيح

```text
audio
```

مثال:

```bash
curl -sS https://toolkit.rork.com/stt/transcribe/ \
  -F 'audio=@sample.wav'
```

لا تضبط `Content-Type` يدويًا عند استخدام `FormData`؛ اترك client يضيف boundary.

## Response

```json
{
  "text": "transcribed text",
  "language": "en"
}
```

## Errors

عند استخدام field باسم `file` بدل `audio`، أو عدم إرسال الملف:

```http
400 Bad Request
```

```json
{"error":"Audio file is required"}
```

## نتائج العربية والمصري

في العينات القصيرة العامة التي تم اختبارها:

- تم transliterate كلمات عربية بدل تفريغها بالعربية.
- اللغة المكتشفة كانت خاطئة في بعض الحالات.
- تمرير `language=ar` أو `ar-EG` لم يحسن النتائج بشكل موثوق.
- ملف غير صوتي باسم `.wav` أعاد في اختبار واحد `200` ونصًا فارغًا بدل validation error.

## الحكم الإنتاجي

لا تستخدم STT الحالي كمصدر وحيد لمسار دعم عربي مهم. طبّق:

- validation للصوت قبل الإرسال.
- minimum confidence أو quality check عندك.
- fallback إلى مزود STT أقوى للعربية.
- سؤال المستخدم عند النصوص منخفضة الجودة بدل تنفيذ إجراء حساس.

---

# Connection APIs

الـSDK المنشور يكشف:

```text
GET /connections/list
GET /connection/init/{toolkit}
GET /connection/wait/{id}
GET /connection/disconnect/{toolkit}
```

## Flow المتوقع

```text
useConnections()
    |
    +--> GET /connections/list
    |
    +--> GET /connection/init/{toolkit}
              |
              v
          redirectUrl
              |
              v
       Expo WebBrowser auth session
              |
              v
 demotoolkit://connection/callback
```

## حالات Connection في TypeScript definitions

```text
INITIALIZING
INITIATED
ACTIVE
FAILED
EXPIRED
INACTIVE
```

هذه المسارات لم تُختبر بنفس عمق AI endpoints، لذلك لا تعتبرها Contract ثابتًا دون فحص إضافي، خصوصًا auth، cookies، والredirect validation.
