# Matekk Coffee Shop — Local Vulnerable Web Lab

Matekk is a deliberately vulnerable React/Vite + FastAPI/Starlette + SQLite training target. It is designed for the full penetration-testing lifecycle: reconnaissance, web enumeration, vulnerability analysis, controlled exploitation, post-exploitation analysis, and reporting.

> **Safety:** This is an intentionally insecure training application. Keep it isolated and bound to loopback (127.0.0.1). Never expose it to a LAN, VPN, or the public internet. Use only the synthetic data supplied with the lab.

## Run locally

Requirements: Node.js 20+ and Python 3.11+.

### Windows PowerShell

1. npm.cmd install
2. python -m pip install -r requirements.txt
3. npm.cmd run build
4. python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
5. Open http://127.0.0.1:8000/.

### Kali Linux

1. git clone <PRIVATE_REPOSITORY_URL>
2. cd Matekk-Coffee-Shop
3. python3 -m venv .venv
4. source .venv/bin/activate
5. python -m pip install -r requirements.txt
6. npm install
7. npm run build
8. python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
9. Open http://127.0.0.1:8000/.

Keep the server bound to 127.0.0.1. When testing from Kali itself, run the application and the browser/tools on that Kali machine. Do not change the bind address to 0.0.0.0.

## Demo accounts

- Administrator: Sally / admin1234
- Customer: Jhon / iloveyou

## Implemented reconnaissance surface

- HTTP fingerprint headers: X-Powered-By, X-Matekk-Stack.
- Version inventory: /lab/fingerprint.
- robots.txt and sitemap.xml with training clues.
- Interactive Swagger documentation at /docs and OpenAPI JSON at /openapi.json.
- Directory indexes at /documents/, /backup/, and /internal/.
- Legacy route /staff/archive.
- Exposed synthetic documents and backup/config examples.

## Synthetic document portfolio

The in-app Business Portfolio lists fabricated customer payment records, fictional customer accounts, an owner financial summary, secret recipe notes, employee records, supplier agreement, internal memo, and API schema. Files are also discoverable through the public directory paths above.

All names, contact details, bank values, payment references, and credentials in these files are synthetic. Account numbers are invalid placeholders; payment details are masked; secrets are nonfunctional lab strings. No real payment credentials or real bank information are included.

## Intentional weaknesses and exercise notes

- Technology/version disclosure through HTTP headers and /lab/fingerprint.
- Public API documentation and exposed route inventory.
- Information disclosure through source comments, robots/sitemap clues, and internal notes.
- Directory listing and backup/configuration exposure.
- Authenticated customer-record IDOR exercise: an authenticated user can request another synthetic customer ID because ownership is not checked.
- Weak demo credentials, plaintext password storage, process-local sessions, and no rate limiting.
- Upload validation trusts client-provided MIME metadata; accepted files are stored as inert .bin files in data/uploads and are never executed or publicly served.
- python-multipart==0.0.20 and starlette==0.41.3 are retained for CVE research exercises. Their presence is version-based exposure evidence, not proof that a denial-of-service exploit has been reproduced.
- CVE-2026-42561 and CVE-2025-62727 DoS validation is intentionally deferred to a later bounded testing phase.

PHP2Shell is not included: this target uses FastAPI, and a PHP runtime was not found on the host during implementation. It would be misleading to claim PHP2Shell affects this application.

## Suggested testing progression

1. Reconnaissance: HTTP headers, service fingerprinting, robots, sitemap.
2. Enumeration: API docs, directories, backups, exposed documents.
3. Vulnerability analysis: access control, authentication, upload handling, dependency versions.
4. Controlled exploitation: IDOR, information disclosure, and upload validation.
5. Advanced validation: bounded CVE testing in a later phase.
6. Post-exploitation: inspect synthetic records and document impact without using real data.
7. Reporting: evidence, severity, reproduction, impact, and remediation.

## Git and lab data

The repository intentionally excludes data/, uploaded files, logs, node_modules/, and generated dist/ output. The SQLite database is created and seeded automatically when the backend starts. Build dist/ locally with npm run build.

Keep the GitHub repository private. Although the lab's exposed documents contain synthetic training data, the application deliberately includes exploitable weaknesses and weak demo credentials.

## Safety and reset

This application is intentionally insecure and must never be deployed. Use only the synthetic data supplied with the lab. Do not upload actual malware, credentials, financial records, or personal information. Uploaded bytes remain inert and quarantined.

To reset the database and upload queue: stop the app, delete data/matekk.db and the contents of data/uploads, then restart. The database seeds the demo accounts, sample reviews, and synthetic customer records at startup. Public portfolio files live under public/ and are copied into dist/ during the Vite build.
