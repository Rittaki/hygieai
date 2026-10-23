# HygieAI

Secure file sharing where every upload is scanned for malware in an isolated
pipeline before anyone can download it, and an LLM explains the findings to
the file's owner in plain language.

> **Status:** Week 1 of 7, in development.

## How it works

1. The browser uploads directly to a quarantine bucket using a short-lived presigned URL.
2. An isolated worker with no internet access scans the file with ClamAV and YARA.
3. Only clean files are copied to the clean bucket. Anything else is never downloadable (fail closed).
4. Downloads use 60-second presigned links from the clean bucket only.

## Documentation

- [Design doc](docs/design.md)
- [Threat model (STRIDE)](docs/threat-model.md)
- [ADR-0001: Scanning vs end-to-end encryption](docs/adr/0001-scanning-vs-e2e-encryption.md)

## Tech stack

- **Frontend:** React, TypeScript, Vite, Tailwind, shadcn/ui
- **API:** Python, FastAPI, SQLAlchemy, Alembic
- **Data:** PostgreSQL, S3 (MinIO locally), SQS (LocalStack locally)
- **Scanning:** ClamAV, YARA
- **Infra:** Docker Compose, Terraform on AWS, GitHub Actions
- **Testing:** pytest, HTTPX, Testcontainers, Vitest, Playwright

## Repository layout

| Path | Contents |
|---|---|
| `apps/web` | React frontend |
| `apps/api` | FastAPI backend |
| `apps/scanner` | Scan worker |
| `infra/terraform` | AWS infrastructure |
| `docs` | Design doc, threat model, ADRs |

## Running locally

Requires Docker with Compose v2.

```bash
cp .env.example .env   # then set a strong POSTGRES_PASSWORD
docker compose up -d --build
curl http://127.0.0.1:8000/health   # {"status":"ok"}
```
