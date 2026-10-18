#!/usr/bin/env python3
"""CareerMate application tracker and learning loop. Stdlib only.

Files (defaults; override with --home or per-file flags):
  ~/careermate/applications-tracker.md   private, human-readable markdown table (Applications + Leads)
  ~/careermate/learned-signals.md        what moves forward vs gets rejected/ghosted (written by `learn`)
  ~/careermate/learned-weights.json      score adjustments the daily run applies (written by `learn`)
  ~/careermate/tracker-email-log.json    processed email ids with a one-line summary (never bodies)
  ~/careermate/keywords.txt              confirmed title/keyword phrases (used for title-family signals)
  ~/careermate/submission-log.jsonl      apply-check reservations and submissions with timestamps (daily cap)
  ~/careermate/interviews.json           interview times, durations and check-in routine ids, per tracker row
  ~/careermate/apply-queue.json          roles the user picked after the daily cap was reached (not approvals)

Commands:
  init | add | update | note | lead | find | list | refresh | learn | summary | email-seen | email-log
  apply-check | apply-release | queue | interview | interviews | wrapup
Run `tracker.py <command> -h` for flags. Exit code 2 means "ambiguous or not found": read the candidates and decide.
Exit code 3 means "blocked by the daily application cap" (or no apply-check for this role); 4 means another
application is still open (finish it with `add` or free it with `apply-release` first).
Times use the user's time zone: --tz, else $CAREERMATE_TZ, else a "Time zone: Area/City" line in
search-preferences.md, else the system zone.
The daily run imports this file for features() and adjustment() so both sides compute signals the same way.
"""
import argparse, datetime as dt, difflib, json, math, os, re, sys
from zoneinfo import ZoneInfo

HOME = os.path.expanduser("~/careermate")
HERE = os.path.dirname(os.path.abspath(__file__))

STATUSES = ["applied", "recruiter reply", "screen scheduled", "interviewing", "offer", "accepted",
            "rejected", "withdrawn", "ghosted", "not applied"]
STAGE = {"applied": 0, "recruiter reply": 1, "screen scheduled": 2, "interviewing": 3, "offer": 4, "accepted": 5}
FORWARD = {"recruiter reply", "screen scheduled", "interviewing", "offer", "accepted"}
TERMINAL = {"rejected", "offer", "withdrawn", "accepted"}
ACTIVE = {"applied", "recruiter reply", "screen scheduled", "interviewing", "offer"}
ALIASES = {"reply": "recruiter reply", "recruiter": "recruiter reply", "recruiter outreach": "recruiter reply",
           "assessment": "recruiter reply", "assessment request": "recruiter reply", "screen": "screen scheduled",
           "phone screen": "screen scheduled", "interview": "interviewing", "interviews": "interviewing",
           "rejection": "rejected", "declined": "rejected", "withdraw": "withdrawn", "withdrew": "withdrawn",
           "ghost": "ghosted", "submitted": "applied", "unsubmitted": "not applied",
           "offer accepted": "accepted", "accepted offer": "accepted", "hired": "accepted"}
GHOST_DAYS = 14
MIN_SAMPLE = 3        # decided outcomes needed before a feature can move a score
MIN_TOTAL = 5         # decided outcomes needed overall before any adjustment
DIM_CAP, TOTAL_CAP = 5, 10
DAILY_CAP = 15        # submitted applications per calendar day in the user's time zone; not configurable by design
RESERVE_HOURS = 3     # an apply-check slot that was never submitted or released frees itself after this long
CHECKIN_AFTER_MIN = 60
DEFAULT_INTERVIEW_MIN = 60
COLS = ["#", "Company", "Title", "Link", "Source", "Applied", "Status", "Furthest stage", "Last update",
        "Industry", "Size", "Submitted at", "Submitted by", "Interview", "Notes"]
LEAD_COLS = ["Date", "Company", "Role", "Source", "Note"]

HEADER = """# CareerMate application tracker

Private. Kept by CareerMate for you only. Email bodies are never stored here: notes hold one-line summaries.
Statuses: applied, recruiter reply, screen scheduled, interviewing, offer, accepted, rejected, withdrawn,
ghosted (no response 14 days after applying), not applied. "Furthest stage" keeps the best stage reached, so a
rejection after an interview still counts as moving forward when CareerMate learns from outcomes.
"""

# ---------------------------------------------------------------- text helpers (shared with daily_diff.py)

def norm(text):
    text = (text or "").lower().replace("&", " and ")
    return " ".join(re.sub(r"[^a-z0-9+#*]+", " ", text).split())

def compile_phrases(phrases):
    pats, seen = [], set()
    for raw in phrases:
        p = norm(raw)
        prefix = p.endswith("*")
        p = p.rstrip("*").replace("*", "").strip()
        if not p or (p, prefix) in seen:
            continue
        seen.add((p, prefix))
        rx = r"(?<![a-z0-9+#])" + re.escape(p) + (r"[a-z0-9+#]*" if prefix else r"(?![a-z0-9+#])")
        pats.append((raw.strip(), re.compile(rx)))
    return pats

def load_keywords(path):
    """Returns [(phrase, tier)]. Tier comes from optional '# core' / '# expansion' / '# adjacent' header lines;
    search_boards.py ignores every '#' line, so the same file feeds both scripts."""
    out, tier = [], "expansion"
    if not path or not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        s = line.strip()
        if s.startswith("#"):
            m = re.match(r"#\s*(core|expansion|adjacent)\b", s, re.I)
            if m:
                tier = m.group(1).lower()
            continue
        out.extend((x.strip(), tier) for x in s.split("|") if x.strip())
    return out

COMPANY_SUFFIX = re.compile(r"\b(inc|llc|ltd|limited|corp|corporation|co|company|plc|gmbh|technologies|technology|the)\b")
def norm_company(c):
    """Whole normalized company name: lowercase, punctuation stripped, legal/common suffixes (Inc, LLC, Ltd, Corp, Co,
    Technologies, ...) and parentheticals removed. Compared for equality only, never by substring."""
    c = re.sub(r"\(.*?\)", " ", c or "")
    n = norm(c)
    return " ".join(COMPANY_SUFFIX.sub(" ", n).split()) or n

LEVELS = [("chief", r"\b(chief|ceo|coo|cpo|cto|cfo|cro|cmo|chro|cio)\b"),
          ("svp/evp", r"\b(svp|evp|senior vice president|executive vice president)\b"),
          ("vp", r"\b(vp|vice president|avp)\b"), ("head", r"\bhead\b"),
          ("senior director", r"\b(senior|sr) director\b"), ("director", r"\bdirector\b"),
          ("senior manager", r"\b(senior|sr) manager\b"), ("manager", r"\bmanager\b"),
          ("lead", r"\b(lead|leader|principal)\b")]
def level(title):
    n = norm(title)
    return next((name for name, rx in LEVELS if re.search(rx, n)), "other")

STOP = set("""of and the for to a an in at on with or head vp vice president chief director senior sr svp evp avp lead
leader manager principal global us usa remote staff associate executive officer i ii iii iv team new role
north america americas emea apac hybrid onsite based""".split())
def title_words(title):
    return sorted({w for w in norm(title).split() if w not in STOP and not w.isdigit() and len(w) > 1})

