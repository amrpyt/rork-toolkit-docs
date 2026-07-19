# Contributing

Contributions should preserve the evidence standard of this repository.

## Evidence labels

Every behavioral claim should be traceable to one of:

- `OFFICIAL`: official documentation.
- `SDK`: published client package source.
- `MEASURED`: reproducible HTTP test.
- `INFERENCE`: a clearly labeled engineering conclusion.

## Pull request requirements

- Describe the endpoint and date tested.
- Include a minimal reproducible request.
- Redact credentials, cookies, customer data, and Base64 media.
- Distinguish accepted fields from fields proven to affect behavior.
- Update `docs/09-test-matrix.md` when adding a measured behavior.
- Update the OpenAPI specification when the request or response contract changes.
- Run `mkdocs build --strict` before opening the pull request.

## Safety

Do not submit destructive testing, credential bypass instructions, private customer information, high-volume abuse methods, or secrets.
