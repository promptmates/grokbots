---
name: live-ats-board-search
description: >-
  Search live public Greenhouse, Ashby, Lever, Workable and SmartRecruiters job
  boards (no auth) for open roles matching a list of title/skill keywords, and
  optionally read every job description and rank it against the person's
  profile so roles with unusual titles still surface. Use during a CareerMate
  run (Phase 2) or whenever the user asks to find real, currently open postings
  at target companies. Can also search public Workday career sites, but only
  when the user has opted in to Workday.
---
# Live ATS board search

Board list: sibling `target-companies.md` (1,200+ verified tokens, last verified Oct 15 2026). If the user has a personal copy at `~/careermate/target-companies.md`, use that instead (create it by copying the sibling file the first time the user customizes the list).

APIs (no auth):
- Greenhouse `https://boards-api.greenhouse.io/v1/boards/{token}/jobs` (add `?content=true` for descriptions; detail: `.../jobs/{job_id}`)
- Lever `https://api.lever.co/v0/postings/{slug}?mode=json` (list already includes descriptionPlain and lists)
- Ashby `https://api.ashbyhq.com/posting-api/job-board/{slug}` (list already includes descriptionPlain)
- Workable `https://apply.workable.com/api/v1/widget/accounts/{slug}` (add `?details=true` for descriptions)
- SmartRecruiters `https://api.smartrecruiters.com/v1/companies/{id}/postings?limit=100&offset=N` (paginate; unknown IDs return 0 jobs; descriptions only from the per-posting endpoint `.../postings/{id}`)

## Rules
- Use Shell with python3 (or curl), NOT WebFetch: WebFetch truncates large JSON and misses most jobs on boards with 50+ roles.
- Search ALL boards except industries the user explicitly excluded. Target all; minimum 60; explain if fewer.
- Skip 404s/empty boards silently, no retries. Only mention failures if more than half fail (network problem).
- Every result must carry its direct posting URL, exactly as the API returned it.

## Two match modes
- `--match title` (default, about 30 seconds for 1,260 boards): keyword phrases against job titles. Use it for daily runs and quick checks.
- `--match description` (alias `--semantic`, about 4-5 minutes for 1,260 boards): reads every description and ranks it against a match profile, so a role like "Workforce Systems Lead" whose work fits the person is not dropped for its title. Use it on first and full runs. It needs `--profile FILE` (see below); without one it prints a notice and falls back to title mode.