def platform_of(source, link=""):
    s = norm(source) + " " + (link or "").lower()
    for p in ("greenhouse", "ashby", "lever", "workday", "workable", "smartrecruiters", "rippling", "icims"):
        if p in s:
            return p
    if "myworkdayjobs" in s:
        return "workday"
    if "gh_jid" in s:
        return "greenhouse"
    return norm(source) or "other"

def features(title, company, source, industry="", size="", phrases=None):
    """[(dim, value, label, noun)] for one role. phrases: compiled [(raw, rx)] from keywords.txt.
    label names the signal in tables; noun completes "N of your M <noun>" in explanations."""
    n, out = norm(title), []
    for raw, rx in phrases or []:
        if rx.search(n):
            out.append(("title", "phrase:" + norm(raw), f'"{raw}" titles', f'"{raw}" applications'))
    for w in title_words(title):
        out.append(("title", "word:" + w, f'titles with "{w}"', f'applications with "{w}" in the title'))
    lv = level(title)
    if lv != "other":
        out.append(("level", lv, f"{lv}-level roles", f"{lv}-level applications"))
    if company:
        out.append(("company", norm_company(company), company.strip(), f"applications to {company.strip()}"))
    if industry:
        out.append(("industry", norm(industry), f"{industry} companies", f"applications to {industry} companies"))
    if size:
        out.append(("size", norm(size), f"companies of {size} people", f"applications to companies of {size} people"))
    p = platform_of(source)
    if p:
        out.append(("source", p, f"roles applied through {p.capitalize()}", f"{p.capitalize()} applications"))
    return out

def adjustment(feats, weights):
    """Returns (points, reasons). Takes the strongest learned feature per dimension, caps each dimension at
    +/-DIM_CAP and the total at +/-TOTAL_CAP. Re-ranks only; never used to drop a role."""
    table = {(f["dim"], f["value"]): f for f in (weights or {}).get("features", [])}
    best = {}
    for dim, value, *_ in feats:
        f = table.get((dim, value))
        if f and (dim not in best or abs(f["adj"]) > abs(best[dim]["adj"])):
            best[dim] = f
    pts = sum(max(-DIM_CAP, min(DIM_CAP, f["adj"])) for f in best.values())
    pts = max(-TOTAL_CAP, min(TOTAL_CAP, pts))
    reasons = [f'{"+" if f["adj"] > 0 else ""}{max(-DIM_CAP, min(DIM_CAP, f["adj"]))} '
               + ("ranked higher" if f["adj"] > 0 else "ranked lower") + " because " + f["why"]
               for f in sorted(best.values(), key=lambda f: -abs(f["adj"]))]
    return pts, reasons

# ---------------------------------------------------------------- job keys (shared with daily_diff.py)

def job_key(url="", platform="", job_id=None, tenant="", req_id=None):
    """Stable key for a posting: ATS job id where the URL or record has one, else the normalized URL."""
    u = (url or "").strip()
    low = u.lower()
    p = platform or platform_of("", u)
    m = re.search(r"[?&]gh_jid=(\d+)", low) or re.search(r"greenhouse\.io/.*/jobs/(\d+)", low)
    if p == "greenhouse" and job_id:
        return f"greenhouse:{job_id}"
    if m:
        return f"greenhouse:{m.group(1)}"
    m = re.search(r"jobs\.ashbyhq\.com/[^/]+/([0-9a-f\-]{36})", low)
    if m:
        return f"ashby:{m.group(1)}"
    m = re.search(r"jobs\.lever\.co/[^/]+/([0-9a-f\-]{36})", low)
    if m:
        return f"lever:{m.group(1)}"
    m = re.search(r"jobs\.smartrecruiters\.com/([^/]+)/(\d+)", low)
    if m:
        return f"smartrecruiters:{m.group(2)}"
    m = re.search(r"https?://([a-z0-9\-]+)\.wd\d+\.myworkdayjobs\.com/.*?/([^/?#]+?)/?(?:[?#]|$)", low)
    if m or p == "workday":
        ten = (tenant or (m.group(1) if m else "")).lower()
        rid = req_id or job_id
        if not rid and m:
            seg = m.group(2)
            rid = seg.rsplit("_", 1)[-1] if "_" in seg else seg
        if ten and rid:
            rid = re.sub(r"-\d+$", "", str(rid).lower())   # "_Req39018-2" is a repost of req Req39018
            return f"workday:{ten}:{rid}"
    m = re.search(r"apply\.workable\.com/([^/]+)/j/([0-9a-z]+)", low)
    if m:
        return f"workable:{m.group(1)}:{m.group(2)}"
    m = re.match(r"https?://(?:www\.)?([^?#]+)", low)
    return "url:" + (m.group(1).rstrip("/") if m else low)

def same_role(c1, t1, c2, t2, link1="", link2=""):
    """Same company (whole normalized name) and same or near-identical title. When both sides have job links, the
    links decide: the same job key is the same job, different keys are different jobs."""
    if link1 and link2:
        return job_key(link1) == job_key(link2)
    n1, n2 = norm_company(c1), norm_company(c2)
    if not n1 or n1 != n2:
        return False
    return norm(t1) == norm(t2) or difflib.SequenceMatcher(None, norm(t1), norm(t2)).ratio() >= 0.9

# ---------------------------------------------------------------- tracker file

def cell(v):
    return str(v or "").replace("|", "/").replace("\n", " ").strip()

def parse_table(lines, start):
    rows, cols = [], None
    for line in lines[start:]:
        if line.startswith("## "):
            break
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cols is None:
            cols = cells
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        rows.append(dict(zip(cols, cells + [""] * (len(cols) - len(cells)))))
    return rows

def load(path):
    if not os.path.exists(path):
        return [], []
    lines = open(path, encoding="utf-8").read().splitlines()
    apps = leads = []
    for i, line in enumerate(lines):
        if line.strip().lower() == "## applications":
            apps = parse_table(lines, i + 1)
        elif line.strip().lower() == "## leads":
            leads = parse_table(lines, i + 1)
    for r in apps:
        if not r.get("Submitted by"):
            r["Submitted by"] = submitted_by(r)
    return apps, leads

def submitted_by(r):
    """'user' or 'careermate' for a submitted row ('' for not applied). Reads the Submitted by column; older rows
    without it fall back to the 'submitted by the user' note, else careermate."""
    v = (r.get("Submitted by") or "").strip().lower()
    if v in ("user", "careermate"):
        return v
    if "submitted by the user" in (r.get("Notes") or ""):
        return "user"
    if (r.get("Status") or "") == "not applied" or not (r.get("Applied") or r.get("Submitted at")):
        return ""
    return "careermate"

def save(path, apps, leads):
    out = [HEADER, "## Applications", "", "| " + " | ".join(COLS) + " |", "|" + "---|" * len(COLS)]
    for r in apps:
        out.append("| " + " | ".join(cell(r.get(c)) for c in COLS) + " |")
    out += ["", "## Leads", "", "Recruiter outreach and referrals for roles you have not applied to. Not tracked as applications.", "",
            "| " + " | ".join(LEAD_COLS) + " |", "|" + "---|" * len(LEAD_COLS)]
    for r in leads:
        out.append("| " + " | ".join(cell(r.get(c)) for c in LEAD_COLS) + " |")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    open(tmp, "w", encoding="utf-8").write("\n".join(out) + "\n")
    os.replace(tmp, path)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass

def tracker_keys(apps):
    """(set of job keys, list of (company, title)) for every row, used by the daily run to skip tracked roles."""
    keys = {job_key(r.get("Link", "")) for r in apps if r.get("Link")}
    return keys, [(r.get("Company", ""), r.get("Title", "")) for r in apps]

