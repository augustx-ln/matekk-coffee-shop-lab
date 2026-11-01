# Phase 4 — Authorization and Input-Validation Assessment

**Status:** Completed with one explicitly deferred test (logout endpoint semantics)
**Date:** 2026-11-01
**Target:** Matekk Coffee Shop, local Kali lab (`127.0.0.1:8000`)

## Confirmed findings

| ID | Finding | Evidence | Assessment |
|---|---|---|---|
| P4-01 | Broken object-level authorization (IDOR) | Customer account received HTTP 200 and another customer's synthetic private record for IDs 1001, 1002 and 1003 | High priority; confirmed behaviorally |
| P4-02 | Client-controlled MIME type accepted | Plain-text test file declared as `image/png` was accepted by `POST /api/reviews` and appeared in quarantine as review 3 | High priority; confirmed behaviorally; no execution demonstrated |

## Controls that passed

- Anonymous access to `/api/me` returned HTTP 401 after restart.
- Customer access to admin summary, users and reviews returned HTTP 403 in the manual test.
- Admin access to summary, users and quarantine returned HTTP 200 in the manual test.
- Upload size limit and MIME allowlist were present in source review; signature validation was absent.

## Prior reconnaissance exposure (Phase 3)

Anonymous requests previously returned HTTP 200 for `/documents/`, `/backup/`, `/internal/`, and `/staff/archive`. These remain Phase 3 findings and are not reclassified as new Phase 4 findings.

## Data integrity and session handling

- Post-test SQLite `PRAGMA integrity_check`: `ok`.
- Post-test row counts: users=2, customer_private_records=3, reviews=3.
- Review count increased from 2 to 3, matching the quarantined MIME-spoof test upload.
- The original Uvicorn process (PID 11465) was stopped and a new process (PID 20085) started. The new process returned HTTP 200 on `/api/health`.
- Source review confirms sessions are held in process memory; restarting the process clears those sessions. This invalidates the exposed in-memory session tokens by design.
- **Not tested:** the `/logout` endpoint itself and whether a token is rejected immediately after a logout request. Do not claim logout behavior is verified.

## Evidence handling

- Manual test summary: `manual/phase4-manual-validation-summary.txt` (raw bearer tokens and passwords excluded).
- Baseline and test plan retained in this directory.
- No application source files or database records were modified for remediation.
- Evidence directory ownership was corrected to `agustx:agustx` so the lab operator can manage the results.

## Phase 5 entry conditions

Phase 5 may proceed as a controlled impact assessment against this local-only synthetic lab. Keep tests non-destructive, preserve database snapshots, and do not expose the service beyond loopback. The logout endpoint check remains a deferred Phase 4 follow-up and can be performed before remediation retesting.
