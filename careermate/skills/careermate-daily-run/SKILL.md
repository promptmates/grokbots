---
name: careermate-daily-run
description: >-
  CareerMate daily new-matches run. Use when a routine says "run the
  careermate-daily-run skill", or the user asks "any new jobs today?", "check
  for new matches" or "what's new since yesterday?". Reports only roles not seen
  in an earlier run and not already in the application tracker, scored and
  re-ranked by what has worked so far. Stays silent when nothing is new. On
  Fridays it also adds the weekly application summary.
---
# CareerMate daily new-matches run

Runs unattended from a routine. Reuse what the full run (`careermate-job-search`) saved; never re-ask intake questions here. Read `../careermate-job-search/guardrails.md` and follow it for all output.

Scripts: sibling `daily_diff.py`; `../live-ats-board-search/search_boards.py`; `../careermate-tracker/tracker.py` (daily_diff.py imports it for job keys and learned signals). All data lives in `~/careermate/` (below, `CM`). Use the user's time zone for "today" and the weekday (daily_diff.py resolves it like tracker.py: `--tz`, then `$CAREERMATE_TZ`, then the prefs "Time zone:" line, then the system zone).

## 1. Check inputs
- If `CM/search-preferences.md` says "CareerMate paused: yes", stop and post nothing. (Pausing normally pauses this routine; this catches a routine that still fires.)
- Need `CM/search-preferences.md` and `CM/keywords.txt` (confirmed phrases, one per line). If either is missing, post one line: "I need a full CareerMate run before I can watch for new roles. Say 'run CareerMate' when you're ready." and stop. This is the only setup message the daily run sends.
- Filters come from `CM/daily-config.json`. If it is missing, or its `prefs_sha` differs from the sha256 of `search-preferences.md` (`sha256sum`), rebuild it from the prefs with the table below and keep every key. Only stated preferences become filters; anything "not stated" stays empty. When a filter changes, daily_diff.py re-checks roles it filtered out before, so a loosened filter can surface them.

| Preference | daily-config.json |
|---|---|
| Base pay floor | `pay_floor` (USD per year; null when no floor), `pay_buffer` 0.15 |
| Locations / work model | `location_allow` regexes (for example `remote`, `denver`); `location_block` regexes for regions ruled out (for "US only remote", list non-US countries and regions) |
| Deal-breakers, excluded role types | `exclude_title_patterns` |
| Excluded industries | `exclude_sections` (board-list headings, for example `Fintech`), also passed to search_boards.py `--exclude-section` |
| Excluded companies | `exclude_companies` |
| Target level, only if stated | `seniority_patterns` (scoring only); `require_title_patterns` only if the user said they want nothing below a level |
| Core skills from the profile | `skills` (skill-overlap scoring against the posting text) |
| Company size, where known | `company_sizes` {"Company": "1k-10k"} (signals only; postings rarely state size) |
| Workday choice | `workday.opt_in` (true only for "Include Workday companies: yes"), `workday.day` "Monday", `workday.search_terms` |
| Match profile present (`CM/match-profile.md`) | `description_match.enabled` true, `description_match.day` "Monday", `description_match.max_description_only` 60; false when there is no profile file |

## 2. Update the tracker first (quiet)
If `CM/applications-tracker.md` exists:
- If the user set up email forwarding (prefs line "Tracker email: ..."), process new tracker email per the `careermate-tracker` skill, without posting a separate message; fold any status changes or leads into this run's message. That includes interview check-ins: record a concrete interview time and set up its check-in routine, or, for a scheduling link only, ask the user in this run's message to share the time once booked.
- `python3 ../careermate-tracker/tracker.py refresh` (marks applications with no reply after 14 days as ghosted), then `tracker.py learn` (rewrites `CM/learned-signals.md` and `CM/learned-weights.json`).

## 3. Search
ATS boards, every run:
`python3 ../live-ats-board-search/search_boards.py --boards <CM/target-companies.md if present, else ../live-ats-board-search/target-companies.md> --keywords-file CM/keywords.txt [--exclude-section X ...] > /tmp/cm_daily_ats.json`

Description matching, only when `description_match.enabled` is true AND today is `description_match.day` (Monday by default), or the user asks for it in chat:
- Add `--match description --profile CM/match-profile.md --max-description-only <description_match.max_description_only>` to whichever search command runs today, and run that command in the background (Shell `block_until_ms: 0`). It reads every description, so the board search takes about 5 minutes instead of 30 seconds; on Workday days it runs alongside Workday and adds little wall time. Other weekdays stay title-only. Weekly is enough for the same reason as Workday: the ledger keeps first-seen dates, so Monday catches any off-title role posted since the last pass.
- If fastembed is missing or the model cannot load, the script uses its TF-IDF fallback by itself. The script makes at most one quiet fastembed install attempt ever (see `live-ats-board-search`); do not install anything yourself from the daily run.
- The first description pass on an existing ledger does not post a backlog: daily_diff.py records that day's description-only rows as seen without reporting them (stderr shows "description-only baseline N") and from then on reports only new ones.