def norm_status(s):
    s = (s or "").strip().lower()
    s = ALIASES.get(s, s)
    if s not in STATUSES:
        sys.exit(f"unknown status {s!r}; use one of: {', '.join(STATUSES)}")
    return s

def prefs_tz(home):
    p = os.path.join(home or HOME, "search-preferences.md")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            m = re.match(r"\s*[-*]?\s*\**time zone[^:\n]*:\s*\**\s*([A-Za-z_]+(?:/[A-Za-z0-9_+\-]+)+|UTC)\b", line, re.I)
            if m:
                return m.group(1)
    return ""

def user_tz(a):
    name = getattr(a, "tz", None) or os.environ.get("CAREERMATE_TZ") or prefs_tz(getattr(a, "home", HOME))
    if name:
        try:
            return ZoneInfo(name)
        except Exception:
            sys.exit(f"unknown time zone {name!r}; use an IANA name such as America/New_York")
    try:   # system zone by IANA name, so daylight saving is right for dates other than today
        link = os.path.realpath("/etc/localtime")
        if "zoneinfo/" in link:
            return ZoneInfo(link.split("zoneinfo/", 1)[1])
    except Exception:
        pass
    return dt.datetime.now().astimezone().tzinfo

def parse_when(s, tz):
    """ISO date-time; a time without an offset is read as the user's local time. Returns it in tz."""
    d = dt.datetime.fromisoformat(str(s).strip().replace("Z", "+00:00"))
    if d.tzinfo is None:
        d = d.replace(tzinfo=tz)
    return d.astimezone(tz)

def now_dt(a):
    tz = user_tz(a)
    if getattr(a, "now", None):
        return parse_when(a.now, tz)
    if getattr(a, "today", None):
        return dt.datetime.combine(dt.date.fromisoformat(a.today), dt.time(12, 0), tz)
    return dt.datetime.now(tz)

def today(a):
    return now_dt(a).date()

def show_dt(d):
    return d.strftime("%a %b %-d, %Y %-I:%M %p %Z")

def pdate(s):
    try:
        return dt.date.fromisoformat((s or "")[:10])
    except ValueError:
        return None

def find(apps, company, title=None):
    """Candidates sorted by confidence: [(row, confidence 0-1, reason)]."""
    nc = norm_company(company)
    out = []
    for r in apps:
        rc = norm_company(r.get("Company"))
        if not nc or not rc:
            continue
        if rc == nc:
            cs = 1.0
        elif nc in rc or rc in nc:
            cs = 0.85
        else:
            cs = difflib.SequenceMatcher(None, nc, rc).ratio()
            if cs < 0.8:
                continue
        if title:
            ts = difflib.SequenceMatcher(None, norm(title), norm(r.get("Title"))).ratio()
            tw, rw = set(title_words(title)), set(title_words(r.get("Title", "")))
            if tw and rw:
                ts = max(ts, len(tw & rw) / len(tw | rw))
            conf = cs * (0.4 + 0.6 * ts)
            why = f"company {cs:.2f}, title {ts:.2f}"
        else:
            conf, why = cs * 0.8, f"company {cs:.2f}, no title given"
        out.append((r, round(conf, 2), why))
    return sorted(out, key=lambda x: -x[1])

def pick(apps, a):
    if getattr(a, "row", None):
        r = next((r for r in apps if r.get("#") == str(a.row)), None)
        if not r:
            print(json.dumps({"error": f"no row #{a.row}"})); sys.exit(2)
        return r
    cands = find(apps, a.company, a.title)
    company_rows = [c for c in cands if c[1] >= 0.5]
    live = [c for c in company_rows if c[0].get("Status") != "not applied"]
    if len(company_rows) > 1 and len(live) == 1 and (not a.title or live[0][1] >= 0.6):
        return live[0][0]          # only one of them was actually submitted
    if len(company_rows) == 1 and (not a.title or company_rows[0][1] >= 0.6):
        return company_rows[0][0]
    if len(company_rows) > 1 and company_rows[0][1] >= 0.75 and company_rows[0][1] - company_rows[1][1] >= 0.15:
        return company_rows[0][0]
    print(json.dumps({"error": "ambiguous or not found; pass --row N, or treat as a lead",
                      "candidates": [{"row": r.get("#"), "company": r.get("Company"), "title": r.get("Title"),
                                      "status": r.get("Status"), "confidence": c, "why": w} for r, c, w in cands[:5]]},
                     indent=1))
    sys.exit(2)

def append_note(r, text, when):
    if text:
        note = f"{when} {text}".strip()
        r["Notes"] = (r.get("Notes", "") + "; " + note).strip("; ") if r.get("Notes") else note

def industry_lookup(company):
    """Section heading for a company in the board lists (user copies first), or ''."""
    nc = norm_company(company)
    for p in (os.path.join(HOME, "target-companies.md"),
              os.path.join(HERE, "..", "live-ats-board-search", "target-companies.md"),
              os.path.join(HOME, "workday-companies.md"),
              os.path.join(HERE, "..", "live-ats-board-search", "workday-companies.md")):
        if not os.path.exists(p):
            continue
        section = ""
        for line in open(p, encoding="utf-8"):
            if line.startswith("### "):
                section = line[4:].strip()
            elif line.startswith("| ") and section:
                c = line.strip().strip("|").split("|")[0].strip()
                if norm_company(c) == nc:
                    return section
    return ""

# ---------------------------------------------------------------- learning

def outcome(r, now):
    st = (r.get("Status") or "").lower()
    furthest = (r.get("Furthest stage") or "").lower()
    if st in ("withdrawn", "not applied"):
        return None
    if st in FORWARD or furthest in FORWARD:
        return "forward"
    if st == "rejected":
        return "rejected"
    if st == "ghosted":
        return "ghosted"
    d = pdate(r.get("Applied"))
    if st == "applied" and d and (now - d).days >= GHOST_DAYS:
        return "ghosted"
    return "pending"

def learn(apps, phrases, now):
    rows = []
    for r in apps:
        o = outcome(r, now)
        if o is None:
            continue
        rows.append((r, o, features(r.get("Title"), r.get("Company"), r.get("Source"), r.get("Industry"),
                                     r.get("Size"), phrases)))
    decided = [x for x in rows if x[1] != "pending"]
    fwd_total = sum(1 for x in decided if x[1] == "forward")
    base = fwd_total / len(decided) if decided else 0.0
    stats = {}
    for r, o, feats in rows:
        for dim, value, label, noun in set(feats):
            s = stats.setdefault((dim, value), {"dim": dim, "value": value, "label": label, "noun": noun, "applied": 0,
                                                "forward": 0, "rejected": 0, "ghosted": 0, "pending": 0})
            s["applied"] += 1
            s[o] += 1
    feats_out = []
    for s in stats.values():
        n = s["forward"] + s["rejected"] + s["ghosted"]
        s["decided"] = n
        s["adj"] = 0
        if len(decided) >= MIN_TOTAL and n >= MIN_SAMPLE:
            rate = (s["forward"] + 2 * base) / (n + 2)          # shrink toward your overall rate
            s["adj"] = max(-DIM_CAP, min(DIM_CAP, round(12 * (rate - base))))
        if s["adj"] > 0:
            s["why"] = (f'{s["forward"]} of your {n} {s["noun"]} got a recruiter reply or further '
                        f"(all applications: {fwd_total} of {len(decided)})")
        elif s["adj"] < 0:
            s["why"] = (f'{s["forward"]} of your {n} {s["noun"]} moved forward '
                        f'({s["rejected"]} rejected, {s["ghosted"]} no response; all applications: {fwd_total} of {len(decided)})')
        if s["adj"]:
            feats_out.append({k: s[k] for k in ("dim", "value", "label", "noun", "adj", "forward", "decided", "rejected",
                                                 "ghosted", "why")})
    weights = {"generated": now.isoformat(), "min_sample": MIN_SAMPLE, "min_total": MIN_TOTAL,
               "dim_cap": DIM_CAP, "total_cap": TOTAL_CAP,
               "baseline": {"forward": fwd_total, "decided": len(decided), "pending": len(rows) - len(decided)},
               "features": sorted(feats_out, key=lambda f: -abs(f["adj"]))}
    return weights, stats, rows

