#!/usr/bin/env python3
"""CareerMate daily new-matches diff. Stdlib only.

Takes one or more search_boards.py JSON outputs plus the seen-jobs ledger and returns only roles that are NEW:
not in the ledger, not a repost of a role seen in the last 30 days, and not already in the application tracker.
New roles then get the same filters as the full run (title/company/industry exclusions, location, pay floor with
the 15% buffer), the Phase 3 score, and the tracker's learned adjustments (re-rank only, never drop).

  python3 daily_diff.py --search /tmp/cm_ats.json [--search /tmp/cm_workday.json] [--searched-sources ats,workday]
  python3 daily_diff.py --search /tmp/cm_ats.json --seed          # baseline: mark everything seen, report nothing

Stdout: a markdown digest when there are new matches, and NOTHING when there are none (the run stays silent).
Stderr: one summary line. --json-out writes the new rows; the ledger is updated in place (or --ledger-out).

Files (default ~/careermate, override with --home): seen-jobs.json (ledger), daily-config.json (filters and scoring
inputs derived from search-preferences.md), keywords.txt, applications-tracker.md, learned-weights.json.
"""
import argparse, datetime as dt, hashlib, html, importlib.util, json, math, os, re, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
UA = "CareerMate/1.1 (read-only public job listing search)"

def load_tracker_module():
    """Shared helpers (job_key, features, adjustment, norm) live in the careermate-tracker skill."""
    import glob
    cands = sorted(glob.glob(os.path.join(HERE, "..", "careermate-tracker*", "tracker.py"))) + [os.path.join(HERE, "tracker.py")]
    for p in cands:
        if os.path.exists(p):
            spec = importlib.util.spec_from_file_location("cm_tracker", p)
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            return m
    sys.exit("daily_diff.py needs careermate-tracker*/tracker.py next to this skill")

T = load_tracker_module()

DEFAULT_CONFIG = {
    "prefs_sha": "",                 # sha256 of search-preferences.md when this config was derived
    "pay_floor": None,               # base pay floor in USD/year, or null for no comp filter
    "pay_buffer": 0.15,              # keep rows whose posted top is within 15% below the floor (labeled)
    "location_allow": [],            # regexes; a location part must match one (empty list = no location filter)
    "location_block": [],            # regexes; a location part matching one fails (e.g. non-US remote)
    "exclude_title_patterns": [],    # regexes for titles the user ruled out
    "require_title_patterns": [],    # optional regexes, e.g. seniority words, only if the user stated a level
    "exclude_companies": [],         # exact company names the user ruled out
    "exclude_sections": [],          # industry headings from the board lists the user excluded
    "seniority_patterns": [],        # regexes for the user's target level, used for the seniority-fit score only
    "skills": [],                    # core skill phrases, used for skill overlap against the job description
    "company_sizes": {},             # optional {"Company": "1k-10k"} for size signals
    "max_rows": 15,
    "workday": {"opt_in": False, "day": "Monday", "search_terms": []},
    # Weekly description-matching pass (search_boards.py --match description); needs ~/careermate/match-profile.md.
    "description_match": {"enabled": False, "day": "Monday", "max_description_only": 60},
}

def norm(s):
    return T.norm(s)

def today_of(a):
    """--today, else today's date in the user's time zone, resolved like tracker.py: --tz, then $CAREERMATE_TZ,
    then the "Time zone:" line in search-preferences.md, then the system zone."""
    if a.today:
        return dt.date.fromisoformat(a.today)
    return dt.datetime.now(T.user_tz(a)).date()

# ---------------------------------------------------------------- inputs

def load_json(path, default):
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default

def row_key(j):
    return T.job_key(j.get("url", ""), j.get("platform") or j.get("ats") or "", j.get("job_id"),
                     j.get("tenant", ""), j.get("job_req_id"))

def ct_key(j):
    return T.norm_company(j.get("company")) + "|" + norm(j.get("title"))

