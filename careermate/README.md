# CareerMate

CareerMate from PromptMates is a free job-search discovery assistant. It reads your background, expands it into skills, alternate titles, and adjacent industries, then searches live public job boards (Greenhouse, Ashby, Lever, Workable, SmartRecruiters, and optional Workday). It surfaces roles you qualify for but are not already searching.

It is a discovery tool, not a mass-apply tool. Optional applying is capped at 15 per day, and each role is chosen individually. Routines never apply.

This folder is the Grok Bot agent version. The Claude skills version lives at https://github.com/promptmates/promptmates-toolkit/tree/main/careermate.

## Install

Add the CareerMate bot from the Grok Bot marketplace. On first run it reads `manifest.txt` and downloads each listed file from:

https://raw.githubusercontent.com/promptmates/grokbots/main/careermate/

Updates ship by pushing to this repo. The next run picks them up from those same raw URLs.

## Privacy

Your resume, preferences, and tracker data stay on your own bot. They are never in this repo.

Built by PromptMates (promptmates.ai)