def signals_md(weights, stats, rows, now):
    b = weights["baseline"]
    L = ["# CareerMate learned signals", "",
         f"Updated {now.isoformat()}. Private. Built from your application tracker. Learned signals only re-rank "
         "new roles in the daily run, by at most 5 points per signal type and 10 points total; they never hide a role.", "",
         f"- Applications counted: {len(rows)} ({b['decided']} with an outcome, {b['pending']} still waiting)",
         f"- Moved forward (recruiter reply or further): {b['forward']} of {b['decided']}",
         f"- An application counts as no response (ghosted) {GHOST_DAYS} days after applying with no reply.", ""]
    if b["decided"] < MIN_TOTAL:
        L += [f"Not enough outcomes yet to adjust scores: {b['decided']} of the {MIN_TOTAL} needed. "
              "Until then the daily run uses the standard score only.", ""]
    else:
        L += ["## Adjustments in use", ""]
        if weights["features"]:
            L += [f"- {f['label']}: {'+' if f['adj'] > 0 else ''}{f['adj']} ({f['why']})" for f in weights["features"]]
        else:
            L.append("- None yet: no signal has a large enough sample or a clear difference from your overall rate.")
        L.append("")
    names = {"title": "Title families", "level": "Seniority", "company": "Companies", "industry": "Industries",
             "size": "Company size", "source": "Sources"}
    for dim, name in names.items():
        items = [s for s in stats.values() if s["dim"] == dim and (dim != "title" or s["applied"] >= 2)]
        if not items:
            continue
        L += [f"## {name}", "", "| Signal | Applied | Moved forward | Rejected | No response | Waiting | Score effect |",
              "|---|---|---|---|---|---|---|"]
        for s in sorted(items, key=lambda s: (-s["applied"], s["label"])):
            eff = f"{'+' if s['adj'] > 0 else ''}{s['adj']}" if s["adj"] else "none"
            L.append(f"| {cell(s['label'])} | {s['applied']} | {s['forward']} | {s['rejected']} | {s['ghosted']} | "
                     f"{s['pending']} | {eff} |")
        L.append("")
    return "\n".join(L) + "\n"

# ---------------------------------------------------------------- commands

def cmd_init(a):
    apps, leads = load(a.tracker)
    save(a.tracker, apps, leads)
    print(f"tracker ready: {a.tracker} ({len(apps)} applications, {len(leads)} leads)")

def cmd_add(a):
    apps, leads = load(a.tracker)
    key = job_key(a.link) if a.link else None
    for r in apps:
        if same_role(r["Company"], r["Title"], a.company, a.title, r.get("Link"), a.link):
            if not a.force:
                print(json.dumps({"error": "already tracked", "row": r.get("#"), "company": r["Company"],
                                  "title": r["Title"], "status": r["Status"]}))
                sys.exit(2)
    st = norm_status(a.status)
    now = now_dt(a)
    when = a.applied or now.date().isoformat()
    submitted_at, extra_note, entry = "", "", role_entry(a.company, a.title, a.link)
    if st != "not applied":
        if a.submitted_at:
            submitted_at = parse_when(a.submitted_at, now.tzinfo).isoformat(timespec="minutes")
            if not a.applied:
                when = submitted_at[:10]
        elif when == now.date().isoformat():
            submitted_at = now.isoformat(timespec="minutes")
        if submitted_at[:10] == now.date().isoformat() and a.by == "careermate":
            extra_note = require_check(a, entry, now, a.no_check_reason)
    n = max([int(r["#"]) for r in apps if r.get("#", "").isdigit()] + [0]) + 1
    r = {"#": str(n), "Company": a.company, "Title": a.title, "Link": a.link or "", "Source": a.source or
         platform_of("", a.link or "").capitalize(), "Applied": when if st != "not applied" else "",
         "Status": st, "Furthest stage": st if st in FORWARD else "", "Last update": when,
         "Industry": a.industry if a.industry is not None else industry_lookup(a.company), "Size": a.size or "",
         "Submitted at": submitted_at, "Submitted by": a.by if st != "not applied" else "", "Interview": "", "Notes": "; ".join(x for x in (a.notes, extra_note) if x)}
    if a.by == "user" and st != "not applied":
        r["Notes"] = "; ".join(x for x in (r["Notes"], "submitted by the user") if x)
    apps.append(r)
    save(a.tracker, apps, leads)
    out = {"added": r}
    if submitted_at:
        write_event(a, "submitted", entry, parse_when(submitted_at, now.tzinfo), by=a.by, row=r["#"])
        _, _, out["cap"] = cap_state(a, now)
    print(json.dumps(out, indent=1))

def cmd_update(a):
    apps, leads = load(a.tracker)
    r = pick(apps, a)
    new = norm_status(a.status) if a.status else r["Status"]
    old = r.get("Status", "")
    now = now_dt(a)
    when = a.date or now.date().isoformat()
    if old == "not applied" and new != "not applied" and new not in ("withdrawn", "rejected"):
        # a prepared role that is now submitted: same cap rules as add
        entry = role_entry(r.get("Company"), r.get("Title"), r.get("Link"))
        if a.by == "careermate":
            extra = require_check(a, entry, now, a.no_check_reason)
            if extra:
                a.note = "; ".join(x for x in (a.note, extra) if x)
        r["Applied"] = r.get("Applied") or now.date().isoformat()
        r["Submitted at"] = now.isoformat(timespec="minutes")
        r["Submitted by"] = a.by
        write_event(a, "submitted", entry, now, by=a.by, row=r["#"])
    if a.status and not a.force:
        if old in TERMINAL and new != old and new not in ("offer",):
            print(json.dumps({"error": f"row #{r['#']} is already {old}; pass --force to change it", "row": r}))
            sys.exit(2)
        if new in STAGE and old in STAGE and STAGE[new] < STAGE[old]:
            a.note = f"{a.note or 'update'} (kept status {old})"
            new = old
    r["Status"] = new
    if new in FORWARD and STAGE.get(new, 0) > STAGE.get(r.get("Furthest stage", ""), 0):
        r["Furthest stage"] = new
    r["Last update"] = when
    append_note(r, a.note, when)
    save(a.tracker, apps, leads)
    print(json.dumps({"updated": r, "previous_status": old}, indent=1))

def cmd_note(a):
    apps, leads = load(a.tracker)
    r = pick(apps, a)
    append_note(r, a.note, a.date or today(a).isoformat())
    save(a.tracker, apps, leads)
    print(json.dumps({"noted": r}, indent=1))

