# Authentication & Security

## Overview
- Platform-managed authentication (no client API key required)
- Session-based and origin-aware access
- Project-scoped permissions
- All endpoints over HTTPS

## Environment Variables
```env
EXPO_PUBLIC_TOOLKIT_URL=https://toolkit.rork.com
```

## Request Headers
- JSON requests: set `Content-Type: application/json`
- Multipart requests (STT): do NOT set `Content-Type` manually; the browser/runtime will set it with boundary

## CORS & Deployment
- When calling directly from web, ensure your domain is allowed by the platform
- For stricter control, proxy requests via your backend (recommended for logging/metrics)

## Security Best Practices
- Do not log sensitive user data (images, audio, PII)
- Strip `data:*;base64,` prefix from images before sending
- Use HTTPS everywhere; avoid mixed content
- Keep environment variables out of client bundle unless intended (e.g., EXPO_PUBLIC_TOOLKIT_URL)
- Handle 401/403 gracefully (session expiry, quota enforcement)

## Example: Safe Fetch Wrapper
```ts
export async function safeJson<T>(res: Response): Promise<T> {
  const text = await res.text();
  try { return JSON.parse(text) as T; } catch {
    throw new Error(`Invalid JSON response: ${text?.slice(0, 300)}`);
  }
}
```

## Threat Model Notes
- Authentication appears linked to user/project session on the Rork platform
- No API key in code: prefer server-side observability for auditing and rate insights
