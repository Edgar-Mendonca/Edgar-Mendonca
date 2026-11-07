---
project: cairn
area: project-controls
---
# Cairn: a browser scheduler

An offline-first, single-project scheduler in React, TypeScript and Vite with a real scheduling engine, not just a
Gantt picture: critical path with all four dependency types, leads and lags, task constraints, slack and critical
tasks, resources and levelling, baselines, earned value, several views and report definitions. It imports and
exports its own JSON, common scheduler XML and XER files, MPX and CSV, and Excel, with browser storage and autosave,
and builds to a single page for static hosting.

An audit listed what it still needed: dated, auditable progress updates; actual cost history; durable storage;
controls-grade revisions; schedule quality checks; evidence attached to progress; round-trip validation of file
exchange; collaboration; and security hardening. A count of test cases is not proof that the tests pass. The same
needs shaped Datum Plan.