def cmd_lead(a):
    apps, leads = load(a.tracker)
    when = a.date or today(a).isoformat()
    for l in leads:
        if same_role(l["Company"], l["Role"], a.company, a.role or ""):
            l["Note"] = (l.get("Note", "") + f"; {when} {a.note or ''}").strip("; ")
            save(a.tracker, apps, leads)
            print(json.dumps({"lead_updated": l})); return
    l = {"Date": when, "Company": a.company, "Role": a.role or "not stated", "Source": a.source or "", "Note": a.note or ""}
    leads.append(l)
    save(a.tracker, apps, leads)
    print(json.dumps({"lead_added": l}))

def cmd_find(a):
    apps, _ = load(a.tracker)
    c = find(apps, a.company, a.title)
    print(json.dumps([{"row": r.get("#"), "company": r.get("Company"), "title": r.get("Title"), "status": r.get("Status"),
                       "confidence": s, "why": w} for r, s, w in c[:5]], indent=1))
    if not c:
        sys.exit(2)

def cmd_list(a):
    apps, leads = load(a.tracker)
    rows = [r for r in apps if not a.status or r.get("Status") == norm_status(a.status)]
    if a.json:
        print(json.dumps({"applications": rows, "leads": leads}, indent=1)); return
    counts = {}
    for r in apps:
        counts[r.get("Status")] = counts.get(r.get("Status"), 0) + 1
    print(f"{len(apps)} applications: " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items(), key=lambda x: -x[1])))
    for r in rows:
        print(f"#{r['#']} {r['Company']} | {r['Title']} | {r['Status']} | applied {r['Applied']} | last {r['Last update']}")
    if leads:
        print(f"{len(leads)} leads")

def cmd_refresh(a):
    apps, leads = load(a.tracker)
    now, changed = today(a), []
    for r in apps:
        d = pdate(r.get("Applied"))
        if r.get("Status") == "applied" and d and (now - d).days >= GHOST_DAYS:
            r["Status"] = "ghosted"
            r["Last update"] = now.isoformat()
            append_note(r, f"no response {(now - d).days} days after applying", now.isoformat())
            changed.append(f"#{r['#']} {r['Company']} | {r['Title']}")
    if changed and not a.dry_run:
        save(a.tracker, apps, leads)
    print(json.dumps({"marked_ghosted": changed}, indent=1))

def cmd_learn(a):
    apps, _ = load(a.tracker)
    now = today(a)
    phrases = compile_phrases([p for p, _ in load_keywords(a.keywords)])
    weights, stats, rows = learn(apps, phrases, now)
    if not a.dry_run:
        json.dump(weights, open(a.weights, "w"), indent=1)
        open(a.signals, "w", encoding="utf-8").write(signals_md(weights, stats, rows, now))
    print(json.dumps({"baseline": weights["baseline"], "adjustments": len(weights["features"]),
                      "top": weights["features"][:5]}, indent=1))

def cmd_summary(a):
    apps, leads = load(a.tracker)
    now = today(a)
    since = now - dt.timedelta(days=a.days)
    phrases = compile_phrases([p for p, _ in load_keywords(a.keywords)])
    weights, stats, rows = learn(apps, phrases, now)
    counts = {}
    for r in apps:
        counts[r["Status"]] = counts.get(r["Status"], 0) + 1
    moved = [r for r in apps if (pdate(r.get("Last update")) or dt.date.min) > since and r["Status"] in FORWARD | {"rejected", "offer"}]
    applied_week = [r for r in apps if (pdate(r.get("Applied")) or dt.date.min) > since]
    quiet = [r for r in apps if r["Status"] == "ghosted" and (pdate(r.get("Last update")) or dt.date.min) > since]
    L = [f"## CareerMate weekly summary ({now.strftime('%a %b %-d, %Y')})", "",
         "**Pipeline:** " + ", ".join(f"{counts.get(s, 0)} {s}" for s in STATUSES if counts.get(s)) + f" ({len(apps)} total)",
         f"**This week:** {len(applied_week)} new applications; {len(moved)} replies or decisions; "
         f"{len(quiet)} went quiet (no response {GHOST_DAYS}+ days)"]
    for r in moved:
        L.append(f"- {r['Company']}, {r['Title']}: {r['Status']} ({r['Last update']})")
    L += ["", "**What's working:**"]
    b = weights["baseline"]
    if b["decided"] < MIN_TOTAL:
        L.append(f"- Too early to tell: {b['decided']} applications have an outcome so far (need {MIN_TOTAL}). "
                 f"{b['forward']} moved forward.")
    else:
        pos = [f for f in weights["features"] if f["adj"] > 0][:3]
        neg = [f for f in weights["features"] if f["adj"] < 0][:2]
        L += [f"- {f['label']}: {f['why']}" for f in pos] or ["- No signal stands out yet."]
        L += [f"- Weaker so far, {f['label']}: {f['why']}" for f in neg]
    L += ["", "**Worth a follow-up (suggestions only; CareerMate never sends anything):**"]
    fol = []
    for r in apps:
        d, lu, st = pdate(r.get("Applied")), pdate(r.get("Last update")), r.get("Status")
        if st == "applied" and d and 7 <= (now - d).days < GHOST_DAYS:
            fol.append(f"- {r['Company']}, {r['Title']}: applied {(now - d).days} days ago, no reply. A short note to the recruiter or hiring manager is reasonable now.")
        elif st == "ghosted" and lu and (now - lu).days <= 14:
            fol.append(f"- {r['Company']}, {r['Title']}: no response since {r['Applied']}. One polite follow-up, then let it go.")
        elif st in ("recruiter reply", "screen scheduled", "interviewing") and lu and (now - lu).days >= 5:
            fol.append(f"- {r['Company']}, {r['Title']}: {st}, nothing new for {(now - lu).days} days. Worth a check-in.")
    L += fol or ["- Nothing stale this week."]
    tz = user_tz(a)
    soon = []
    for row, items in load_iv(a).items():
        for i in items:
            if i.get("status") == "scheduled":
                d = parse_when(i["at"], tz)
                if now <= d.date() <= now + dt.timedelta(days=14):
                    r = next((x for x in apps if x["#"] == row), {})
                    soon.append((d, f"- {r.get('Company', '?')}, {r.get('Title', '?')}: {show_dt(d)}"
                                    + (f" ({i['round']})" if i.get("round") else "")))
    if soon:
        L += ["", "**Upcoming interviews:**"] + [x for _, x in sorted(soon)]
    if leads:
        recent = [l for l in leads if (pdate(l.get("Date")) or dt.date.min) > since]
        if recent:
            L += ["", "**New leads:**"] + [f"- {l['Company']}: {l['Role']} ({l['Note']})" for l in recent]
    print("\n".join(L))

def load_log(path):
    return json.load(open(path)) if os.path.exists(path) else {}

def cmd_email_seen(a):
    log = load_log(a.email_log)
    if a.id in log:
        print(json.dumps(log[a.id])); sys.exit(0)
    sys.exit(1)

def cmd_email_log(a):
    log = load_log(a.email_log)
    summary = (a.summary or "")[:160].replace("\n", " ")
    log[a.id] = {"date": a.date or today(a).isoformat(), "class": a.cls, "company": a.company or "",
                 "row": a.row_ref or "", "summary": summary}
    json.dump(log, open(a.email_log, "w"), indent=1)
    try:
        os.chmod(a.email_log, 0o600)
    except OSError:
        pass
    print(json.dumps({"logged": a.id}))