## Steps
1. Build a list of keyword PHRASES from the confirmed title_expansion (+ core skill phrases). Each phrase is kept whole: commas inside a title stay part of it ("VP, Sales" is one phrase, not "vp" and "sales").
2. Run the sibling script with the phrases as repeatable `--keyword` args, or write them to a file (one phrase per line, or pipe-separated; lines starting with # are ignored) and pass `--keywords-file`:
   `python3 search_boards.py --boards target-companies.md --keyword "VP, Sales" --keyword "head of operations" --keyword "supply chain analyst" [--exclude-section Fintech] > /tmp/careermate_matches.json`
   `python3 search_boards.py --boards target-companies.md --keywords-file /tmp/careermate_keywords.txt > /tmp/careermate_matches.json`
   `--boards` is tried as given, including a cwd-relative name. If that file is not there, the script uses `~/careermate/target-companies.md`, then `target-companies.md` next to the script, and says which file it opened. The same command works from any folder.
   Matching is case-insensitive and on whole words in the job title. Punctuation and hyphens count as spaces and "&" as "and", so "VP, Sales" matches "VP Sales Operations" and "full-stack" matches "Full Stack", but "people" does not match "PeopleSoft". Word order matters: add variants such as "VP of Sales" and "Vice President, Sales" as separate phrases. End a phrase with `*` for a prefix match on its last word ("recruit*" matches Recruiter and Recruiting). Each result carries a `matched` list naming the phrases it hit. The old comma-separated `--keywords` flag is gone and exits with an error.
   For a description run, add `--match description --profile ~/careermate/match-profile.md`, run it in the background (Shell `block_until_ms: 0`), and write to a file so an interruption does not lose the results:
   `python3 search_boards.py --boards target-companies.md --keywords-file ~/careermate/keywords.txt --match description --profile ~/careermate/match-profile.md --with-text --match-stats /tmp/careermate_match_stats.json > /tmp/careermate_matches.json`
3. For strong title matches on Greenhouse, fetch the detail endpoint to confirm skill overlap and extract comp/location/remote. Do not guess comp.
4. Deduplicate (same role under multiple tokens) and hand results to scoring.

## Description mode
Match profile: `~/careermate/match-profile.md`, written by the full run (`careermate-job-search` Phase 1) from the sibling `match-profile-template.md`. Sections whose heading mentions skills, tools or terms hold match terms (one per line or pipe-separated, `*` for a prefix match). Every section feeds the similarity score; Summary and Target problems count most (weight 2), Outcomes and Core skills next (1), the rest least (0.5). Keep it in the person's words. It is private: no employer names, salary or contact details are needed for matching.

How it works:
- Fetch. Descriptions come from the list calls where the API has them (Greenhouse `?content=true`, Ashby, Lever, Workable `?details=true`), so there is one request per board as in title mode, only larger. SmartRecruiters has no description in its list, so the script fetches the per-posting detail only for jobs that pass the title or loose-title check, title hits first, at most `--detail-cap-per-board` (default 40) per board, paced by `--detail-interval` (0.25 s), and cached by posting id. Timeouts are the same as title mode (30 s for the larger Greenhouse and Ashby payloads).
- Pass 1, recall. A job stays if its title hits a keyword phrase, or one meaningful word from the phrases is in the title (generic words such as manager, senior, operations, platform do not count), or its description contains at least `--min-term-hits` (default 2) distinct profile terms. Terms that appear in more than `--common-term-share` (5%) of all postings, usually company boilerplate, do not count toward that minimum; the stats file lists them as `common_terms`.
- Pre-rank. If more than `--prerank-keep` (3,000) non-title jobs survive, a stdlib TF-IDF score keeps the best 3,000 for the embedding model. Every title hit is kept.
- Pass 2, ranking. `semantic_score` = 0.8 x description similarity + 0.2 x title similarity to the keyword phrases. Description similarity is the weighted mean, over profile sections, of the cosine with the best-matching 1,000-character chunk of the description (first 6,000 characters, title prepended).
- Output. Every title hit is returned as in title mode. Description-only rows are returned when `semantic_score` is at or above the cutoff (0.45 with the embedding model, 0.12 with TF-IDF; override with `--semantic-min`), best first, at most `--max-description-only` (default 400).

Backends (`--embed-backend auto`, the default, picks the first that works):
- `fastembed` with `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions, about 90 MB, CPU only, downloaded once to `~/.cache/careermate/models`). If fastembed cannot be imported, description mode makes one quiet attempt, ever, to install it (`pip install --user --break-system-packages fastembed`, up to about 3 minutes; a marker file `~/.cache/careermate/fastembed-install-attempted` stops later attempts, and `CAREERMATE_NO_AUTO_INSTALL=1` skips it). If that fails or times out, the run carries on with TF-IDF. Stderr always prints one line, `semantic: backend <name>`, naming the backend used. The first fastembed run also downloads the model. About 120 descriptions per second on 8 cores when nothing is cached.
- `tfidf`, stdlib only. Used automatically when fastembed is not installed, the model cannot be downloaded, or embedding fails mid-run. The run never fails for lack of the model; stderr says which backend ran and every row's score comes from that backend. TF-IDF is weaker on wording that differs from the profile, so it returns fewer description-only rows.
Cache: `~/.cache/careermate/match-cache.sqlite` holds embeddings keyed by model and text hash, plus SmartRecruiters descriptions keyed by posting id. Entries unused for 45 days are pruned at the end of each run. In testing it reached about 200 MB; delete it any time to reset, nothing else depends on it.

Extra output fields in description mode (title mode output is unchanged):
- `match_reason`: `title` (title hit only), `title+description` (title hit and the description also clears the cutoff with at least one profile term or loose title word), or `description` (found only through the description).
- `semantic_score`, `description_similarity`, `title_similarity`: from the backend that ran. Compare scores only within one run.
- `matched_terms`: profile terms found in the description. Use these to explain an off-title row.
- `description` (only with `--with-text`): the plain description, first 6,000 characters, so the agent can read it without another request.
Pay, location and remote fields are only what the API returned. Missing stays missing; do not fill them from the description by guessing. The script applies no preference filters except `--exclude-section`; location, pay floor (with the 15% buffer) and exclusions are applied afterwards exactly as in title mode.
`--match-stats FILE` records jobs read, pass counts, cutoff, backend, common terms and seconds per stage.

Measured on 1,260 boards (65,600 open jobs, Oct 2026, 8-core box):
| Run | Wall time | Peak memory | Notes |
|---|---|---|---|
| Title mode | 24-31 s | 0.45 GB | |
| Description mode, empty cache | about 5 min | 2.2 GB | fetch 4 min; 3,000 descriptions embedded in 43 s |
| Description mode, warm cache | 4-5 min | 1.3-1.6 GB | fetch is nearly all of it; scoring under 10 s |
| Description mode, TF-IDF fallback | 5 min | 1.5 GB | 8,000 descriptions scored in 7 s |
Fetching descriptions is the cost (Greenhouse `?content=true` payloads are about 20 times larger than the plain list), not the model. Embedding every pass-1 survivor without the pre-rank took 10 minutes and 3.9 GB for 24,000 jobs, which is why the pre-rank exists.

Precision: description-only rows are leads, not answers. In two test profiles about 40% of the top description-only rows were clear fits and about 30% more were the right field at a different level or as an individual contributor. Common misses: engineering roles at AI companies for non-engineers (title-mode topic phrases such as "ai platform" hit them too; `careermate-daily-run`'s `engineering_ic_filter` drops them for users whose confirmed titles include no engineering titles), roles at the right company in the wrong function, licensed roles the person does not hold, and postings whose location text is loose. The agent reads them before showing them (see `careermate-job-search`).

## Workday (opt-in only)
Off by default. Add `--include-workday` only when the user's saved preferences say "Include Workday companies: yes" (CareerMate Phase 0 Q4). Never turn it on without that yes. The user must have seen this disclaimer: "This checks public Workday job pages directly. Workday's site terms restrict automated access, so it's offered as an optional, use-at-your-own-discretion feature. It runs slowly, reads job listings only, and never logs in or applies."
- Company list: sibling `workday-companies.md` (100+ sites verified Oct 17 2026: company, tenant, wdN, site, careers URL), or `~/careermate/workday-companies.md` if the user has a personal copy. Grow it with `discover-ats-boards`.
- For each company the script sends each search term as `searchText` to `POST https://<tenant>.wd<N>.myworkdayjobs.com/wday/cxs/<tenant>/<site>/jobs` (limit 20, offset 0), pages further only while the total is above 20 and the last page still had phrase matches (up to `--workday-pages-per-term`, default 3, and `--workday-company-request-cap`, default 40), keeps only titles that pass the same phrase filter, and builds the public URL `https://<tenant>.wd<N>.myworkdayjobs.com/en-US/<site><externalPath>`. Output rows have the same JSON shape with `"ats": "workday"`.
- Pacing is built in and must not be loosened: about 1 request per second overall (`--workday-interval`, minimum 1.0), Retry-After honored, exponential backoff on 429 or 5xx, a company is dropped after 2 consecutive blocked requests, the whole Workday portion stops if more than 20% of companies block, and at most `--workday-max-companies` (default 150) companies. Read-only, descriptive User-Agent, no login.
- Description mode does not add Workday requests. Workday stays title-filtered; when `--workday-details` is on, the description already returned by each detail call is scored too, so Workday rows also get `semantic_score` and `matched_terms`.
- Runtime is about (companies x search terms) seconds: 112 companies x 11 terms with `--workday-details` took about 30 minutes (1,526 requests). Keep it fast by passing a short list of broad `--workday-search` terms (8-12) while keeping the full `--keyword` phrase list for filtering. Run it in the background (Shell `block_until_ms: 0`) and keep working. Board fetching runs alongside it, so adding `--match description` to a Workday run adds little wall time.
- Add `--workday-details` to fetch each match's detail record (pay text, all locations, remote type, start date), capped per company by `--workday-detail-cap-per-company`. Use it for comp and location checks instead of guessing. Workday pay text is whatever the posting states; many postings state none.
- `--workday-stats FILE` writes requests, blocks and runtime. Report the request count and any blocked companies to the user. If the run stopped for blocks, say so and give the user the Google `site:myworkdayjobs.com` Boolean string instead.
  `python3 search_boards.py --boards target-companies.md --keywords-file /tmp/careermate_keywords.txt --include-workday --workday-search "operations manager" --workday-search "data analyst" --workday-details --workday-stats /tmp/careermate_workday_stats.json > /tmp/careermate_matches.json`

Search priority if you must trim: industry-preference matches first, always include AI/ML boards, include HR Tech boards for People/TA backgrounds, prefer boards with 50+ jobs, never fewer than 20. The board list leans toward tech companies; for non-tech backgrounds (clinical, education, trades, public sector) say so and lean on the Boolean strings and `job-board-discovery`.

Cannot search: Google site-search, Workday (unless the user opted in, above), iCIMS, Taleo, SuccessFactors, LinkedIn. That is why the Boolean strings exist (for the user to run in their browser). For LinkedIn, Indeed and Glassdoor discovery through the box browser, use the `job-board-discovery` skill.