def board_sections(paths):
    """token -> section heading, from target-companies.md files (industry signal and section exclusions)."""
    out = {}
    for p in paths:
        if not p or not os.path.exists(p):
            continue
        section = ""
        for line in open(p, encoding="utf-8"):
            if line.startswith("### "):
                section = line[4:].strip()
            elif line.startswith("| ") and section:
                c = [x.strip() for x in line.strip().strip("|").split("|")]
                if len(c) >= 2 and re.fullmatch(r"[a-z0-9_\-]+", c[1]):
                    out.setdefault(c[1], section)
    return out

# ---------------------------------------------------------------- details (new rows only)

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8", "replace"))

def strip_html(h):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(html.unescape(h or ""))))

PAYRX = re.compile(r"([$£€])\s?(\d[\d,]*(?:\.\d+)?)\s?([kK])?(?:\s*(?:-|–|—|to)\s*[$£€]?\s?(\d[\d,]*(?:\.\d+)?)\s?([kK])?)?")

def pay_from_text(texts):
    """(top USD/year or None, display text, note). Ignores hourly figures and non-USD currencies."""
    tops, shown, nonusd = [], [], False
    for t in texts or []:
        for m in PAYRX.finditer(t or ""):
            tail = (t or "")[m.end(): m.end() + 20].lower()
            if re.search(r"hour|/hr|per hr|/h\b", tail):
                continue
            vals = []
            for num, k in ((m.group(2), m.group(3)), (m.group(4), m.group(5))):
                if num:
                    v = float(num.replace(",", ""))
                    vals.append(v * 1000 if k else v)
            vals = [v for v in vals if v >= 20000]
            if not vals:
                continue
            if m.group(1) != "$":
                nonusd = True
                continue
            tops.append(max(vals))
            shown.append(m.group(0).strip())
    if tops:
        return max(tops), shown[0], ""
    return None, "", "non-USD pay" if nonusd else ""

def fmt_money(v):
    return f"${v/1000:,.0f}K" if v else ""

