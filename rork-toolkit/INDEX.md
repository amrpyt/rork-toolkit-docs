# Rork Toolkit API – Complete Developer Guide

This documentation set provides a production-ready reference to integrate Rork Toolkit AI endpoints in any application. Hand this folder to any AI developer/agent to implement safely and correctly.

## Contents
- 01-quick-start.md – Minimal setup and first call
- 02-authentication.md – Security model and environment setup
- 03-endpoints.md – Full endpoint specifications (Text LLM, Agent Chat, Images, STT)
- 04-implementation-examples.md – Web, React Native, Node examples
- 05-error-handling-and-retries.md – Robust patterns and utilities
- 06-best-practices.md – Performance, security, and scaling
- 07-openai-compatibility.md – Differences, adapters, and migration notes
- 08-advanced-features.md – Monitoring, caching, deduplication
- 09-ai-dev-agent-brief.md – Task brief for automated AI dev agents
- **rork-toolkit-postman-collection.json** – Complete Postman collection for all endpoints
- **postman-setup-guide.md** – Import guide and testing instructions

## Summary
- Primary production endpoint: `POST https://toolkit.rork.com/text/llm/` (text + vision)
- Additional endpoints: Agent chat, image generation/editing, speech-to-text
- Platform-managed authentication (no client API key)
- Not OpenAI-compatible out of the box; custom adapters recommended
