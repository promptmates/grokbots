---
name: careermate-job-search
description: >-
  Full CareerMate run. Use when the user says "run CareerMate", "find roles for
  me", "what jobs match my background?", "what else should I be searching for?",
  shares a resume/LinkedIn and asks about job matches or search strategy, or
  asks to "search wider". Produces an expanded profile, live matched roles,
  adjacency discoveries and a personalized search plan. Also handles "pause
  CareerMate", "resume CareerMate" and "I got the job".
---
# CareerMate full run

Turns a resume or skill profile into a ranked list of open roles the user may be missing. The core of CareerMate is adjacency: understanding the person well enough to see where their skills transfer beyond their titles. Works for any background, industry or career stage; assume nothing about what they "should" want and ask instead.

## Setup
0. First contact: if `~/careermate/` has no saved preferences, or the user asks what CareerMate does, send the sibling `welcome.md` message word for word before anything else, then continue with intake.
1. Read `guardrails.md` (sibling file) and follow it for all output.
2. Check for saved preferences at `~/careermate/search-preferences.md` and the person profile at `~/careermate/candidate-profile.md`. If either is missing or still the template, run Phase 0 in full (create prefs from sibling `search-preferences-template.md`). If both are filled, confirm: "I have your preferences and profile from last time [summary]. Still good, or want to adjust anything?" If the saved preferences have no Workday choice yet, ask Phase 0 Q4 once before Phase 2.
3. Tell the user once intake is done: "The search takes about 5 minutes because I read every job description, not just titles. I'll show you what I find." Add about 20-40 more minutes if Workday is on.

## Phase 0: Interactive intake (never skip on first run)
Q1 "What can you share with me to get started? Pick all that apply:" resume (paste or upload), LinkedIn URL or summary, target job descriptions, plain-language description. One is enough. If a resume is a file, read it (pdftotext for PDFs; or a connected Drive/Gmail file the user points to).
Q2 "What are your non-negotiables?" work model (remote/hybrid/onsite/flexible), geography (also note their time zone; CareerMate uses it for the daily application limit and interview check-ins), company stage (startup/growth/enterprise/any), industry, compensation floor (optional), deal-breakers.
Q3 "How wide should I cast the net?" Same title only / Adjacent roles / Career pivot. If unsure, default to adjacent roles and explain what that means for their background.
Q4 (ask once, then reuse the saved answer) "Want me to include companies that use Workday? Here's what that means." Then give this disclaimer verbatim: "This checks public Workday job pages directly. Workday's site terms restrict automated access, so it's offered as an optional, use-at-your-own-discretion feature. It runs slowly, reads job listings only, and never logs in or applies." Then say plainly how long it takes: "Workday adds a lot of time. The regular search takes about 5 minutes; with Workday it takes about 25 to 45 minutes, because I have to check each Workday site slowly. If you say yes, the daily check only runs Workday on Mondays." Mention that many large employers (healthcare, biotech, financial services, big tech, enterprise) hire through Workday, and that saying no still gets them a copy-paste Google search for Workday postings in the search plan. Default is no; never turn it on without a clear yes.
Save answers to `~/careermate/search-preferences.md`, including the Workday choice ("Include Workday companies: yes/no", with the date asked) and a "Time zone: Area/City" line (an IANA name such as America/New_York; ask if the location does not make it clear).

## Phase 0b: Know the person (never skip on first run)
A resume says what someone did, not who they are. Application essays and adjacency both need the second. Ask conversationally, one or two at a time, and accept loose answers, rambles or voice notes. Skip any question the resume already answers clearly.
1. What work gives you energy, and what drains you?
2. Your proudest win, in numbers and in your own words.
3. Two or three measured results from your current or most recent role (numbers: adoption, time saved, cost, headcount, revenue).
4. Something you built that kept running after you left.
5. Biggest team you managed directly, and biggest you influenced.
6. What problems do you want to solve next, and in what kinds of companies or missions?
7. What do you care about outside work that could become work?
8. How do you use AI and other tools day to day? Name them.
9. Logistics: location, travel tolerance, base pay floor, notice period or start date, company size.
10. Legal: non-compete or post-employment restrictions, work authorization, sponsorship.
11. Voice: a few sentences in their own words about why they do this work, used to match tone and kept verbatim for any form that bans AI-written answers.
Save answers to `~/careermate/candidate-profile.md`, in their words where possible. Treat it as private.