ASHBY_CACHE = {}
def fetch_detail(j):
    """Adds pay_top, pay_text, location detail, remote, posted date and description text where the ATS exposes them."""
    p, tok, u = j.get("platform") or j.get("ats"), j.get("token", ""), j.get("url", "")
    d = {}
    try:
        if p == "greenhouse" and j.get("job_id"):
            x = get(f"https://boards-api.greenhouse.io/v1/boards/{tok}/jobs/{j['job_id']}?pay_transparency=true")
            text = strip_html(x.get("content", ""))
            ranges = [r for r in x.get("pay_input_ranges") or [] if (r.get("currency_type") or "USD") == "USD"]
            if ranges:
                top = max((r.get("max_cents") or 0) for r in ranges) / 100
                lo = min((r.get("min_cents") or 0) for r in ranges) / 100
                d.update(pay_top=top, pay_text=f"{fmt_money(lo)}-{fmt_money(top)}" + (" (by zone)" if len(ranges) > 1 else ""))
            else:
                top, shown, note = pay_from_text([text])
                d.update(pay_top=top, pay_text=shown or note)
            d.update(location=(x.get("location") or {}).get("name") or j.get("location"), posted=x.get("first_published"),
                     text=text)
        elif p == "ashby":
            if tok not in ASHBY_CACHE:
                ASHBY_CACHE[tok] = {y.get("jobUrl"): y for y in
                                    get(f"https://api.ashbyhq.com/posting-api/job-board/{tok}?includeCompensation=true").get("jobs", [])}
            x = ASHBY_CACHE[tok].get(u) or {}
            comp = x.get("compensation") or {}
            sal = [c for c in comp.get("summaryComponents") or [] if c.get("compensationType") == "Salary"
                   and (c.get("currencyCode") or "USD") == "USD" and c.get("maxValue") and "YEAR" in (c.get("interval") or "YEAR")]
            if sal:
                d.update(pay_top=max(c["maxValue"] for c in sal), pay_text=comp.get("scrapeableCompensationSalarySummary")
                         or comp.get("compensationTierSummary"))
            elif comp.get("compensationTierSummary"):
                top, shown, note = pay_from_text([comp["compensationTierSummary"]])
                d.update(pay_top=top, pay_text=shown or note)
            wp = x.get("workplaceType")
            locs = [x.get("location") or j.get("location", "")] + [s.get("location", "") for s in x.get("secondaryLocations") or []]
            d.update(location="; ".join(l for l in locs if l), workplace=wp,
                     remote=(wp == "Remote") if wp else x.get("isRemote"), posted=x.get("publishedAt"),
                     text=x.get("descriptionPlain", ""))
        elif p == "lever":
            x = get(f"https://api.lever.co/v0/postings/{tok}/{u.rstrip('/').split('/')[-1]}?mode=json")
            sr = x.get("salaryRange") or {}
            if sr.get("max") and (sr.get("currency") or "USD") == "USD" and "year" in (sr.get("interval") or "per-year-salary"):
                d.update(pay_top=float(sr["max"]), pay_text=f"{fmt_money(sr.get('min'))}-{fmt_money(sr['max'])}")
            text = (x.get("descriptionPlain") or "") + " " + " ".join(strip_html(l.get("content", "")) for l in x.get("lists") or [])
            text += " " + (x.get("additionalPlain") or "")
            if not d.get("pay_top"):
                top, shown, note = pay_from_text([text])
                d.update(pay_top=top, pay_text=shown or note)
            wp = x.get("workplaceType")
            d.update(location=(x.get("categories") or {}).get("location") or j.get("location"), workplace=wp,
                     remote=(wp == "remote") if wp else None, posted=x.get("createdAt"), text=text)
        elif p == "smartrecruiters":
            x = get(f"https://api.smartrecruiters.com/v1/companies/{tok}/postings/{u.rstrip('/').split('/')[-1]}")
            text = " ".join(strip_html(v.get("text", "")) for v in ((x.get("jobAd") or {}).get("sections") or {}).values())
            top, shown, note = pay_from_text([text])
            d.update(pay_top=top, pay_text=shown or note, posted=x.get("releasedDate"), text=text)
        elif p == "workday":
            top, shown, note = pay_from_text(j.get("pay_text") or [])
            d.update(pay_top=top, pay_text=shown or note,
                     location="; ".join([j.get("location") or ""] + list(j.get("additional_locations") or [])).strip("; "),
                     remote=bool(re.search(r"remote", j.get("remote_type") or "", re.I)) or None,
                     posted=j.get("start_date") or j.get("posted_on"))
        d["details"] = "ok"
    except Exception as e:
        d["details"] = f"unavailable ({type(e).__name__})"
    return {k: v for k, v in d.items() if v not in (None, "")}

# ---------------------------------------------------------------- filters and score

def loc_parts(j):
    loc = j.get("location") or ""
    parts = [x.strip() for x in re.split(r";|\||\bor\b|\n", loc) if x.strip()]
    if j.get("remote") is True and not any(re.search(r"remote", x, re.I) for x in parts):
        parts.append("Remote " + (parts[0] if parts else ""))
    return parts

def location_ok(j, cfg):
    """(True|False|None, where). None = location not stated."""
    allow, block = cfg.get("location_allow") or [], cfg.get("location_block") or []
    parts = loc_parts(j)
    if not allow and not block:
        return True, ""
    if not parts:
        return None, "location not stated"
    for part in parts:
        if (not allow or any(re.search(r, part, re.I) for r in allow)) and not any(re.search(r, part, re.I) for r in block):
            return True, part
    return False, ""

def title_filter(j, cfg, sections):
    t = j.get("title", "")
    if any(norm(c) == norm(j.get("company")) for c in cfg.get("exclude_companies") or []):
        return "company"
    sec = j.get("section") or sections.get(j.get("token", ""), "")
    if any(e.lower() in sec.lower() for e in cfg.get("exclude_sections") or [] if e):
        return "industry"
    if any(re.search(r, t, re.I) for r in cfg.get("exclude_title_patterns") or []):
        return "title"
    req = cfg.get("require_title_patterns") or []
    if req and not any(re.search(r, t, re.I) for r in req):
        return "title"
    return ""

