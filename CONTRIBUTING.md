# Contributing

Thanks for improving Local RAG Desk.

1. Fork the repository and create a focused branch.
2. Keep runtime dependencies at zero unless a feature clearly justifies one.
3. Preserve offline-first behavior and never add telemetry or hidden network calls.
4. Add or update tests for behavior changes.
5. Run `python -m compileall -q src tests` and `python -m unittest discover -s tests -v`.
6. Keep English and Arabic README documentation aligned when user-facing behavior changes.
7. Open a pull request describing the problem, implementation, and validation performed.

Use clear commit messages and avoid committing generated indexes, private documents, credentials, or environment files.
