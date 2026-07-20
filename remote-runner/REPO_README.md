# Rork Toolkit Remote Tests

GitHub-hosted remote test harness for:

```text
POST https://toolkit.rork.com/agent/chat
```

The existing workflow runs the same test suite on three separate Ubuntu runners:

- Python 3.9
- Python 3.10
- Python 3.11

Each job records its public egress IP before testing Rork.

## Covered tests

- Unauthenticated agent request.
- Vercel AI SDK UI Message Stream v1.
- Tool request and same-endpoint tool-result round trip.
- Selection between multiple tools.
- Tool execution error result.
- Large tool result.
- Parallel tool calls.
- Controlled concurrency waves up to 96 simultaneous requests.
- Automatic stop on `429`, `5xx`, or success rate below 90%.

## Latest measured results

- 846 total measured agent requests across three completed successful runs.
- Nine distinct GitHub runner egress IPs.
- 0 responses with HTTP `429`.
- 0 responses with HTTP `5xx`.
- 96/96 successful requests at concurrency 96.
- 120/120 successful requests at concurrency 16.
- Parallel tool calls confirmed.
- 64,429-character tool output confirmed.

Full report:

https://amrpyt.github.io/rork-toolkit-docs/11-remote-capacity-results.html

Latest successful run:

https://github.com/amrpyt/rork-toolkit-remote-tests/actions/runs/29712865645

Canonical documentation:

https://github.com/amrpyt/rork-toolkit-docs
