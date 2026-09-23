# Security Policy

## Supported version
The latest `main` branch and latest tagged release are supported.

## Privacy model
Local RAG Desk performs no network requests and has no telemetry. It reads only `.txt` and `.md` files under the root selected by the user and skips symbolic links. Index files contain source text chunks verbatim; protect or delete them with the same care as the source documents.

## Safe usage
Do not index secrets into a location that is synchronized or shared unintentionally. Document text is treated as data and is never executed. Review permissions on the output directory when processing sensitive material.

## Reporting
Please report security concerns privately through GitHub's security reporting facilities when available. Do not publish credentials, personal documents, or exploit details in a public issue.
