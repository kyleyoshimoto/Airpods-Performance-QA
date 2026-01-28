Reports Module – Quick Overview
===============================

Purpose
-------
The `reports/` module is responsible for turning **processed test artifacts**
into **human-readable HTML performance reports**.

It is intentionally separated from test execution so that:
- Tests cannot fail due to reporting issues
- Reports can be regenerated at any time
- Analysis and visualization can evolve independently

In short:
    run_tests.py  →  produces data
    reports/      →  visualizes data


How Reports Are Generated
-------------------------
Reports are generated via a dedicated CLI command:

    python -m reports.generate --run <RUN_ID>
    python -m reports.generate --latest

The command:
1. Loads processed artifacts from:
       logs/processed/<RUN_ID>/
2. Computes summary metrics (mean, p95, variance, etc.)
3. Generates charts (PNG)
4. Renders an HTML report using a Jinja2 template
5. Writes output to:
       reports/<RUN_ID>/report.html


Directory Structure
-------------------
reports/
├── generate.py
│   CLI entry point for report generation
│
├── report_generator.py
│   HTML rendering logic (Jinja2 templates)
│
├── templates/
│   └── report_template.html
│       Base HTML layout for all reports
│
└── <RUN_ID>/
    ├── report.html
    └── assets/
        └── connection_latency.png


Expected Inputs
---------------
The report generator expects the following artifact to exist:

    logs/processed/<RUN_ID>/connection_latency.json

This file is produced by the ConnectionLatencyScenario during test execution.

If the artifact is missing, report generation will fail fast with a clear error.


Why Reporting Is Not Automatic
------------------------------
Report generation is intentionally *not* part of `run_tests.py`.

Reasons:
- Keeps test execution deterministic
- Prevents partial data from breaking runs
- Allows re-generating reports after code changes
- Mirrors real-world QA and CI pipelines

Automation can be added later via:
    python -m orchestrator.run_tests --report


Extending Reports
-----------------
Future extensions may include:
- Multi-scenario summaries
- Regression comparisons across runs
- PASS/FAIL thresholds
- Trend charts over time
- CI-friendly JSON summaries

This module is designed to scale as analysis complexity increases.
