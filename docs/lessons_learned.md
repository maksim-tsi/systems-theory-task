# Lessons Learned

Date: 2026-02-01

## Purpose
This document captures high-level lessons learned during implementation to prevent repeating mistakes. It intentionally avoids duplicating devlog entries.

## Lessons
1. Validate semantic meaning of dataset flags early.
   - Action: cross-check dataset cards or sample records before encoding boolean semantics.

2. Treat control variables as model inputs, not always observed signals.
   - Action: if a candidate control (e.g., price/discount) is constant or zero, define a clear fallback or remove it from the model.

3. Enforce non-streaming data assumptions throughout tests and code.
   - Action: ensure both implementation and tests align with full-dataset loading requirements.

4. Keep derived datasets reproducible.
   - Action: regenerate artifacts after logic changes and document any behavioral shifts in analysis outputs.

## Update Rule
- Append new lessons with date and short actionable guidance when a recurring or high-impact mistake is discovered.
- Review this file at the start of any new modeling or preprocessing task.