# ---------------------------------------------------------------- daily application cap

CAP_MESSAGE = ("You've sent {cap} applications today, which is CareerMate's daily limit. The limit is on purpose: "
               "recruiters read every application, and a few tailored ones get further than a large batch. "
               "I can save the roles you pick for tomorrow, and I'll check with you on each one again before "
               "anything is sent. The count resets at midnight ({tz}).")

def role_entry(company, title, link=""):
    return {"company": company or "", "title": title or "", "link": link or "",
            "key": job_key(link) if link else ""}

def same_entry(x, y):
    if x.get("key") and y.get("key"):
        return x["key"] == y["key"]   # both have job links: the links decide
    return same_role(x.get("company"), x.get("title"), y.get("company"), y.get("title"))

def log_file(a):
    return os.path.join(a.home, "submission-log.jsonl")

def read_events(a):
    p = log_file(a)
    if not os.path.exists(p):
        return []
    out = []
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out

def write_event(a, event, entry, when, **extra):
    os.makedirs(a.home, exist_ok=True)
    ev = {"ts": when.isoformat(timespec="seconds"), "event": event, **entry, **extra}
    with open(log_file(a), "a", encoding="utf-8") as f:
        f.write(json.dumps(ev) + "\n")
    try:
        os.chmod(log_file(a), 0o600)
    except OSError:
        pass
    return ev

def row_submit_date(r, tz):
    if (r.get("Status") or "") == "not applied":
        return None
    at = r.get("Submitted at")
    if at:
        try:
            return parse_when(at, tz).date()
        except ValueError:
            pass
    return pdate(r.get("Applied"))

def day_usage(a, now):
    """(submitted today, open reservations) as lists of entries. Counts tracker rows submitted on today's date in
    the user's time zone plus logged submissions, without double counting the same role. Applications the user
    sent themselves (--by user) do not count."""
    tz, day = now.tzinfo, now.date()
    apps, _ = load(a.tracker)
    subs = []
    def add_sub(e):
        if not any(same_entry(e, s) for s in subs):
            subs.append(e)
    for r in apps:
        if submitted_by(r) == "user":
            continue   # only applications CareerMate submits count toward the cap (column, else the old note)
        if row_submit_date(r, tz) == day:
            add_sub({**role_entry(r.get("Company"), r.get("Title"), r.get("Link")), "row": r.get("#"),
                     "ts": r.get("Submitted at") or r.get("Applied")})
    held = []
    for ev in read_events(a):
        try:
            t = parse_when(ev.get("ts"), tz)
        except (TypeError, ValueError):
            continue
        kind = ev.get("event")
        if kind == "submitted" and t.date() == day and ev.get("by") != "user":
            add_sub(ev)
        if kind == "reserved" and t.date() == day:
            held = [h for h in held if not same_entry(h, ev)] + [ev]
        elif kind in ("released", "submitted"):
            held = [h for h in held if not same_entry(h, ev)]
    held = [h for h in held if not any(same_entry(h, s) for s in subs)
            and now - parse_when(h["ts"], tz) < dt.timedelta(hours=RESERVE_HOURS)]
    return subs, held

def cap_state(a, now):
    subs, held = day_usage(a, now)
    used = len(subs) + len(held)
    midnight = dt.datetime.combine(now.date() + dt.timedelta(days=1), dt.time(0, 0), now.tzinfo)
    return subs, held, {"date": now.date().isoformat(), "time_zone": str(now.tzinfo), "cap": DAILY_CAP,
                        "submitted_today": len(subs), "open_checks": len(held), "remaining": max(0, DAILY_CAP - used),
                        "resets_at": midnight.isoformat(timespec="minutes")}

def cmd_apply_check(a):
    now = now_dt(a)
    subs, held, st = cap_state(a, now)
    msg = CAP_MESSAGE.format(cap=DAILY_CAP, tz=st["time_zone"])
    if not a.company:
        st["roles_today"] = [f"{s.get('company')} | {s.get('title')}" for s in subs]
        st["open"] = [f"{h.get('company')} | {h.get('title')} (checked {h.get('ts')})" for h in held]
        if st["remaining"] == 0:
            st["message"] = msg
        print(json.dumps(st, indent=1))
        sys.exit(3 if st["remaining"] == 0 else 0)
    if not a.title:
        sys.exit("apply-check needs --title as well as --company: one named role per check")
    me = role_entry(a.company, a.title, a.link)
    apps, _ = load(a.tracker)
    for r in apps:
        if r.get("Status") != "not applied" and same_entry(me, role_entry(r.get("Company"), r.get("Title"), r.get("Link"))):
            print(json.dumps({"error": "already applied", "row": r.get("#"), "status": r.get("Status"),
                              "applied": r.get("Applied")}, indent=1))
            sys.exit(2)
    if any(same_entry(me, h) for h in held):
        print(json.dumps({"ok": True, "already_checked": True, **st}, indent=1)); return
    if held:
        h = held[0]
        print(json.dumps({"error": "another application is still open; CareerMate submits one at a time",
                          "open": f"{h.get('company')} | {h.get('title')} (checked {h.get('ts')})",
                          "next": "record it with tracker.py add once submitted, or free it with tracker.py apply-release",
                          **st}, indent=1))
        sys.exit(4)
    if st["remaining"] == 0:
        print(json.dumps({"error": "daily cap reached", "message": msg,
                          "next": "offer tracker.py queue for tomorrow; a queued role still needs a fresh yes", **st},
                         indent=1))
        sys.exit(3)
    write_event(a, "reserved", me, now, user_pick=a.user_pick or "")
    st["remaining"] -= 1
    st["open_checks"] += 1
    print(json.dumps({"ok": True, "slot": DAILY_CAP - st["remaining"], **st,
                      "next": "submit this one application, then tracker.py add (or apply-release if it was not sent)"},
                     indent=1))

def cmd_apply_release(a):
    now = now_dt(a)
    me = role_entry(a.company, a.title, a.link)
    _, held = day_usage(a, now)
    if not any(same_entry(me, h) for h in held):
        print(json.dumps({"error": "no open apply-check for this role today"})); sys.exit(2)
    write_event(a, "released", me, now, reason=(a.reason or "")[:160])
    _, _, st = cap_state(a, now)
    print(json.dumps({"released": f"{a.company} | {a.title}", **st}, indent=1))

def require_check(a, entry, now, note_reason):
    """Exit 3 unless this CareerMate submission had an apply-check today (or a stated reason it did not)."""
    _, held = day_usage(a, now)
    if any(same_entry(entry, h) for h in held):
        return ""
    if note_reason:
        return f"recorded without apply-check: {note_reason[:120]}"
    print(json.dumps({"error": "no apply-check for this role today",
                      "next": "run tracker.py apply-check --company ... --title ... before submitting. If the user "
                              "submitted it themselves, pass --by user. To record a submission that already happened "
                              "without a check, pass --no-check-reason \"...\""}, indent=1))
    sys.exit(3)

def queue_file(a):
    return os.path.join(a.home, "apply-queue.json")

