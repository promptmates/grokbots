---
name: boolean-search-plan
description: >-
  Generate CareerMate's personalized search plan - copy-paste Boolean strings
  (LinkedIn, Google, Greenhouse, Ashby, Lever, Workday, Getro, Jobvite, Taleo),
  platform strategy, weekly routine and approach by match type. Use as Phase 4
  of a full run, or on its own when the user wants a quick search strategy
  without a live board search (the zero-setup "Prompt Pack" flow).
---
# Boolean strings and search plan

## Quick mode (no live search; adapted from the CareerMate Prompt Pack)
Inputs: resume / LinkedIn summary / plain description, optional target JD for calibration, and preferences (location, work model, stage, industries to avoid, deal-breakers, scope: same title / adjacent / career pivot - recommend adjacent).
1. **My Expanded Profile**: core skills (5-10, filler stripped), adjacent skills (3-7), title expansion (8-12 alternate titles), transferable outcomes (3-5 measurable), industries (direct + adjacent). Ask "Do these feel right? Add or remove any before I continue." and wait.
2. **Roles I Am Probably Missing**: 3-5 titles they likely aren't searching (one line why they qualify), 1-2 industries, 1-2 company stages or function areas. Be specific (name example companies and why), not "consider operations roles".
3. **Boolean strings** (below).
4. **Search plan** (sections 2-4 below).
Do not invent job postings or URLs: this mode produces strategy, not results.

## Section 1: Custom Boolean strings (for the user's browser)
Fill with the user's confirmed titles and locations. Copy-paste ready, no placeholders left.
```
inurl:boards.greenhouse.io ([TITLES]) AND ([LOCATIONS])
inurl:jobs.ashbyhq.com ([TITLES]) AND ([LOCATIONS])
inurl:jobs.lever.co ([TITLES]) AND ([LOCATIONS])
site:myworkdayjobs.com ([TITLES]) AND ([LOCATIONS])
inurl:getro.com ("jobs" OR "careers" OR "openings") AND ([TITLES]) AND ([LOCATIONS])
inurl:jobs.jobvite.com ([TITLES]) AND ([LOCATIONS])
inurl:taleo.net ([TITLES]) AND ([LOCATIONS])
```
Always include the `site:myworkdayjobs.com` string when the user declined the opt-in Workday search, or when it did not run or was stopped for blocks: many large employers (healthcare, biotech, financial services, enterprise tech) post only on Workday. Example: `site:myworkdayjobs.com ("Director of Product Operations" OR "Head of Product Operations") ("remote" OR "Atlanta")`.
Example (recruiter, remote + SF): `inurl:boards.greenhouse.io ("recruit*" OR "talent acquisition" OR "sourcer") AND ("remote" OR "virtual" OR "work from home" OR "San Francisco")`
Also give:
- LinkedIn: `("Title A" OR "Title B" OR "Title C") AND ("remote" OR "City, State")`
- Google jobs on LinkedIn: `site:linkedin.com/jobs ("Title A" OR "Title B") "remote"`
- General Google: title keywords + "remote" or location.

## Section 2: Platform strategy (pick what fits their target, explain why)
Consider.com (VC-backed growth companies); Wellfound (early-stage startups, advisory/fractional); Climatebase (mission-driven climate, only if relevant); direct ATS boards (specific target companies); Bolster.com (executive and fractional, if senior).

## Section 3: Weekly routine
- Monday: run the Boolean strings, check postings from the last 3 days.
- Wednesday: check aggregator platforms, apply to Stretch Matches.
- Friday: review Adjacency Discoveries, update profile if new patterns emerge.

## Section 4: What to do when you find something
- Strong: apply directly, find a connection at the company.
- Stretch: tailor resume to overlapping skills, address gaps in a cover note.
- Adjacency: lead with transferable outcomes, not title history.

Rules: specific to this person, active voice, no emojis, no filler; mention resume gaps once, practically.
