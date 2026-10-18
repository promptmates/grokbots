---
name: discover-ats-boards
description: >-
  Find working Greenhouse, Lever, Ashby, Workable or SmartRecruiters board
  tokens for companies and add them to the user's CareerMate target list, and
  (opt-in only) find public Workday career sites for the Workday list. Use when
  the user says "add [company] to my target list", wants to search a company not
  on the list, or wants to grow the searchable company universe from a list (VC
  portfolio, Cloud 100, Inc 5000, etc.).
---
# Discover ATS board tokens

Uses sibling `discover_boards.py` (Python 3.8+, stdlib only). It generates plausible tokens from each company name (e.g. notion, notionhq, palo-alto-networks) and probes each platform's public API; first hit per platform wins.

## Steps
1. Single company: `python3 discover_boards.py --company "Figma"`
   Batch: write names one per line to a file, then `python3 discover_boards.py --file companies.txt --output results.md`
   Options: `--platforms greenhouse,lever,ashby,workable,smartrecruiters`, `--json`, `--workers N`. With no args it runs a built-in list of ~131 companies.
2. Save onto the user's list with `--update`: `python3 discover_boards.py --company "Figma" --update` (or `--file companies.txt --update`). It appends to `~/careermate/target-companies.md`. If that file is missing, the script first copies the shipped list from the `live-ats-board-search` folder next to this skill (resolved from the script's own location, so the shell's cwd does not matter), then appends. You can also add a row by hand, `| Company | token | ~jobs | notes |`, under the matching platform section.
3. If the script finds nothing, find the token manually: open the company careers page, click a posting, read the URL:
   - `boards.greenhouse.io/COMPANY/jobs/123` or `job-boards.greenhouse.io/COMPANY/...` -> Greenhouse token COMPANY
   - `jobs.lever.co/COMPANY/abc-123` -> Lever slug COMPANY
   - `jobs.ashbyhq.com/COMPANY` -> Ashby token COMPANY
   - `apply.workable.com/COMPANY/` -> Workable slug COMPANY
   - `jobs.smartrecruiters.com/COMPANY/...` -> SmartRecruiters ID COMPANY
   - `TENANT.wdN.myworkdayjobs.com/en-US/SITE/...` -> Workday tenant TENANT, data center wdN, site SITE (see the Workday section; opt-in only)
   If the company uses iCIMS/Taleo/SuccessFactors/Personio (or Workday and the user has not opted in to Workday), it cannot be API-searched; tell the user to cover it with Boolean strings.
4. Report what was added. Tokens can go stale when companies rebrand or switch ATS; re-run discovery for boards that start returning 404.

## Workday (opt-in only)
Run this only when the user has opted in to Workday search (CareerMate Phase 0 Q4, saved as "Include Workday companies: yes"), or explicitly asks to add a Workday company. The user must have seen this disclaimer: "This checks public Workday job pages directly. Workday's site terms restrict automated access, so it's offered as an optional, use-at-your-own-discretion feature. It runs slowly, reads job listings only, and never logs in or applies."

Uses sibling `discover_workday.py` (stdlib only, read-only, globally paced). Per company it:
1. Sniffs the careers page for `*.wdN.myworkdayjobs.com/<site>` links (pass `--careers-url URL` for one company; otherwise it tries `www.<name>.com/careers` and `careers.<name>.com`).
2. Falls back to a pattern guess: tenant slugs from the name x wd1-wd12 (add `--wd-extra 100,103,108,503` for newer data centers), reading each host's robots.txt, which lists the public site names; if robots.txt lists none it tries common site names (External, Careers, ...).
3. Verifies with one CXS request (`POST .../wday/cxs/<tenant>/<site>/jobs`, limit 1) and keeps the site with the most jobs, preferring the main external site over campus, agency, private or regional sites.
It skips any site the tenant's robots.txt disallows, and reports those as skipped.

Commands:
- One company: `python3 discover_workday.py --company "Zendesk"`; with a slug hint when the tenant differs from the name: `--company "Flex|flextronics"`; with a known data center: `--company "Acme|acme|5"`.
- From a known Workday URL: `python3 discover_workday.py --url https://TENANT.wd5.myworkdayjobs.com/SITE`
- Batch and append: `python3 discover_workday.py --file companies.txt --append ~/careermate/workday-companies.md --section "Healthcare / Life Sciences"` (copy `../live-ats-board-search/workday-companies.md` to `~/careermate/` first so the shipped list stays untouched). New rows are added under a `###` section; rows already listed are skipped.
- Re-check the whole list (robots.txt + one CXS request per row, read-only): `python3 discover_workday.py --verify ~/careermate/workday-companies.md`. Remove rows that fail.
- Also available through `discover_boards.py --platforms workday` (or `--platforms greenhouse,...,workday`) with `--workday-append PATH`; Workday is never in the default platform list.

Check every appended row by eye: the pattern guess can land on a same-named organization (for example a college instead of a company) or a narrow site. Do not add defense-only employers unless the user asks for them. Many companies are not findable by name alone; ask the user for a link to one of the company's job postings and use `--url`.