def cmd_queue(a):
    p = queue_file(a)
    q = json.load(open(p)) if os.path.exists(p) else []
    now = now_dt(a)
    if a.remove:
        q = [x for i, x in enumerate(q, 1) if i not in set(a.remove)]
    elif a.company:
        if not a.title:
            sys.exit("queue needs --title: one named role per entry")
        e = role_entry(a.company, a.title, a.link)
        if not any(same_entry(e, x) for x in q):
            q.append({**e, "queued": now.date().isoformat(), "for": (now.date() + dt.timedelta(days=1)).isoformat(),
                      "note": (a.note or "")[:160]})
    if a.remove or a.company:
        json.dump(q, open(p, "w"), indent=1)
        try:
            os.chmod(p, 0o600)
        except OSError:
            pass
    due = [x for x in q if x.get("for", "") <= now.date().isoformat()]
    print(json.dumps({"queue": [{"n": i, "company": x["company"], "title": x["title"], "link": x["link"],
                                 "for": x.get("for"), "note": x.get("note", "")} for i, x in enumerate(q, 1)],
                      "due_today": len(due),
                      "reminder": "Queued roles are not approvals. Ask the user about each one by name before "
                                  "applying, and run apply-check for each."}, indent=1))

# ---------------------------------------------------------------- interviews

def iv_file(a):
    return os.path.join(a.home, "interviews.json")

def load_iv(a):
    p = iv_file(a)
    return json.load(open(p)) if os.path.exists(p) else {}

def save_iv(a, data):
    os.makedirs(a.home, exist_ok=True)
    json.dump(data, open(iv_file(a), "w"), indent=1)
    try:
        os.chmod(iv_file(a), 0o600)
    except OSError:
        pass

def iv_cell(items, tz):
    up = sorted((i for i in items if i.get("status") == "scheduled"), key=lambda i: i["at"])
    if not up:
        return ""
    i = up[0]
    s = parse_when(i["at"], tz).strftime("%Y-%m-%d %H:%M %Z") + f", {i['duration']} min"
    return s + (f" ({i['round']})" if i.get("round") else "") + (f" +{len(up) - 1} more" if len(up) > 1 else "")

def iv_view(i, tz):
    v = dict(i)
    for k in ("at", "end", "checkin_at"):
        if v.get(k):
            v[k + "_local"] = show_dt(parse_when(v[k], tz))
    return v

def bump_stage(r, stage):
    new = norm_status(stage)
    old = r.get("Status", "")
    if old in TERMINAL or (new in STAGE and old in STAGE and STAGE[new] <= STAGE[old]):
        return False
    r["Status"] = new
    if new in FORWARD and STAGE.get(new, 0) > STAGE.get(r.get("Furthest stage", ""), 0):
        r["Furthest stage"] = new
    return True

def cmd_interview(a):
    apps, leads = load(a.tracker)
    r = pick(apps, a)
    now = now_dt(a)
    tz = now.tzinfo
    data = load_iv(a)
    items = data.setdefault(r["#"], [])
    up = [i for i in items if i.get("status") == "scheduled"]
    target = None
    if a.interview_id:
        target = next((i for i in items if i["id"] == a.interview_id), None)
        if not target:
            print(json.dumps({"error": f"no interview {a.interview_id} on row #{r['#']}"})); sys.exit(2)
    elif not a.new_round and (a.at or a.cancel or a.done or a.routine_id):
        if len(up) > 1:
            print(json.dumps({"error": "more than one upcoming interview on this row; pass --interview-id",
                              "interviews": [iv_view(i, tz) for i in up]}, indent=1)); sys.exit(2)
        target = up[0] if up else None
        if a.done and not target:
            past = [i for i in items if i.get("status") == "done"]
            target = past[-1] if past else None
    when = now.date().isoformat()
    out = {"row": r["#"], "company": r.get("Company"), "title": r.get("Title")}
    if a.cancel or a.done:
        if not target:
            print(json.dumps({"error": "no scheduled interview on this row", "interviews": items}, indent=1)); sys.exit(2)
        target.setdefault("history", []).append({"ts": now.isoformat(timespec="seconds"),
                                                 "change": "cancelled" if a.cancel else "done"})
        out["routine_to_delete"] = target.get("routine_id") or ""
        if a.cancel:
            target["status"] = "cancelled"
            append_note(r, f"interview on {target['at'][:16].replace('T', ' ')} cancelled" +
                        (f" ({a.note})" if a.note else ""), when)
            out["cancelled"] = iv_view(target, tz)
        else:
            target["status"] = "done"
            if a.summary:
                target["summary"] = a.summary[:200]
                append_note(r, f"interview{' (' + target['round'] + ')' if target.get('round') else ''}: "
                               f"{a.summary[:160]}", when)
            out["done"] = iv_view(target, tz)
        target["routine_id"] = ""
    elif a.at:
        start = parse_when(a.at, tz)
        dur = a.duration or (target["duration"] if target and target.get("duration") else DEFAULT_INTERVIEW_MIN)
        end = start + dt.timedelta(minutes=dur)
        checkin = end + dt.timedelta(minutes=CHECKIN_AFTER_MIN)
        fields = {"at": start.isoformat(timespec="minutes"), "duration": dur,
                  "duration_assumed": not a.duration and not (target and not target.get("duration_assumed")),
                  "end": end.isoformat(timespec="minutes"), "checkin_at": checkin.isoformat(timespec="minutes"),
                  "checkin_at_utc": checkin.astimezone(dt.timezone.utc).isoformat(timespec="minutes")}
        if target and target["at"] == fields["at"] and target["duration"] == dur:
            out["unchanged"] = True
            if a.routine_id:
                target["routine_id"] = a.routine_id
        elif target:
            old_at = target["at"]
            out["routine_to_replace"] = target.get("routine_id") or ""
            target.update(fields)
            target["routine_id"] = a.routine_id or ""
            target.setdefault("history", []).append({"ts": now.isoformat(timespec="seconds"),
                                                     "change": f"rescheduled from {old_at}"})
            append_note(r, f"interview moved from {old_at[:16].replace('T', ' ')} to "
                           f"{fields['at'][:16].replace('T', ' ')}", when)
            out["rescheduled"] = True
        else:
            target = {"id": f"{r['#']}-{len(items) + 1}", "round": a.round or "", **fields, "status": "scheduled",
                      "routine_id": a.routine_id or "", "source": a.source or "",
                      "history": [{"ts": now.isoformat(timespec="seconds"), "change": "added"}]}
            items.append(target)
            append_note(r, f"interview set for {fields['at'][:16].replace('T', ' ')}"
                           f"{' (' + a.round + ')' if a.round else ''}", when)
            out["added"] = True
        if a.round:
            target["round"] = a.round
        out["interview"] = iv_view(target, tz)
        out["checkin_in_past"] = checkin <= now
    elif a.routine_id:
        if not target:
            print(json.dumps({"error": "no scheduled interview on this row"})); sys.exit(2)
        target["routine_id"] = a.routine_id
        out["interview"] = iv_view(target, tz)
    else:
        out["interviews"] = [iv_view(i, tz) for i in items]
        print(json.dumps(out, indent=1)); return
    if a.stage and bump_stage(r, a.stage):
        out["status"] = r["Status"]
    r["Interview"] = iv_cell(items, tz)
    r["Last update"] = when
    save_iv(a, data)
    save(a.tracker, apps, leads)
    print(json.dumps(out, indent=1))

