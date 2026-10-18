---
name: ta-people-role-scanner
description: Live snapshot of open Talent Acquisition / People roles (recruiting, recruiting ops, people systems/HRIS, people analytics, TA/People leadership, HRBPs) across 1,200+ verified company career boards. Use when the user asks "who's hiring in TA/recruiting/People right now?" or wants TA/People roles without a full CareerMate run.
---

# TA/People role scanner

Runs sibling `find_ta_roles.py` (Python 3.8+, stdlib only, public APIs, no auth). Typically finishes in seconds to a few minutes.

## Steps
1. Ask (or infer) filters: focus area, remote only, US only, Director+ only.
2. Run from this skill folder with Shell:
   - `python3 find_ta_roles.py` (everything)
   - `--remote`, `--us`, `--leadership`
   - `--focus recruiting|ops|systems|analytics|leadership|partners|all`
   - `--json` for JSON, `--output roles.md` to write a file, `--no-urls` to hide links
   Example: `python3 find_ta_roles.py --us --remote --focus ops --output /workspace/ta_roles.md`
3. The stderr summary shows counts by function; stdout is a markdown list grouped by company with [REMOTE] / [LEADERSHIP] badges.
4. Present the results (or attach the file). Only report roles the script returned, with their URLs. If few results, suggest dropping filters or a full CareerMate run.

Note: the script reads target-companies.md (~/careermate/ copy first, then the sibling copy, then ../live-ats-board-search/); pass --boards PATH to override. The hardcoded lists in the file are only a fallback.
