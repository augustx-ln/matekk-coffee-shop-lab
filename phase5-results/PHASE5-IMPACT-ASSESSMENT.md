# Phase 5 — Controlled Exploitation and Impact Assessment

**Status:** Completed for the defined non-destructive scope  
**Date:** 2026-11-01  
**Target:** Matekk Coffee Shop local synthetic lab (`127.0.0.1:8000`)  
**Method:** Read-only HTTP requests, source review, and read-only SQLite/file inspection. No destructive payloads, persistence, privilege escalation, external callbacks, or data modification were performed.

## Executive result

Phase 5 confirmed that the previously identified weaknesses have meaningful confidentiality impact inside the lab. Anonymous visitors can retrieve multiple categories of synthetic customer, employee, payment, financial, supplier, configuration, and database-backup material. Authenticated customer IDOR exposure was already behaviorally demonstrated in Phase 4. The upload MIME weakness accepted an inert plain-text file, but the stored upload was not found to be directly retrievable through the tested public paths and was not executed.

## 1. Anonymous exposure impact — confirmed

The following directory indexes and direct file requests returned HTTP 200 without authentication:

- `/documents/` — 8 listed files, including customer account export, customer payment records, employee records, internal memos, owner financial records, recipes, supplier contracts, and API schema.
- `/backup/` — 3 listed files, including configuration backup, SQL database backup, and legacy backup.
- `/internal/` — 2 listed files, admin notes and developer comments.
- `/staff/archive` — legacy backup content returned HTTP 200.
- `/static-lab/` direct file paths also returned HTTP 200 for customer account/payment exports and configuration/database backups.

Thirteen direct document/backup/internal/legacy file requests returned HTTP 200. Content was classified using metadata and pattern indicators; sensitive values were not copied into this report. Indicators found included email addresses and phone numbers in customer/employee/supplier exports, financial markers in payment and owner financial records, credential markers in the configuration backup and admin notes, and SQL statements plus personal-data markers in the database backup.

**Impact:** An unauthenticated visitor can obtain synthetic records and internal operational material without logging in. In a production analogue, this could expose personal data, payment-related information, internal business information, and configuration secrets. Actual credential validity or external reuse was not tested.

## 2. IDOR impact — Phase 4 evidence carried forward

A customer account previously retrieved private records for customer IDs 1001, 1002 and 1003, all with HTTP 200. The three records included names, email addresses, phone numbers, and internal notes. The source confirms the route requires authentication but does not enforce record ownership.

**Impact:** Any authenticated customer may enumerate valid customer IDs and retrieve other customers' private records, subject to the current lab dataset and route behavior.

## 3. Upload MIME spoofing impact — bounded

The Phase 4 plain-text test file was stored as an opaque `.bin` in `data/uploads/`. It was 30 bytes and did not begin with an MZ or ELF executable signature and contained no `<script` marker. The tested `/data/uploads/...` and `/uploads/...` URLs returned the SPA HTML fallback (same hash as `/`), not the uploaded bytes. No public route for serving quarantine contents was identified in the reviewed source.

**Impact:** The application accepts content whose bytes do not match the declared MIME type and records it for quarantine. This can poison the review/upload workflow and may create downstream risk if later processing trusts metadata. This test does **not** demonstrate code execution, public file retrieval, malware execution, or server compromise.

## 4. Authorization controls and service health

After the Phase 4 server restart, anonymous requests returned:

- `/api/me`: HTTP 401
- `/api/admin/summary`: HTTP 401
- `/api/admin/users`: HTTP 401
- `/api/admin/reviews`: HTTP 401
- `/api/admin/quarantine`: HTTP 401

Phase 4's authenticated checks remain the evidence for role separation: customer-to-admin requests returned 403 while admin requests returned 200. Phase 5 did not re-run credentialed role tests.

Health endpoint remained HTTP 200. The application stayed bound to loopback at `127.0.0.1:8000`.

## 5. Data integrity and test boundaries

- SQLite integrity check before and after Phase 5: `ok` (Phase 5 used read-only database access).
- Row counts at start of Phase 5: users=2, customer_private_records=3, reviews=3.
- No database writes were made during Phase 5.
- Existing Phase 4 review 3 was preserved.
- No source code or runtime configuration was changed.
- The upload test artifact was inspected but not deleted, to preserve Phase 4 evidence.

## Evidence files

- `phase5-anonymous-impact.json` — anonymous route status and directory index entries.
- `phase5-public-file-impact.json` — file status, sizes, hashes, and non-content indicators.
- `phase5-direct-path-checks.json` — direct static and upload-path checks.

## Phase 5 conclusion

**Confirmed impact:** anonymous disclosure of synthetic sensitive business/customer material; authenticated cross-customer private-record access; and acceptance of MIME-spoofed uploads into quarantine.

**Not demonstrated:** production credential compromise, access to real customer data, arbitrary file execution, server-side code execution, persistence, privilege escalation, or database tampering.

## Phase 6 entry recommendation

Proceed with a bounded post-exploitation impact review focused on mapping data exposure and trust boundaries, without attempting persistence, destructive actions, or real-world credential reuse. Keep the target loopback-only and preserve the current database and Phase 4/5 evidence. Remediation should follow in Phase 7.