Workday, only when `workday.opt_in` is true AND today is Monday (or the user asks for it in chat):
- Workday is paced at about 1 request per second, so it costs roughly companies x search terms seconds (112 companies x 11 terms took about 30 minutes). Once a week with 6-10 broad terms keeps it near 12-20 minutes and still catches every posting that stays up a few days. Weekly is enough because the ledger tracks first-seen dates, so Monday's run reports everything that appeared since the last Workday pass.
- Search terms: `workday.search_terms`, or `CM/workday-search-terms.txt` (one per line). If neither exists, pick 6-10 broad terms from the confirmed titles (for example "product marketing", "data platform", "operations"), save them to that file, and use them. The full keywords file still filters titles.
- On those days run one command instead of the ATS-only one (it searches the ATS boards and Workday together), in the background (Shell `block_until_ms: 0`), and wait for it:
  `python3 ../live-ats-board-search/search_boards.py --boards <same> --keywords-file CM/keywords.txt --include-workday --workday-search "<term>" ... --workday-details --workday-stats /tmp/cm_daily_wd_stats.json > /tmp/cm_daily_ats.json`
- Never loosen the built-in pacing. If the stats show the run stopped for blocks, add `--note "Workday check stopped early (sites were blocking); it will try again next Monday."`.

## 4. Diff, filter, score
`python3 daily_diff.py --search /tmp/cm_daily_ats.json [--boards <same boards file>] [--note "..."] > /tmp/cm_daily_digest.md`
- Ledger `CM/seen-jobs.json`: one entry per role keyed by a stable ID (Greenhouse job id, Ashby/Lever posting UUID, Workday tenant + requisition id, else the normalized URL) with `first_seen`, `last_seen` and an outcome (reported, filtered:<reason>, in_tracker, repost-of, seeded). Entries unseen for 120 days are pruned. A role at the same company with the same title seen in the last 30 days counts as a repost, not new.
- New rows get the full-run filters: title/company/industry exclusions, location, then a posting-detail fetch (only for new rows) for pay, location detail, remote type and posting date. Pay floor: keep if the posted top is at or above the floor; keep and label "below floor on base; bonus may close the gap" if within 15% below; drop if more than 15% below; "not stated" stays in.
- Rows with `match_reason: "description"` (found by description, not title) go through the same filters. They get the adjacency weight, and their skill overlap comes from `matched_terms` when `skills` is empty. Their score is capped at 74 (Stretch) because nobody has read the posting yet; after reading, you may call one Strong in the post if the overlap clearly earns it. The digest notes "found by its description, not its title" with the terms it mentions. Before posting, read the posting text of each such row in the digest and replace that note with one plain line on why it fits, naming the overlap; if on reading it has no real overlap with the profile, leave it out of the post and say how many you left out.
- Score: the full run's Phase 3 weights (skill overlap 0.35, adjacency 0.20, preference fit 0.20, recency 0.15, seniority 0.10), approximated from the posting text, plus learned adjustments from `CM/learned-weights.json` (at most +/-5 per signal type, +/-10 total, re-rank only). Every adjusted row carries its reason in the digest notes.
- Baseline: if `CM/seen-jobs.json` does not exist yet, run daily_diff.py with `--seed` instead, then post one line: "I'm now watching for new roles. From the next run on you'll only hear from me when something new shows up." (The full run normally seeds the ledger, so this is rare.)

## 5. Post
- Empty digest (no new roles): post nothing. Do not send "no new matches" messages. Exception: Fridays, below.
- Otherwise post the digest as written (table: score, title, company, location, pay, source, link; notes for learned adjustments, unstated locations and missing details; counts filtered out). Up to 15 rows show; the rest are saved to `CM/daily/new-<date>.json` and the digest says how many.
- Add tracker changes from step 2 in at most three lines, and any new leads.
- Fridays: if the tracker has applications, append `python3 ../careermate-tracker/tracker.py summary` (pipeline counts, what's working, follow-ups to consider). Post it even when no roles are new.
- If `tracker.py queue` shows roles saved for today after yesterday's limit, list them in one line each and ask which ones the user still wants; they need a fresh yes, by name.
- Close with one optional offer, for example "Want a fit check on any of these, or an application for the ones you pick? I tailor each one and send at most 15 a day." Never apply, start an application, email anyone or follow up on the user's behalf from this run.

## Do not
Apply or start an application (the user picks roles in chat, one at a time); run while paused; re-ask intake; widen searches beyond the saved keywords and match profile; run description matching on days other than the configured one unless asked; turn Workday on without the saved yes; run Workday on other days unless asked; hide a role because of learned signals; post when nothing is new (except the Friday summary); report the same role twice.