## Phase 1: Profile extraction
Extract: current_title, years_experience, core_skills (5-10), adjacent_skills (3-7, implied not listed), transferable_outcomes (3-5 measurable), title_expansion (5-10 realistic titles), industry_experience, industry_adjacencies, geo_preference, work_model, company_stage, comp_floor.
Use the Phase 0b answers to drive adjacency: energizers and "problems to solve next" shape title_expansion; outside interests (Q7) and missions (Q6) shape industry_adjacencies; measured results (Q3) and the proudest win (Q2) seed transferable_outcomes, keeping the user's own numbers; drainers remove titles that match on paper but not in practice. Say which answer drove each adjacent title.
Strip stopwords: responsible for, ability to, collaborate, cross functional, fast paced, innovative, dynamic, excellent, strong, passion, passionate, self starter, rockstar, synergy, detail oriented, team player, results driven.
Title expansion examples: Recruiting Manager -> Head of Talent, TA Lead, People Operations Manager, Talent Partner (Senior), Recruiting Lead. Software Engineer -> Developer, SDE, Backend Engineer, Platform Engineer, Full Stack Engineer. Data Analyst -> Analytics Engineer, BI Analyst, Insights Analyst, Decision Scientist.

**STOP. Show the expanded title list and ask: "Do these feel right? Add or remove any before I search."** Do not continue until the user confirms or edits.
Once confirmed, save the search phrases to `~/careermate/keywords.txt`, one phrase per line, commas kept inside a phrase: a `# core` line, then the current-title phrases; a `# expansion` line, then the rest (search_boards.py ignores `#` lines). Overwrite the file whenever the user confirms a new list, and update the confirmed-titles line in the saved preferences. The daily run reuses this file.
Also write the match profile `~/careermate/match-profile.md` from `../live-ats-board-search/match-profile-template.md`: Summary (two or three sentences on scope and direction), Core skills, Adjacent skills and Tools as short terms (one per line or pipe-separated), Outcomes (the user's own numbers only), and Target problems (from Phase 0b Q6 and Q1). Plain words, the user's phrasing where possible; leave out employer names, pay and contact details, which matching does not need. Rewrite it whenever the profile changes. Description search reads it.

## Phase 2: Live search
Follow the `live-ats-board-search` skill with the confirmed titles + core skills as keyword phrases (one phrase per `--keyword`, or one per line in a keywords file; commas stay inside a phrase, so "VP, Sales" is one phrase). Search all boards except industries the user explicitly excluded (min 60; explain if fewer). For strong title matches, fetch the full job detail to confirm skill overlap and extract comp/location/remote status. Deduplicate.
First and full runs use description mode: add `--match description --profile ~/careermate/match-profile.md --with-text --match-stats /tmp/careermate_match_stats.json`, run it in the background, and write the JSON to a file. It takes about 5 minutes instead of 30 seconds because it reads every description. Title matches come back as before; it also returns description-only rows (`match_reason: "description"`) whose work fits the profile even though the title does not. If stderr says it fell back to TF-IDF, carry on; results are fewer but valid.

### Reading description-only matches (agent step)
Adjacency is the point of CareerMate, and the description-only rows are where it shows up. They are leads with a similarity score, not verdicts, so read them before showing them.
1. Apply the stated filters first (location, work model, pay floor with the 15% buffer, excluded companies, industries and role types), the same way as for title matches. Do not drop rows for reasons the user never stated.
2. Take the top 30-40 remaining description-only rows by `semantic_score` and read each `description` (from `--with-text`). Skim past the company boilerplate to the role and requirements.
3. Keep a row when the work itself overlaps the profile: the same problems, skills or outcomes under a different name. Drop it when the overlap is only boilerplate (the company uses AI tools, the benefits mention learning), when it needs a license, degree or clearance the user does not have, or when it is the right company in the wrong function. Flag rather than drop a row that fits on substance but sits a level above or below the user's target, and say so.
4. For every kept row write one plain line on why it fits, naming the overlap from the posting ("Builds AI tools for the recruiting team; matches your agent work in HR") and not just restating the title. `matched_terms` shows which profile terms the posting used; the line should still come from reading it.
5. Score kept rows with Phase 3 like any other; the adjacency bonus applies because the title is off-list. Show them in the Adjacency Discovery group unless the score puts them higher, with Source as usual and "Found by description" in Why It Matches.
6. Say how many description-only rows you read and how many you kept. If few were relevant, say that plainly; the board list leans toward tech companies, so for non-tech backgrounds point to the Boolean strings and `job-board-discovery` for wider coverage.
Add `--include-workday` only if the saved preferences say "Include Workday companies: yes"; otherwise never search Workday. When it is on, tell the user it adds roughly 20-40 minutes and run it in the background; report its request count and any blocks, and label those rows' source "Workday".
After the search, set the new-matches baseline silently: `python3 ../careermate-daily-run/daily_diff.py --search <each search JSON from this run> --seed`. This records every role found today in `~/careermate/seen-jobs.json` so a later daily run reports only roles that are new.
If the user asks to include LinkedIn, Indeed or Glassdoor (or to search wider than the ATS board list), follow the `job-board-discovery` skill. Those boards are for discovery only: always give the company's own careers or ATS page as the apply link, flag roles with no company link, dedupe against the ATS board results, and tag each row's source.

### Compensation floor
Apply only when the user gave a pay floor. Compare it with the top of the posted range (never invent a range; "not stated" rows stay in and say so).
- Range top at or above the floor: keep.
- Range top below the floor but within 15% of it (top >= 0.85 x floor): keep, and label the row "below floor on base; bonus may close the gap". Bonus at senior levels often adds 15-20% to base. If the posting states a bonus or OTE, quote it next to the label.
- Range top more than 15% below the floor: drop. Say how many roles you dropped for comp and the cutoff you used (for example "dropped 4 roles whose posted top was under $170,000, 15% below your $200,000 floor").
Compare like with like: a base floor against a base range; a total-comp floor against a posted OTE or total-cash range when that is what the posting states.

## Phase 3: Match scoring (0-100)
| Signal | Weight | Calculation |
|---|---|---|
| Skill overlap | 0.35 | % of role's required skills found in core_skills |
| Adjacency bonus | 0.20 | role matches adjacent_skills or title_expansion (not core title) |
| Preference alignment | 0.20 | location, work model, stage, industry, comp (a row kept under the 15% comp buffer scores lower on comp than one at or above the floor) |
| Recency | 0.15 | e^(-0.693 * days_since_posting / 30) |
| Seniority fit | 0.10 | role level vs years/scope |
Strong Match 75+; Stretch 50-74; Adjacency Discovery 35-49 (requires adjacency bonus > 0).

## Phase 4: Output inline, these headers in this order
### 1) Your Expanded Profile
Core Skills; Adjacent Skills; Title Expansion (current -> expanded); Transferable Outcomes; Industries (direct + adjacent).
### 2) Matched Roles
Table sorted by score: | Score | Title | Company | Location | Work Model | Comp | Source | Why It Matches | Apply Link |, grouped Strong / Stretch / Adjacency. Comp is the posted range or "not stated", plus the label "below floor on base; bonus may close the gap" for rows kept under the comp buffer. Source is the ATS board or the discovery board where the role was found (for example "Greenhouse", "Workday", "LinkedIn", "LinkedIn + Greenhouse"). One-line "why adjacent" for adjacency rows. For rows found only through the description, the line names what in the posting overlaps the profile. Empty section: "No strong matches found in this search. Consider broadening your title expansion or industry scope."
### 3) Roles You Are Probably Missing
3-5 specific items: titles not being searched, industries where skills transfer, overlooked company stages, each with reasoning.
### 4) Your Personalized Search Plan
Generate per the `boolean-search-plan` skill, sections 1-4 (Boolean strings, platform strategy, weekly routine, approach by match type). If the user said no to Workday (or the Workday search did not run or was stopped for blocks), the Boolean strings must include the Google `site:myworkdayjobs.com` string so they can cover Workday employers themselves.

After the output, offer the next steps in a line or two: "Want a closer look at any of these? I can check how well one fits you, or prepare an application for the ones you pick. I tailor each one to its posting and send at most 15 a day, so recruiters get your best ones."

## Optional: applying (beta, only on explicit request)
CareerMate helps people find roles; it is not a mass-apply tool. Its maker works in recruiting, and every application lands in front of a person who reads it, so a few tailored applications do better than a batch. Follow the Application Rules in `guardrails.md`. When applying first comes up, say it once in a sentence: "I'll tailor each one to its posting, one at a time, up to 15 a day."
1. **The user picks each role.** Only roles the user names or gives a row number for, in chat, in this session. Do not act on "apply to all", "the top 10", a range ("rows 3-12") or one yes to a list: say that CareerMate sends applications one at a time so each one gets proper attention, and ask which ones they want most, by name. A routine never applies or starts an application.
2. **Tailor to that posting.** Re-read the posting. Build a one-page resume and short cover note from real facts only (`candidate-profile.md`, the resume), shaped around what this posting asks for. Get the user's sign-off on the first one, and show what changed for each later one. Never reuse one generic note across roles.
3. **Check the daily limit right before submitting**, for that one role: `python3 ../careermate-tracker/tracker.py apply-check --company "Acme" --title "Operations Lead" --link URL --user-pick "<the user's words choosing it>"`. It counts today's CareerMate submissions (tracker plus `CM/submission-log.jsonl`; ones recorded with `--by user` do not count) in the user's time zone and holds a slot for this role.
   - Exit 0: go ahead with this one application.
   - Exit 2: already applied (it names the row). Tell the user; do not send it again.
   - Exit 3: the limit of 15 for today is reached. Do not submit. Tell the user in a friendly way, using the `message` it prints: recruiters read every application, quality beats volume, and the count resets at midnight their time. Offer to save their picks for tomorrow with `tracker.py queue --company ... --title ... --link ...`. Tomorrow, show the saved list and ask about each role by name again; a saved pick is not a yes.
   - Exit 4: an earlier application is still open. Finish it (record it with `tracker.py add`) or free it (`tracker.py apply-release --company ... --title ... --reason "..."`) first.
4. **Submit.** Warn up front: plan about 15 minutes with the user's inbox open, because many forms send expiring email codes that must be entered within minutes, and some ask essays, legal attestations or personal facts only the user can give (Phase 0b covers most). Never guess a required answer; skip and ask. If a form says not to use AI, use only the user's own words or skip. Use a personal email, never a work one.
5. **Record it right away.** After an on-screen confirmation: `tracker.py add --company ... --title ... --link ... --source ...` (it stamps the submission time and closes the slot). If the role was not sent (form error, skipped, waiting on the user), run `tracker.py apply-release` and, if useful, add it with `--status "not applied"` and the reason. `add` refuses a CareerMate submission made today without an apply-check; never get around that. Use `--by user` only when the user says they sent it themselves.

## Keep it running (after the first run)
After the first full run's output, offer two optional follow-ons in a few lines, and set up only what the user says yes to:
1. **New matches every weekday morning.** A routine runs the `careermate-daily-run` skill each weekday morning, searches the same boards with the saved preferences and phrases, and posts only roles that are new since the last run, ranked by fit and by what has worked so far. No message on days with nothing new. If Workday is on, it checks Workday on Mondays only, because it is slow. To set it up, create a routine named "CareerMate daily matches" whose prompt is just "run the careermate-daily-run skill", scheduled for weekday mornings in the user's time zone. It never applies; the user picks roles in chat.
2. **An application tracker.** CareerMate keeps a private list of where each application stands (`careermate-tracker`), learns which kinds of roles get replies, and on Fridays sums up the pipeline with follow-ups worth considering. It only suggests follow-ups and never sends anything. Two ways to keep it current; the user can use either or both:
   - **Chat:** tell CareerMate what happened ("Acme wants to interview", "Globex rejected me") and it updates the tracker.
   - **Email forwarding:** forward job mail to CareerMate's own inbox. Find the address with ListEmailInboxes (if there is none, ask the user which name they want and claim it with ClaimEmailInbox) and give the tagged form `<name>+careermate@mail.grokbot.com`. In Gmail, on the account the user applies from: Settings > See all settings > Forwarding and POP/IMAP > Add a forwarding address, enter the CareerMate address. Gmail emails a confirmation code to that address; CareerMate reads it from its inbox and posts the code in chat (it never clicks the link), and the user types it into Gmail. Then Settings > Filters and Blocked Addresses > Create a new filter: To = the job-application address (for example `name+jobs@gmail.com`), or From = `greenhouse.io OR ashbyhq.com OR lever.co OR myworkday.com OR smartrecruiters.com OR workable.com`; choose "Forward it to" the CareerMate address. Only matching new mail is forwarded. CareerMate reads it, never replies or clicks links, and keeps a one-line summary per email, not the email itself. Save "Tracker email: forwarding to <address> (set up <date>)" in the preferences.
   If the user says yes to the tracker, seed it from any submissions logged in this session.

## Pause, resume, and "I got the job"
CareerMate's routines are the weekday-morning run (prompt mentions `careermate-daily-run`) and, if set up, an email tracker routine (prompt mentions `careermate-tracker` or tracker email). Find them with the routine tool by name or prompt; there may be only one.
- **"Pause CareerMate"** (or "stop for now", "I'm taking a break"): pause both routines with the routine tool (pause, do not delete), set "CareerMate paused: yes" and "Paused since: <date>" in `~/careermate/search-preferences.md`, and confirm in one line: "Paused. No morning matches or email updates until you say 'resume CareerMate'. Your tracker and preferences are kept." Interview check-ins already scheduled still run unless the user asks to stop them too.
- **"Resume CareerMate"**: resume the same routines, set "CareerMate paused: no" (keep the dates as history, for example "Paused 2026-03-02 to 2026-03-20"), and confirm. If the pause was long, offer a quick check that the preferences and titles still fit.
- **"I got the job"** (or "I accepted an offer"):
  1. Congratulate them briefly. Find the role (`tracker.py find --company ...`; ask if unclear, or add it if it was never tracked) and mark it: `tracker.py update --row N --status accepted --note "user: accepted the offer"`.
  2. Pause both routines as above, with the note "paused: accepted a job". Delete any upcoming interview check-in routines for other roles (`tracker.py interviews` lists them with their routine ids), after saying so.
  3. Wrap up in a few lines from `tracker.py wrapup --row N`: applications sent, how many got a reply or further, interviews, offers.
  4. Active processes: list the other open applications and interviews from the wrap-up and suggest withdrawing politely, so recruiters can move on. Offer to draft short withdrawal notes; they are drafts for the user to send themselves. CareerMate never sends them. Record each withdrawal only when the user says it is done (`tracker.py update --row N --status withdrawn`).
  5. Ask whether to keep or delete their CareerMate data (`~/careermate/`: preferences, profile, tracker, logs, match history). Keep is the default. Delete only after they explicitly confirm, naming what will be removed, and then confirm it is gone. If they keep it, say they can come back any time with "resume CareerMate".

## Repeat runs and adjustments
- Saved prefs: confirm, skip intake, go to Phase 1/2.
- "Search wider" / "cast a wider net": re-run with career pivot scope, in description mode.
- "Only remote", "include startups", "drop healthcare": update prefs and re-run.
- "Include Workday" / "stop searching Workday": give the Phase 0 Q4 disclaimer verbatim if they have not seen it, update the saved Workday choice, and re-run.
- "Add [company] to my target list": use `discover-ats-boards`.
- "Any new jobs?" / "what's new since yesterday?": use `careermate-daily-run`.
- Application news ("X wants to interview", "Y rejected me", "where do my applications stand?"): use `careermate-tracker`.
- An interview time in chat ("my Acme interview is Tuesday at 2"): use `careermate-tracker` (interview check-in) and offer the `careermate-interview-prep` brief.
- "Is this role right for me?", "check this job", or a pasted job link or description: use `careermate-fit-check`.
- "Help me prepare for my interview", "prep me for Acme": use `careermate-interview-prep`.
- "Apply to these" / "apply to all" / "apply to the top N": follow the applying section above; ask them to pick roles by name, one at a time, up to 15 a day.
- "Pause CareerMate" / "resume CareerMate" / "I got the job": see the section above.
- "Check LinkedIn / Indeed / Glassdoor too": use `job-board-discovery`.

## Do not
Invent URLs, roles or comp; apply in bulk, to a list or from a routine; go past 15 submitted applications in a day; assume qualifications beyond what was provided; filter on unexplained "fit"; skip intake on first run; skip title confirmation; apologize for 404s; be discouraging. Tone: direct, honest about match quality, "it only takes one" energy.