def pay_check(j, cfg):
    """('keep'|'buffer'|'drop', label)."""
    floor, top = cfg.get("pay_floor"), j.get("pay_top")
    if not floor:
        return "keep", ""
    if not top:
        return "keep", "not stated"
    if top >= floor:
        return "keep", ""
    if top >= (1 - cfg.get("pay_buffer", 0.15)) * floor:
        return "buffer", "below floor on base; bonus may close the gap"
    return "drop", ""

def days_since(posted, now):
    if posted is None or posted == "":
        return None
    if isinstance(posted, (int, float)):
        return max(0, (now - dt.datetime.fromtimestamp(posted / 1000).date()).days)
    s = str(posted)
    m = re.search(r"posted\s+(today|yesterday|(\d+)\+?\s+days?\s+ago)", s, re.I)
    if m:
        return 0 if m.group(1).lower() == "today" else 1 if m.group(1).lower() == "yesterday" else int(m.group(2))
    try:
        return max(0, (now - dt.date.fromisoformat(s[:10])).days)
    except ValueError:
        return None

def score(j, cfg, tiers, phrases, weights, now):
    n = norm(j.get("title"))
    matched = [raw for raw, rx in phrases if rx.search(n)]
    core = {norm(p) for p, t in tiers if t == "core"}
    desc_only = j.get("match_reason") == "description"
    adj = 1.0 if desc_only or any(norm(p) not in core for p in matched) else 0.0
    text = (j.get("text") or "").lower()
    skills = cfg.get("skills") or []
    if text and skills:
        hits = [s for s in skills if re.search(r"(?<![a-z0-9])" + re.escape(s.lower()) + r"(?![a-z0-9])", text)]
        skill = min(1.0, len(hits) / max(1, min(len(skills), 5)))
    elif j.get("matched_terms"):   # description mode: profile terms found in the posting by search_boards.py
        hits = list(j["matched_terms"]); skill = min(1.0, len(hits) / 5)
    else:
        hits, skill = [], 0.5
    lo = j.get("_loc_ok")
    loc_s = 1.0 if lo is True else 0.7
    comp_s = {"keep": 1.0 if j.get("pay_top") or not cfg.get("pay_floor") else 0.8, "buffer": 0.6}[j["_pay"]]
    pref = (loc_s + comp_s) / 2
    d = days_since(j.get("posted") or j.get("published_at") or j.get("posted_on") or j.get("created_at"), now)
    rec = math.exp(-0.693 * d / 30) if d is not None else 0.5
    sen_p = cfg.get("seniority_patterns") or []
    sen = (1.0 if any(re.search(r, j.get("title", ""), re.I) for r in sen_p) else 0.6) if sen_p else 0.8
    base = round(100 * (0.35 * skill + 0.20 * adj + 0.20 * pref + 0.15 * rec + 0.10 * sen))
    feats = T.features(j.get("title"), j.get("company"), j.get("platform") or j.get("ats"), j.get("_industry", ""),
                       (cfg.get("company_sizes") or {}).get(j.get("company", ""), ""), phrases)
    pts, reasons = T.adjustment(feats, weights)
    final = max(0, min(100, base + pts))
    if desc_only:   # unread description-only matches top out at Stretch until the agent reads the posting
        final = min(final, 74)
    j.update(_base=base, _learned=pts, _reasons=reasons, _score=final, _days=d,
             _skills_hit=hits, _matched=matched)
    return j

def band(s):
    return "Strong" if s >= 75 else "Stretch" if s >= 50 else "Adjacency" if s >= 35 else "Low"

SOURCE = {"greenhouse": "Greenhouse", "ashby": "Ashby", "lever": "Lever", "workday": "Workday",
          "workable": "Workable", "smartrecruiters": "SmartRecruiters"}

