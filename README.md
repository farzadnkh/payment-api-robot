# Checkout Payment API Automation

API automation suite for the checkout payment endpoint. Validates response schema, types, mandatory fields, and business rules (R1–R7). Built with **Robot Framework**, **RequestsLibrary**, and BDD-style scenarios.

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Mock server + testdata** | Enables local execution without a real backend; full control over response variants. |
| **RequestsLibrary** | Per spec; ensures tests perform real HTTP calls and exercise the full flow. |
| **Layered structure** | `features/` = scenarios only; `resources/` = keywords; `steps/` = validation; `apis/` = HTTP/JSON. Clear separation of concerns. |
| **variables.robot** | Centralizes config (BASE_URL, SESSION); easier maintenance and environment override. |
| **Early server check** | `Ensure Server Available` in Suite Setup fails fast with a clear message if mock server is not running. |

## Scope

- **In scope:** Response checks (schema, types, mandatory fields), business rule validation (method clickability, option eligibility), negative/edge cases, actionable failure messages.
- **Out of scope:** UI automation, actual payment processing, pricing correctness beyond presence/type.

## Project Structure

```
payment-api-robot/
├── features/           # BDD scenarios (S1–S10)
├── resources/          # Robot keywords, variables (POM-like)
│   ├── payment_resources.robot
│   └── variables.robot
├── steps/              # Validation logic – R1–R7 (Python)
├── apis/               # HTTP + JSON handling (Python)
├── testdata/           # Sample API response JSON files
├── mock_server.py      # Flask mock server (serves testdata by scenario)
├── requirements.txt
├── .gitignore
└── .github/workflows/  # CI
```

> **Note:** `payment_validation.feature` is BDD specification (Gherkin); Robot executes `.robot` files. The `.feature` file documents the scenarios for stakeholders.

## Data and Approach: Mock Server + RequestsLibrary

The suite uses a **tiny Flask mock server** (`mock_server.py`) that serves sample JSON files from `testdata/`. Tests call the API via **RequestsLibrary** (`GET On Session`) with a `scenario` query param (s1–s8, plus dedicated inline responses for s9 and s_r3) to receive the corresponding response. This satisfies the PDF requirement for "API tests written with RequestsLibrary".

| File | Scenario |
|------|----------|
| `happy_path.json` | S1 – Happy path |
| `bnpl_blocked.json` | S2 – BNPL blocked |
| `insufficient_credit.json` | S3 – Insufficient credit (R5) |
| `non_active_option.json` | S4 – Non-active option (R5) |
| `multiple_default.json` | S5 – Multiple default (R6 fail) |
| `missing_field.json` | S6 – Missing required field |
| `wrong_type.json` | S7 – Wrong type |
| `non_success.json` | S8 – Non-success status |

All technical actions (HTTP via RequestsLibrary, JSON parsing, validations) live in `resources/` and `steps/`; `features/` contains only scenario flow.

## Assumptions

1. **Base URL:** Default `http://localhost:8080` (per PDF; in `variables.robot`); override with `BASE_URL` if needed.
2. **R3 (is_wallet):** The spec says “is_wallet must be false if type is not wallet”. The response schema in the task does not define `is_wallet`. Validation treats it as **optional**; when present and `true`, `type` must be `"wallet"`.
3. **BNPL options:** For methods with `type=bnpl` and `is_clickable=true`, `options` must be an array (can be empty). For non-clickable BNPL, `options` may be missing or empty.
4. **Case sensitivity:** `price_type` is validated as `CASH_PRICE` or `CREDIT_PRICE` (case-sensitive) per task.

## How to Run

### Prerequisites

- Python 3.8+
- pip

### Install

```bash
cd payment-api-robot
pip install -r requirements.txt
```

### Start mock server (Terminal 1)

```bash
python mock_server.py
```

### Run tests (Terminal 2)

```bash
robot --outputdir results features/
```

If `robot` is not on PATH, use: `python -m robot --outputdir results features/`

### Run with report / log

```bash
robot --outputdir results --loglevel DEBUG features/
```

Reports: `results/report.html`, `results/log.html`.

### Override base URL

```bash
robot --variable BASE_URL:http://localhost:9000 --outputdir results features/
```

## Test Cases (Minimum 8)

| # | Scenario | Type | Expected |
|---|----------|------|----------|
| S1 | Happy path (online, wallet, BNPL; all clickable) | Positive | All rules pass |
| S2 | BNPL blocked | Positive | Not selectable; options may be empty |
| S3 | Insufficient credit (`credit=0`) | Positive | Option ineligible by R5 |
| S4 | Non-active option (`is_active=false`) | Positive | Option ineligible by R5 |
| S5 | Multiple `is_default=true` among eligible | Negative | Fail with R6 message |
| S6 | Missing required field | Negative | Validation fail |
| S7 | Wrong types | Negative | Type validation fail |
| S8 | Non-success (`body.status != 200`) | Negative | Fail with status diagnostics |

In addition, the suite includes:

- **S9**: HTTP 500 transport failure (server returns status 500) – negative, HTTP-level robustness.
- **S10**: Wallet rule violation (`is_wallet=true` while `type!=wallet`) – negative, explicit R3 coverage.

## Business Rules Validated (R1–R7)

- **R1:** `payment_methods` is an array; each element has `id`, `type`, `title`, `is_clickable`.
- **R2:** Method is selectable only if `is_clickable=true`.
- **R3:** If `is_wallet` is present and `true`, `type` must be `"wallet"`.
- **R4:** `options` must be an array when present; for BNPL clickable method, options must be an array.
- **R5:** Option eligible only if `is_active=true` and `credit>0`.
- **R6:** Among eligible options, exactly one has `is_default=true`.
- **R7:** `price_type` is `CASH_PRICE` or `CREDIT_PRICE` (case-sensitive).

## Optional bonus: CI (GitHub Actions + GitLab CI)

### GitHub Actions (`.github/workflows/robot.yml`)

- **Trigger:** Push or pull request on `main`/`master`.
- **Runs:** Robot suite in a Python 3.11 environment.
- **Publishes reports:**
  - **Job summary:** Pass/fail/total table in the Actions run summary.
  - **Artifact:** `robot-reports` (report.html, log.html, output.xml) available to download.

### GitLab CI (`.gitlab-ci.yml`)

- **Trigger:** Push to any branch.
- **Runs:** Robot suite in a `python:3.11-slim` Docker image.
- **Artifacts:** `results/` published as `robot-reports-<commit-sha>` (report.html, log.html, output.xml).