def cmd_interviews(a):
    apps, _ = load(a.tracker)
    now = now_dt(a)
    tz = now.tzinfo
    names = {r["#"]: (r.get("Company"), r.get("Title"), r.get("Status")) for r in apps}
    out = []
    for row, items in load_iv(a).items():
        for i in items:
            if a.all or i.get("status") == "scheduled":
                c, t, s = names.get(row, ("?", "?", "?"))
                out.append({"row": row, "company": c, "title": t, "status": s, **iv_view(i, tz),
                            "checkin_due": i.get("status") == "scheduled" and parse_when(i["checkin_at"], tz) <= now})
    print(json.dumps(sorted(out, key=lambda x: x["at"]), indent=1))

def cmd_wrapup(a):
    apps, _ = load(a.tracker)
    data = load_iv(a)
    sub = [r for r in apps if r.get("Status") != "not applied"]
    replied = [r for r in sub if r.get("Status") in FORWARD or r.get("Furthest stage") in FORWARD]
    iv_rows = {row for row, items in data.items() if any(i.get("status") in ("scheduled", "done") for i in items)}
    iv_rows |= {r["#"] for r in sub if STAGE.get(r.get("Furthest stage") or r.get("Status"), 0) >= 2}
    n_iv = sum(1 for items in data.values() for i in items if i.get("status") == "done")
    offers = [r for r in sub if r.get("Status") in ("offer", "accepted") or r.get("Furthest stage") in ("offer", "accepted")]
    keep = str(a.row) if a.row else ""
    active = [r for r in sub if r.get("Status") in ACTIVE and r["#"] != keep and r.get("Status") != "accepted"]
    print(json.dumps({"applications": len(sub), "replies_or_further": len(replied),
                      "roles_with_interviews": len(iv_rows), "interviews_held": n_iv, "offers": len(offers),
                      "active_processes": [{"row": r["#"], "company": r["Company"], "title": r["Title"],
                                            "status": r["Status"]} for r in active],
                      "upcoming_interviews": [{"row": row, **i} for row, items in data.items() for i in items
                                              if i.get("status") == "scheduled" and row != keep]}, indent=1))

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--home", default=HOME, help="data folder (default ~/careermate)")
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD), for tests")
    ap.add_argument("--now", help="override the current time (ISO, local if no offset), for tests")
    ap.add_argument("--tz", help="user's IANA time zone, e.g. America/New_York (default: $CAREERMATE_TZ, then the "
                                 "'Time zone:' line in search-preferences.md, then the system zone)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    def sp(name, fn, **kw):
        p = sub.add_parser(name, **kw); p.set_defaults(fn=fn); return p
    sp("init", cmd_init)
    p = sp("add", cmd_add)
    p.add_argument("--company", required=True); p.add_argument("--title", required=True)
    p.add_argument("--link"); p.add_argument("--source"); p.add_argument("--applied", help="YYYY-MM-DD")
    p.add_argument("--status", default="applied"); p.add_argument("--notes"); p.add_argument("--industry")
    p.add_argument("--size"); p.add_argument("--force", action="store_true")
    p.add_argument("--submitted-at", help="ISO time of the submission (default now when applied today)")
    p.add_argument("--by", choices=["careermate", "user"], default="careermate",
                   help="who submitted it; CareerMate submissions today need an apply-check first")
    p.add_argument("--no-check-reason", help="record a submission that already happened without an apply-check")
    for name, fn in (("update", cmd_update), ("note", cmd_note)):
        p = sp(name, fn)
        p.add_argument("--row", type=int); p.add_argument("--company", default=""); p.add_argument("--title")
        if name == "update":
            p.add_argument("--status"); p.add_argument("--force", action="store_true")
            p.add_argument("--by", choices=["careermate", "user"], default="careermate")
            p.add_argument("--no-check-reason")
        p.add_argument("--note", required=(name == "note")); p.add_argument("--date")
    p = sp("lead", cmd_lead)
    p.add_argument("--company", required=True); p.add_argument("--role"); p.add_argument("--source")
    p.add_argument("--note"); p.add_argument("--date")
    p = sp("find", cmd_find); p.add_argument("--company", required=True); p.add_argument("--title")
    p = sp("list", cmd_list); p.add_argument("--status"); p.add_argument("--json", action="store_true")
    p = sp("refresh", cmd_refresh); p.add_argument("--dry-run", action="store_true")
    p = sp("learn", cmd_learn); p.add_argument("--dry-run", action="store_true")
    p = sp("summary", cmd_summary); p.add_argument("--days", type=int, default=7)
    p = sp("email-seen", cmd_email_seen); p.add_argument("--id", required=True)
    p = sp("email-log", cmd_email_log)
    p.add_argument("--id", required=True); p.add_argument("--class", dest="cls", required=True,
                   choices=["application received", "rejection", "recruiter outreach", "interview scheduling", "offer",
                            "assessment request", "verification code", "other"])
    p.add_argument("--company"); p.add_argument("--row-ref"); p.add_argument("--summary"); p.add_argument("--date")
    p = sp("apply-check", cmd_apply_check, help="required before each submission; exit 3 at the daily cap")
    p.add_argument("--company", default=""); p.add_argument("--title"); p.add_argument("--link")
    p.add_argument("--user-pick", help="the user's words choosing this role, e.g. 'yes, apply to Acme'")
    p = sp("apply-release", cmd_apply_release, help="free an apply-check slot when the role was not submitted")
    p.add_argument("--company", required=True); p.add_argument("--title", required=True); p.add_argument("--link")
    p.add_argument("--reason")
    p = sp("queue", cmd_queue, help="save roles for tomorrow after the cap; never an approval")
    p.add_argument("--company", default=""); p.add_argument("--title"); p.add_argument("--link"); p.add_argument("--note")
    p.add_argument("--remove", type=int, nargs="+", help="queue numbers to remove")
    p = sp("interview", cmd_interview, help="record, reschedule, cancel or close out an interview")
    p.add_argument("--row", type=int); p.add_argument("--company", default=""); p.add_argument("--title")
    p.add_argument("--at", help="start time, ISO; no offset means the user's local time")
    p.add_argument("--duration", type=int, help=f"minutes (default {DEFAULT_INTERVIEW_MIN})")
    p.add_argument("--round", help="e.g. recruiter screen, hiring manager, panel")
    p.add_argument("--routine-id", help="id of the check-in routine created for this interview")
    p.add_argument("--interview-id"); p.add_argument("--new-round", action="store_true",
                                                     help="add another interview instead of moving the upcoming one")
    p.add_argument("--cancel", action="store_true"); p.add_argument("--done", action="store_true")
    p.add_argument("--summary", help="one line on how it went (with --done)")
    p.add_argument("--stage", help="move the status forward, e.g. 'screen scheduled' or 'interviewing'")
    p.add_argument("--source", help="where the time came from: email, invite, chat"); p.add_argument("--note")
    p = sp("interviews", cmd_interviews, help="upcoming interviews and check-ins")
    p.add_argument("--all", action="store_true")
    p = sp("wrapup", cmd_wrapup, help="totals and active processes, for 'I got the job'")
    p.add_argument("--row", type=int, help="the accepted role, left out of active processes")
    a = ap.parse_args()
    a.tracker = os.path.join(a.home, "applications-tracker.md")
    a.weights = os.path.join(a.home, "learned-weights.json")
    a.signals = os.path.join(a.home, "learned-signals.md")
    a.email_log = os.path.join(a.home, "tracker-email-log.json")
    a.keywords = os.path.join(a.home, "keywords.txt")
    if not getattr(a, "company", None):
        a.company = getattr(a, "company", "") or ""
    a.fn(a)

if __name__ == "__main__":
    main()
