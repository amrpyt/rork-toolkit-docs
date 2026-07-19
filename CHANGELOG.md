# Changelog

## 2026-07-20 — Evidence-based rewrite

- Replaced the old endpoint-first documentation with a current/legacy split.
- Documented the published `@rork-ai/toolkit-sdk` package.
- Added `/llm/text` and `/llm/object` as current SDK endpoints.
- Marked `/text/llm/` as Legacy.
- Added complete `/agent/chat` UI Message Stream v1 documentation.
- Added Tool Calling and Tool Result round-trip examples.
- Added Chatwoot Captain adapter architecture and mapping contracts.
- Added measured errors, body-size threshold, latency, concurrency, and known bugs.
- Added image generation, image editing, STT, Connection API, and analytics notes.
- Added OpenAPI 3.1 specification.
- Added GitHub Pages documentation workflow.
- Added source confidence labels and production security checklist.

## Previous repository content

Earlier files were based on limited endpoint discovery and contained assumptions that later testing disproved, including treating `/text/llm/` as the primary current endpoint and requiring raw Base64 without a Data URI prefix. Those files are deprecated in favor of `docs/`.
