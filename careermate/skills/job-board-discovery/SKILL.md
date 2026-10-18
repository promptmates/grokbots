---
name: job-board-discovery
description: >-
  Discover open roles on LinkedIn, Indeed and Glassdoor through the box browser,
  then resolve each one to the company's own careers or ATS posting. Use during
  a CareerMate run (Phase 2) when the user asks to include LinkedIn, Indeed or
  Glassdoor, wants to "search wider" than the ATS board list, or asks what those
  boards show for their confirmed titles.
---
# Job board discovery (LinkedIn, Indeed, Glassdoor)

Job boards find roles the ATS board list misses, especially at companies on Workday, iCIMS, Taleo or SuccessFactors. They are for discovery only. Every role you report must link to the company's own careers or ATS page.

## Who does what
`sign-in`, `in-chat-forms`, and `site-playbooks-linkedin` are platform-provided skills on Grok Bot. They are optional and are not part of this repo, so it is normal that they are not in the skills folder. When one of them is available, follow it. When it is not, use the steps written here.
- The main agent runs this skill. All browser work goes through a `computerUse` subagent that the main agent dispatches, one board per dispatch. The subagent does not read skills, so put every rule it needs (URL or search-box steps, pacing, what to read back, the stop rules below) in the Task text.
- Secrets never go in the Task text. Sign-in passwords and one-time codes come from the user through the secure in-chat form (`RequestUserForm`). Follow the platform `sign-in` and `in-chat-forms` skills when they are available. Never ask the user to paste a code or password in chat.
- The lookup is read-only: never apply, save, follow, message or set alerts on any board.

## Inputs
- The confirmed title expansion from CareerMate Phase 1 (do not run before the user confirms titles).
- Locations: "Remote" (country-scoped, e.g. United States) plus the user's home metro. Add other metros only if the user named them.
- Run every confirmed title x every location. Optionally add the posted-date filter the user asked for (default last 30 days).

## LinkedIn
- Use LinkedIn jobs search in the box browser's signed-in session. The anonymous guest endpoint (`/jobs-guest/...`) gets rate-limited with HTTP 429 on runs of this size; if any guest request returns 429, stop using it for the rest of the run and switch to the signed-in browser search, with no retries.
- If the platform `site-playbooks-linkedin` skill is available, read it before dispatching and follow its URL patterns, filters, field extractors and pacing, with the signed-in browser path as the default for multi-title runs. If it is not, use the URL and steps below.
- URL: `https://www.linkedin.com/jobs/search/?keywords=<"Title">&location=<Location>&f_TPR=r2592000` (add `&f_WT=2` for remote). Read title, company, location, posted date, salary if shown, the job URL, and whether the apply button is Easy Apply or an external link (the external link usually is the company ATS).
- If the session is signed out, sign in with the secure form (the platform `sign-in` skill when it is available), then screen handoff if needed, then re-dispatch.

## Indeed
- Indeed requires signing in for search at this volume. Sign-in may ask for an email code and then an SMS code. The user must supply each one through the secure in-chat form; codes expire within minutes, so send the form as soon as the code page is open (set submitAfterFill for a code-only page). The session persists in the box browser for later runs.
- Cloudflare throttles heavy runs. Pace the searches: one search page at a time, roughly 20-40 seconds between searches, and no rapid pagination. On a Cloudflare challenge, let the subagent try the checkbox once; if it persists, pause the board for several minutes or finish with the boards that work, and say so. Do not loop.
- URL: `https://www.indeed.com/jobs?q=<"Title">&l=<Location>&fromage=30`. Read title, company, location, salary if shown, posted date and the job URL.

## Glassdoor
- Works without signing in. Close any sign-in modal and keep going.
- Glassdoor ignores URL query parameters, so do not build search URLs. Have the subagent type the title into the job title search box and the location into the location box, submit, then read the results.
- Read title, company, location, salary estimate (mark it as Glassdoor's estimate, not posted comp), posted age and the job URL.

## Resolve to the company's own posting (required)
1. For every discovered role, find the same posting on the company's own careers page or ATS (Greenhouse, Lever, Ashby, Workable, SmartRecruiters, Workday, iCIMS, Taleo, SuccessFactors, etc.): follow the board's external apply link, or open the company careers page and search the title.
2. Confirm the company page shows the same title and location and that it is open. Take comp from the company page when it lists a range; do not carry board estimates over as posted comp.
3. Use that company URL as the apply link. If you cannot find a company link, keep the role only if the user wants board-only leads, and flag it "no company link found (board listing only)". Never present a board URL as the apply link.

## Dedupe and tag
- Dedupe against the `live-ats-board-search` results and across boards: same company plus same or near-identical title plus overlapping location is one role. Prefer the ATS record's data.
- Tag every row's source: the board(s) where it was found plus the ATS, for example "LinkedIn", "Indeed + Glassdoor", "LinkedIn + Greenhouse (also on ATS list)".
- Flag staffing-agency postings rather than hiding them.

## Hand-off
Return the resolved roles (title, company, location, work model, comp or "not stated", source tag, company apply link, board link) to CareerMate Phase 3 for scoring. Report per board how many searches ran, how many roles were found, how many resolved to a company link, and any board that was throttled, blocked or skipped.
