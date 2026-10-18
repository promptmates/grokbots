---
name: careermate-interview-prep
description: >-
  CareerMate interview prep brief. Use when the user asks "help me prepare for
  my interview", "prep me for Acme", "what should I expect in this interview?",
  or says yes when CareerMate offers a brief after an interview is scheduled.
  Builds a one-page brief from the real job posting, company basics and recent
  news with real links, what the posting stresses, likely questions mapped to
  the person's own stories, gaps to prepare for and good questions to ask.
---
# CareerMate interview prep brief

Read `../careermate-job-search/guardrails.md` and follow it, especially the Research Rules. Data in `~/careermate/` (below, `CM`). Posting reader: `../careermate-fit-check/fetch_posting.py`.

## 1. Gather what is real
- **The role.** Find it in the tracker (`python3 ../careermate-tracker/tracker.py find --company X --title T`) for the link, stage and interview time (`tracker.py interview --row N` shows it). Re-fetch the posting from its real URL: `python3 ../careermate-fit-check/fetch_posting.py --url "<link>"`. If it has closed or cannot be read, say so and ask the user for the job description (they may have it in an email or a saved copy); never rebuild a posting from memory. Workday links follow the same opt-in rule as the fit check.
- **The interview.** Ask what they know if it is not in the tracker: the round (recruiter screen, hiring manager, panel, case), who they meet (roles are enough), length, and the format. Do not ask for names; if they share them, use them only in this brief and do not store them.
- **The person.** `CM/candidate-profile.md` (their stories, numbers and words) and the resume they shared. If neither exists, ask for a resume or a few stories before writing the brief.
- **The company.** Use web search for the company's own site (about page, product, recent announcements) and recent news from the last 6-12 months: funding, launches, leadership changes, layoffs, acquisitions. Open the pages you cite. Cite only links you actually retrieved, next to the fact they support. Prefer the company's own pages and established news outlets over aggregators. If news is thin or you find none, say "I found little recent news about Acme" and move on; do not pad it.

## 2. Write the brief (one page)
Plain language, scannable, no hype. These sections, in order:
1. **The interview:** company, role, round and time in the user's time zone, if known.
2. **Company basics:** what they do, for whom, rough size or stage only when a source states it, with links. 2-4 lines.
3. **Recent news:** 2-4 dated items, each with its link and one line on why it might come up. Or the honest line that there is little.
4. **What the posting stresses:** the 3-5 things it asks for most (repeated, listed first, or called must-have), quoted briefly.
5. **Likely questions and your stories:** 6-8 likely questions for this round, each mapped to a specific story from their profile or resume, with the one detail or number (their own) worth leading with. If no story fits a question, say so; that question goes under gaps.
6. **Gaps to prepare for:** requirements the profile does not clearly cover, each with an honest way to answer (a related experience, how they would learn it, or a direct acknowledgment). Include any pay, location or level mismatch they may get asked about.
7. **Questions to ask them:** 4-6 specific questions drawn from the posting and the news (team, success in the first 90 days, how the role is measured, something from the news), not generic ones.
8. **Logistics:** anything they should have ready (examples, a portfolio, a work sample) based on the round.

Keep their voice in the story prompts (from Phase 0b of `careermate-job-search`). Never invent a story, a number or a company fact. If the brief would run past one page, cut questions before cutting gaps.

## 3. After the brief
- Offer to save it as a file in `CM/prep/<company>-<date>.md` (private), and to run a short mock round with a few of the likely questions.
- If there is no check-in yet for this interview and the time is known, offer to set one up (`careermate-tracker`, "Interview check-ins").
- Never contact the company or the interviewers, and never send anything on the user's behalf.

## Do not
Invent news, links, interviewer details, pay or company facts; cite a page you did not open; store other people's names; reuse a generic question list without tying it to this posting.