def digest(new, dropped, cfg, now, extra_note, more_path):
    L = [f"**CareerMate: {len(new)} new {'match' if len(new) == 1 else 'matches'}** ({now.strftime('%a %b %-d')})", "",
         "| Score | Title | Company | Location | Pay | Source | Link |", "|---|---|---|---|---|---|---|"]
    shown = new[: cfg.get("max_rows", 15)]
    for j in shown:
        pay = j.get("pay_text") or "not stated"
        if j["_pay"] == "buffer":
            pay += "; below floor on base; bonus may close the gap"
        loc = j.get("location") or "not stated"
        if j.get("workplace"):
            loc += f" ({j['workplace']})"
        L.append(f"| {j['_score']} {band(j['_score'])} | {T.cell(j['title'])} | {T.cell(j['company'])} | {T.cell(loc)} | "
                 f"{T.cell(pay)} | {SOURCE.get(j.get('platform') or j.get('ats'), j.get('platform', ''))} | {j['url']} |")
    notes = []
    for j in shown:
        if j["_reasons"]:
            net = f"{'+' if j['_learned'] > 0 else ''}{j['_learned']}"
            notes.append(f"- {j['company']}, {j['title']}: learned adjustment {net} ({'; '.join(j['_reasons'])}).")
        if j.get("match_reason") == "description":
            terms = ", ".join((j.get("matched_terms") or [])[:5])
            notes.append(f"- {j['company']}, {j['title']}: found by its description, not its title"
                         f"{' (mentions ' + terms + ')' if terms else ''}.")
        if j.get("_loc_ok") is None:
            notes.append(f"- {j['company']}, {j['title']}: location not stated on the posting; check before applying.")
        if str(j.get("details", "ok")) != "ok":
            notes.append(f"- {j['company']}, {j['title']}: posting details {j['details']}; pay and location not checked.")
    if notes:
        L += ["", "Notes:"] + notes
    if len(new) > len(shown):
        L += ["", f"{len(new) - len(shown)} more new roles scored lower; they are saved in {more_path}. Ask to see them."]
    drops = []
    if dropped.get("pay"):
        floor = cfg["pay_floor"]
        cut = (1 - cfg.get("pay_buffer", 0.15)) * floor
        drops.append(f"{dropped['pay']} below the pay cutoff (posted top under {fmt_money(cut)}, 15% below your {fmt_money(floor)} floor)")
    for k, label in (("location", "outside your locations"), ("title", "titles you ruled out"),
                     ("industry", "excluded industries"), ("company", "excluded companies")):
        if dropped.get(k):
            drops.append(f"{dropped[k]} {label}")
    if drops:
        L += ["", "Also new but filtered out: " + "; ".join(drops) + "."]
    if extra_note:
        L += ["", extra_note]
    return "\n".join(L)

# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--search", action="append", required=True, help="search_boards.py JSON output, repeatable")
    ap.add_argument("--home", default=os.path.expanduser("~/careermate"))
    ap.add_argument("--ledger"); ap.add_argument("--ledger-out", help="write the updated ledger here (default: --ledger)")
    ap.add_argument("--config"); ap.add_argument("--keywords"); ap.add_argument("--tracker"); ap.add_argument("--weights")
    ap.add_argument("--boards", action="append", default=[], help="target-companies.md for industry sections (default: user copy, else sibling skill)")
    ap.add_argument("--seed", action="store_true", help="mark every role seen without reporting (baseline after a full run)")
    ap.add_argument("--no-details", action="store_true", help="skip posting-detail fetches (offline tests)")
    ap.add_argument("--dry-run", action="store_true", help="do not write the ledger")
    ap.add_argument("--json-out", help="write new rows (scored) to this file")
    ap.add_argument("--digest-out", help="also write the digest markdown here")
    ap.add_argument("--repost-days", type=int, default=30, help="same company+title seen within N days counts as a repost, not new")
    ap.add_argument("--prune-days", type=int, default=120, help="forget ledger entries not seen for N days")
    ap.add_argument("--note", default="", help="extra line for the digest (e.g. Workday status)")
    ap.add_argument("--today", help="YYYY-MM-DD (default: today in the user's time zone)")
    ap.add_argument("--tz", help="user's IANA time zone, e.g. America/New_York (default: $CAREERMATE_TZ, then the "
                                 "'Time zone:' line in search-preferences.md, then the system zone)")
    a = ap.parse_args()
    H = a.home
    a.ledger = a.ledger or os.path.join(H, "seen-jobs.json")
    a.config = a.config or os.path.join(H, "daily-config.json")
    a.keywords = a.keywords or os.path.join(H, "keywords.txt")
    a.tracker = a.tracker or os.path.join(H, "applications-tracker.md")
    a.weights = a.weights or os.path.join(H, "learned-weights.json")
    boards = a.boards or [os.path.join(H, "target-companies.md")
                          if os.path.exists(os.path.join(H, "target-companies.md"))
                          else os.path.join(HERE, "..", "live-ats-board-search", "target-companies.md")]
    now = today_of(a)
    iso = now.isoformat()

    cfg = dict(DEFAULT_CONFIG); cfg.update(load_json(a.config, {}))
    fp = hashlib.sha256(json.dumps({k: cfg.get(k) for k in ("pay_floor", "pay_buffer", "location_allow", "location_block",
                        "exclude_title_patterns", "require_title_patterns", "exclude_companies", "exclude_sections")},
                        sort_keys=True).encode()).hexdigest()[:12]
    ledger = load_json(a.ledger, {"version": 1, "jobs": {}})
    jobs = ledger.setdefault("jobs", {})
    refilter = ledger.get("filters_fingerprint") not in (None, fp)

    rows, seen_keys = [], set()
    for path in a.search:
        for j in load_json(path, []):
            k = row_key(j)
            if k in seen_keys:
                continue
            seen_keys.add(k); j["_key"] = k; rows.append(j)

    # repost index: company|title -> most recent last_seen
    recent = {}
    for k, e in jobs.items():
        ck = T.norm_company(e.get("company")) + "|" + norm(e.get("title"))
        if e.get("last_seen", "") > recent.get(ck, ("", ""))[0]:
            recent[ck] = (e.get("last_seen", ""), k)
    tkeys, tpairs = set(), []
    if os.path.exists(a.tracker):
        apps, _ = T.load(a.tracker)
        tkeys, tpairs = T.tracker_keys(apps)

    def record(j, outcome):
        e = jobs.get(j["_key"]) or {"first_seen": iso, "company": j.get("company"), "title": j.get("title"),
                                    "url": j.get("url"), "source": j.get("platform") or j.get("ats")}
        e["last_seen"] = iso
        if outcome:
            e["outcome"] = outcome
        jobs[j["_key"]] = e

    # The first time description-mode output reaches an existing ledger, its description-only rows were not "new
    # today", they were simply invisible to title search. Record them as seeded once instead of posting a backlog.
    desc_baseline = (not a.seed and jobs and not ledger.get("description_baseline")
                     and any(j.get("match_reason") == "description" for j in rows))
    candidates, counts = [], {"in_ledger": 0, "repost": 0, "in_tracker": 0, "description_baseline": 0}
    for j in rows:
        e = jobs.get(j["_key"])
        if desc_baseline and not e and j.get("match_reason") == "description":
            record(j, "seeded"); counts["description_baseline"] += 1; continue
        if a.seed:
            record(j, None if e else "seeded"); continue
        if e:
            if refilter and str(e.get("outcome", "")).startswith("filtered"):
                candidates.append(j)
            else:
                record(j, None); counts["in_ledger"] += 1
            continue
        prev = recent.get(ct_key(j))
        if prev and prev[0] and (now - dt.date.fromisoformat(prev[0])).days <= a.repost_days:
            record(j, f"repost-of:{prev[1]}"); counts["repost"] += 1; continue
        if j["_key"] in tkeys or any(T.same_role(c, t, j.get("company"), j.get("title")) for c, t in tpairs):
            record(j, "in_tracker"); counts["in_tracker"] += 1; continue
        candidates.append(j)

    new, dropped = [], {}
    if not a.seed and candidates:
        sections = board_sections(boards)
        tiers = T.load_keywords(a.keywords)
        phrases = T.compile_phrases([p for p, _ in tiers]) if tiers else T.compile_phrases(
            sorted({m for j in rows for m in j.get("matched", [])}))
        weights = load_json(a.weights, {})
        stage1 = []
        for j in candidates:
            j["_industry"] = j.get("section") or sections.get(j.get("token", ""), "")
            why = title_filter(j, cfg, sections)
            if why:
                record(j, "filtered:" + why); dropped[why] = dropped.get(why, 0) + 1; continue
            ok, _ = location_ok(j, cfg)
            if ok is False and (j.get("platform") or j.get("ats")) not in ("ashby", "greenhouse", "lever"):
                record(j, "filtered:location"); dropped["location"] = dropped.get("location", 0) + 1; continue
            stage1.append(j)
        if not a.no_details:
            with ThreadPoolExecutor(8) as ex:
                for j, d in zip(stage1, ex.map(fetch_detail, stage1)):
                    j.update(d)
        elif stage1:
            for j in stage1:
                if (j.get("platform") or j.get("ats")) == "workday":
                    j.update(fetch_detail(j))
        for j in stage1:
            ok, _ = location_ok(j, cfg)
            if ok is False:
                record(j, "filtered:location"); dropped["location"] = dropped.get("location", 0) + 1; continue
            j["_loc_ok"] = ok
            j["_pay"], j["_pay_label"] = pay_check(j, cfg)
            if j["_pay"] == "drop":
                record(j, "filtered:pay"); dropped["pay"] = dropped.get("pay", 0) + 1; continue
            score(j, cfg, tiers, phrases, weights, now)
            record(j, "reported")
            new.append(j)
        new.sort(key=lambda j: -j["_score"])

    # prune
    for k in [k for k, e in jobs.items() if e.get("last_seen") and (now - dt.date.fromisoformat(e["last_seen"])).days > a.prune_days]:
        del jobs[k]
    ledger.update(version=1, updated=iso, filters_fingerprint=fp)
    if desc_baseline or (a.seed and any(j.get("match_reason") == "description" for j in rows)):
        ledger["description_baseline"] = iso
    if not a.dry_run:
        out = a.ledger_out or a.ledger
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        tmp = out + ".tmp"
        json.dump(ledger, open(tmp, "w"), indent=1, sort_keys=True)
        os.replace(tmp, out)

    clean = [{k: v for k, v in j.items() if k not in ("text", "description")} for j in new]
    more_path = a.json_out or os.path.join(H, "daily", f"new-{iso}.json")
    if new:
        if not a.dry_run or a.json_out:
            os.makedirs(os.path.dirname(os.path.abspath(more_path)), exist_ok=True)
            json.dump(clean, open(more_path, "w"), indent=1)
        md = digest(new, dropped, cfg, now, a.note, more_path)
        print(md)
        if a.digest_out:
            open(a.digest_out, "w").write(md + "\n")
    elif a.json_out:
        json.dump([], open(a.json_out, "w"))
    if a.seed:
        msg = f"SEED: baseline set, {len(jobs)} roles in ledger"
    else:
        msg = (f"already seen {counts['in_ledger']}, reposts {counts['repost']}, in tracker {counts['in_tracker']}, "
               + (f"description-only baseline {counts['description_baseline']}, " if counts['description_baseline'] else "") +
               f"candidates {len(candidates)}, filtered {sum(dropped.values())} {dropped or ''}, NEW {len(new)}")
    print(f"--- daily_diff: {len(rows)} search rows | {msg} | ledger {len(jobs)} entries"
          f"{' (dry run)' if a.dry_run else ''} ---", file=sys.stderr)

if __name__ == "__main__":
    main()
