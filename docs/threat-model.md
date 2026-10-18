# HygieAI: Threat Model (STRIDE)

**Status:** Draft (Week 1) · **Last updated:** 2026-10-17

## What we are protecting

- **Recipients' devices:** they must never receive a file that wasn't scanned and found clean.
- **Users' files:** only the owner, and people the owner shares with, can read them.
- **Accounts:** passwords, sessions and tokens.
- **The audit log:** an honest record of who did what.

## Trust boundaries

1. Browser ↔ API (the internet; everything from the browser is untrusted).
2. Browser ↔ quarantine bucket (direct upload with a presigned URL).
3. API ↔ queue ↔ scan worker.
4. Scan worker ↔ the untrusted file it is scanning.
5. API ↔ LLM provider (a third party).

## Threats and mitigations

STRIDE: **S**poofing, **T**ampering, **R**epudiation, **I**nformation disclosure, **D**enial of service, **E**levation of privilege.

| # | Category | Threat | Mitigation | When |
|---|---|---|---|---|
| 1 | Spoofing | Attacker guesses or stuffs passwords to take over an account. | Argon2id hashing; rate limiting on login; the same error message for "no such user" and "wrong password". | Week 1 |
| 2 | Spoofing | Stolen refresh token is used to keep a session alive. | Refresh tokens are rotated on every use. Reusing an old token revokes the whole token family (reuse detection). Only a hash of each token is stored. | Week 1 |
| 3 | Spoofing | A malicious site makes the browser send requests with the user's cookies (CSRF). | Refresh cookie is `httpOnly`, `Secure`, `SameSite=Strict` and scoped to the refresh path. Access tokens are sent in the `Authorization` header, which other sites can't set. | Week 1 |
| 4 | Tampering | Uploader replaces the file after it was scanned. | Downloads come only from the clean bucket. Only the worker can write to it. The quarantine object is never served. | Week 3 |
| 5 | Tampering | Client lies about size or type, or uploads a huge file. | Presigned POST with a content-length range enforced by S3; the API re-checks the object's size before queuing the scan. File type is decided by the scanner, not by the client. | Week 2 |
| 6 | Tampering | API is tricked into marking a file `clean`. | Only the worker sets scan verdicts. No API endpoint changes a file's status to `clean`. | Week 3 |
| 7 | Repudiation | User denies sharing or downloading a file. | Audit events for login, upload, verdict, share and download, with user id and timestamp. | Week 4 |
| 8 | Information disclosure | User reads another user's file by changing the file id in the URL (IDOR). | Every file query is filtered by owner id. Unknown and not-yours both return 404, so ids can't be probed. | Week 2 |
| 9 | Information disclosure | A download link leaks (logs, browser history, forwarded message). | Presigned download URLs expire after 60 seconds. Share links can expire and be revoked. | Week 2/4 |
| 10 | Information disclosure | File contents are sent to the LLM provider. | The LLM receives only scan metadata (signature and rule names, file type), never file bytes. | Week 6 |
| 11 | Information disclosure | Secrets are committed to Git. | Config from environment variables; `.env` is git-ignored; gitleaks pre-commit hook. | Week 1 |
| 12 | Denial of service | Login flooding, or flooding the scan queue with uploads. | Rate limits on login and upload; size limit per file. | Week 1/2 |
| 13 | Denial of service | A file crashes or hangs the scanner (e.g. a zip bomb). | Scan timeouts and ClamAV archive limits; failed jobs retry, then go to the dead-letter queue and the file becomes `scan_error` (never downloadable). | Week 3 |
| 14 | Elevation of privilege | A malicious file exploits the scanner itself. | Worker runs as a non-root container with no internet access and only the permissions it needs. | Week 3/5 |
| 15 | Elevation of privilege | Instructions hidden in a file trick the LLM (prompt injection). | The LLM never sees file contents (see #10); its output is treated as text to display, never as instructions to act on. | Week 6 |

## Accepted risks

- **Scanning misses new malware.** Signatures and rules only catch what they know. The UI says "no threats found", never "safe".
- **Private (end-to-end encrypted) mode can't be scanned.** See [ADR-0001](adr/0001-scanning-vs-e2e-encryption.md).
- **No 2FA in v1.** A stolen password is enough to log in. Planned later.
- **The audit log is not tamper-evident.** Someone with database access could edit it. Hash-chaining is planned later.
