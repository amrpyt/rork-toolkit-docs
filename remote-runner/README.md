# Remote Runner Test Harness

This directory contains the exact Python test harness used for the remote Rork Toolkit measurements.

Dedicated runnable repository:

https://github.com/amrpyt/rork-toolkit-remote-tests

## Files

- `test_rork_remote.py` — standard-library-only Pytest suite.
- `pytest.ini` — disables output capture so JSON metrics appear in GitHub Actions logs.

## Execution environment

The harness runs in `amrpyt/rork-toolkit-remote-tests` using a GitHub Actions matrix with three separate GitHub-hosted Ubuntu jobs:

```text
Python 3.9
Python 3.10
Python 3.11
```

The test records each runner's public egress IP before calling Rork.

## Covered behavior

- Agent smoke response.
- Vercel AI SDK UI Message Stream v1 header and frame sequence.
- Tool request and same-endpoint tool-result round trip.
- Correct selection between multiple tools.
- `output-error` tool result.
- Large tool output.
- Parallel tool requests.
- Controlled concurrency waves with automatic stop on `429`, `5xx`, or success rate below 90%.

## Results

See [Remote Capacity and Tool Tests](../docs/11-remote-capacity-results.md).
