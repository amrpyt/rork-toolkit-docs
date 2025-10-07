# AI Dev Agent Brief

## Objective
Integrate Rork Toolkit AI endpoints into the application for:
- Image-aware text generation (primary)
- Optional: conversational agent, image generation/editing, STT

## Primary Endpoint
- `POST https://toolkit.rork.com/text/llm/`
- Send messages with text and optional base64 images (without data URI prefix)
- Expect `{ completion: string }` response; may contain JSON

## Acceptance Criteria
- [ ] Successful call with text+image
- [ ] Robust error handling (400/401/403/413/429/500)
- [ ] Retries with exponential backoff
- [ ] Timeout + cancellation
- [ ] No logging of raw image/audio data
- [ ] Utilities for cleaning base64 and parsing completion

## Optional Endpoints
- Agent Chat: `${EXPO_PUBLIC_TOOLKIT_URL}/agent/chat`
- Image Generation: `POST /images/generate/`
- Image Editing: `POST /images/edit/`
- STT: `POST /stt/transcribe/`

## Risks & Constraints
- Not OpenAI-compatible out-of-the-box
- STT requires multipart/form-data without manual Content-Type
- Image payload size limits apply

## Deliverables
- Reusable client module (fetch wrappers, retries, parsing)
- Example usages for Web and React Native
- Monitoring hooks (latency, status codes)
