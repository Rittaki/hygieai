# ADR-0001: Scan files server-side in standard mode; a future private mode is end-to-end encrypted and unscanned

**Status:** Accepted · **Date:** 2026-10-17

## Context

HygieAI's core promise is that files are scanned for malware before anyone can download them. We also want, later, a private mode where not even HygieAI can read users' files.

"Encrypted" can mean three different things, and only one of them conflicts with scanning:

| Kind | Who can decrypt | Compatible with server-side scanning? |
|---|---|---|
| In transit (TLS) | Client and server | Yes |
| At rest (S3 server-side encryption) | The server, via its keys | Yes |
| End-to-end (E2EE) | Only the users' devices | **No.** The server only ever holds ciphertext. |

To scan a file, the scanner has to read its plaintext. E2EE exists so that the server cannot read the plaintext. The two goals are directly opposed.

## Decision

1. **Standard mode (default, built now):** files are encrypted in transit and at rest, but the server can read them. Every file is scanned, and only `clean` files can be downloaded.
2. **Private mode (built later, opt-in per file):** the browser encrypts the file with a key the server never receives. The server cannot scan it.
   - Private files get a distinct status, `unscanned_encrypted`. They are **never** marked or shown as `clean`.
   - They can be downloaded only through the private-mode flow, and the recipient sees an explicit warning that the file was not scanned.
   - The fail-closed rule for standard mode is unchanged: standard downloads still require `clean`.

## Alternatives considered

- **Scan in the browser before encrypting.** Rejected. The client controls that code; an attacker can skip the scan or fake its result. A security control that the attacker runs is not a control.
- **Client sends a file hash; the server checks it against known-malware hashes.** Rejected. The server can't verify that the hash matches the encrypted content, so the client can lie. It would also only catch exact copies of already-known files.
- **The server keeps a copy of the keys (escrow) so it can decrypt and scan.** Rejected. That is just at-rest encryption, and calling it end-to-end would mislead users.
- **No private mode at all.** Simpler, but privacy is a legitimate need. Deferred, not rejected.

## Consequences

**Positive**
- Standard mode can make, and keep, a real security guarantee.
- The trade-off is explicit and visible to users instead of hidden.

**Negative**
- In standard mode HygieAI can read users' files, so access to plaintext must be tightly limited: only the worker reads the quarantine bucket, the LLM receives findings and never file contents, and bucket access is least-privilege.
- Private mode files carry malware risk that HygieAI cannot reduce. The UI and docs must say so plainly.
- The status model gains an extra state, and every download path must handle it explicitly.
