#!/usr/bin/env python3
"""Search public Greenhouse/Ashby/Lever/Workable/SmartRecruiters boards listed in a CareerMate target-companies.md
for job titles containing any keyword phrase. Adapted from the batch pattern in CareerMate's skill.

Keywords are whole PHRASES, never split on commas, so "VP, Sales" stays one phrase. Pass them as repeatable
--keyword args and/or a --keywords-file (one phrase per line, or pipe-separated;
lines starting with # are comments). Matching is case-insensitive
and on whole words: punctuation and hyphens are treated as spaces and "&" as "and", so "VP, Sales" matches
"VP Sales Operations" and "full-stack" matches "Full Stack", but "people" does not match "PeopleSoft".
End a phrase with * for a prefix match on its last word ("recruit*" matches "Recruiter", "Recruiting").

Workday (OPT-IN, off by default): --include-workday also searches the public Workday career sites listed in
workday-companies.md. This checks public Workday job pages directly. Workday's site terms restrict automated
access, so it's offered as an optional, use-at-your-own-discretion feature. It runs slowly (about 1 request per
second overall), reads job listings only, and never logs in or applies.

Stdlib only. Prints JSON matches to stdout and a summary to stderr."""
import argparse, html, json, os, re, sys, threading, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
WORKDAY_UA = "CareerMate/1.1 (read-only public job listing search; about 1 request per second; never logs in or applies)"

def resolve_boards(path):
    """Use path when that file exists. Otherwise ~/careermate/target-companies.md, then the copy next to this script.
    A relative name such as target-companies.md therefore works from any working directory."""
    if path and os.path.isfile(path):
        return path
    for c in (os.path.expanduser("~/careermate/target-companies.md"),
              os.path.join(HERE, "target-companies.md")):
        if os.path.isfile(c):
            print(f"--- boards: {path} not found; using {c} ---", file=sys.stderr)
            return c
    raise SystemExit(
        f"search_boards.py: board list not found: {path} "
        f"(also checked ~/careermate/target-companies.md and {os.path.join(HERE, 'target-companies.md')})")

def parse_boards(path, exclude):
    boards, platform, section = [], None, ""
    for line in open(path, encoding="utf-8"):
        if line.startswith("## "):
            low = line.lower()
            platform = next((k for k in ("greenhouse", "ashby", "lever", "workable", "smartrecruiters") if k in low), None)
            section = line[3:].strip()
        elif line.startswith("### "):
            section = line[4:].strip()
        elif platform and line.startswith("| ") and not line.startswith("| Company") and not line.startswith("|--"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and re.fullmatch(r"[a-z0-9_\-]+", cells[1]):
                if any(e.lower() in section.lower() for e in exclude):
                    continue
                boards.append((platform, cells[1], cells[0]))
    return boards

def get(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "CareerMate/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

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

def load_phrases(args):
    phrases = list(args.keyword)
    for path in args.keywords_file:
        for line in open(path, encoding="utf-8"):
            if line.lstrip().startswith("#"):
                continue
            phrases.extend(x for x in line.split("|") if x.strip())
    return phrases

def list_jobs(board, want_text=False):
    """All jobs on one board as (row, text, labels). row has the same fields title mode has always returned.
    text is the plain description where the list API carries it (Greenhouse ?content=true, Ashby descriptionPlain,
    Lever descriptionPlain + lists, Workable ?details=true), else None (SmartRecruiters needs a per-job detail call).
    labels is extra department/function text used only for the loose title pass."""
    platform, tok, company = board
    out = []
    if platform == "greenhouse":
        q = "?content=true" if want_text else ""
        for j in get(f"https://boards-api.greenhouse.io/v1/boards/{tok}/jobs{q}", timeout=30 if want_text else 15).get("jobs", []):
            row = {"title": j.get("title", ""), "company": company, "location": (j.get("location") or {}).get("name", ""),
                   "url": j.get("absolute_url", ""), "platform": platform, "token": tok, "job_id": j.get("id"),
                   "updated_at": j.get("updated_at")}
            labels = " ".join(d.get("name") or "" for d in j.get("departments") or [])
            out.append((row, strip_html(j.get("content")) if want_text else None, labels))
    elif platform == "ashby":
        for j in get(f"https://api.ashbyhq.com/posting-api/job-board/{tok}", timeout=30 if want_text else 15).get("jobs", []):
            row = {"title": j.get("title", ""), "company": company, "location": j.get("location", ""),
                   "url": j.get("jobUrl") or f"https://jobs.ashbyhq.com/{tok}/{j.get('id','')}", "platform": platform,
                   "token": tok, "remote": j.get("isRemote"), "published_at": j.get("publishedAt")}
            out.append((row, (j.get("descriptionPlain") or strip_html(j.get("descriptionHtml"))) if want_text else None,
                        f"{j.get('department') or ''} {j.get('team') or ''}"))
    elif platform == "workable":
        q = "?details=true" if want_text else ""
        for j in get(f"https://apply.workable.com/api/v1/widget/accounts/{tok}{q}").get("jobs", []):
            loc = ", ".join(x for x in (j.get("city"), j.get("state"), j.get("country")) if x)
            row = {"title": j.get("title", ""), "company": company, "location": loc, "url": j.get("url") or j.get("shortlink", ""),
                   "platform": platform, "token": tok, "remote": j.get("telecommuting"), "published_at": j.get("published_on")}
            out.append((row, strip_html(j.get("description")) if want_text else None,
                        f"{j.get('department') or ''} {j.get('function') or ''}"))
    elif platform == "smartrecruiters":
        offset, total = 0, 1
        while offset < total and offset < 3000:
            d = get(f"https://api.smartrecruiters.com/v1/companies/{tok}/postings?limit=100&offset={offset}")
            total = d.get("totalFound", 0)
            content = d.get("content", [])
            if not content:
                break
            for j in content:
                l = j.get("location") or {}
                loc = ", ".join(x for x in (l.get("city"), l.get("region"), l.get("country")) if x)
                row = {"title": j.get("name", ""), "company": company, "location": loc,
                       "url": f"https://jobs.smartrecruiters.com/{tok}/{j.get('id','')}", "platform": platform,
                       "token": tok, "remote": l.get("remote"), "published_at": j.get("releasedDate")}
                labels = " ".join(str((j.get(k) or {}).get("label") or "") for k in ("department", "function", "industry"))
                out.append((row, None, labels))
            offset += 100
    else:
        data = get(f"https://api.lever.co/v0/postings/{tok}?mode=json")
        for j in data if isinstance(data, list) else []:
            row = {"title": j.get("text", ""), "company": company, "location": (j.get("categories") or {}).get("location", ""),
                   "url": j.get("hostedUrl", ""), "platform": platform, "token": tok, "created_at": j.get("createdAt")}
            text = None
            if want_text:
                text = " ".join([j.get("descriptionPlain") or ""] +
                                [f"{l.get('text','')}: {strip_html(l.get('content',''))}" for l in j.get("lists") or []] +
                                [j.get("additionalPlain") or ""]).strip()
            c = j.get("categories") or {}
            out.append((row, text, f"{c.get('team') or ''} {c.get('department') or ''}"))
    return out

def strip_html(h):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(html.unescape(h or "")))).strip()

def search(board, kws):
    """Title mode (default): rows whose title hits a phrase."""
    try:
        return [row for row, _, _ in list_jobs(board) if any(rx.search(norm(row["title"])) for _, rx in kws)], True
    except Exception:
        return [], False

def search_desc(board, kws, M, a):
    """Description mode, pass 1. Returns (survivors, ok, n_jobs, sr_unread). Each survivor row carries private
    _title_hit, _loose, _terms and _text keys. Only survivors keep their text."""
    platform, tok, _ = board
    try:
        jobs = list_jobs(board, want_text=True)
    except Exception:
        return [], False, 0, 0
    out, need_detail = [], []
    for row, text, labels in jobs:
        tn = norm(row["title"])
        th = any(rx.search(tn) for _, rx in kws)
        loose = sorted(w for w in set(tn.split()) | (set(norm(labels).split()) if platform == "smartrecruiters" else set())
                       if w in M["loose"])
        if text is None:
            if th or loose:
                need_detail.append((row, th, loose))
            continue
        terms = M["sm"].term_hits(norm(text), M["terms"])
        if terms:
            with M["lock"]:
                M["df"].update(terms)
        if th or loose or len(terms) >= a.min_term_hits:
            row.update(_title_hit=th, _loose=loose, _terms=terms, _text=text[:M["sm"].TEXT_KEEP])
            out.append(row)
    unread = 0
    if need_detail:  # SmartRecruiters: per-posting detail, title-hits first, capped per board, paced, cached by posting id
        need_detail.sort(key=lambda x: (not x[1], -len(x[2])))
        for i, (row, th, loose) in enumerate(need_detail):
            if i >= a.detail_cap_per_board and not th:
                unread += 1
                continue
            pid = row["url"].rstrip("/").split("/")[-1]
            key = f"smartrecruiters:{tok}:{pid}"
            text = M["cache"].get_desc(key)
            if text is None:
                time.sleep(a.detail_interval)
                try:
                    x = get(f"https://api.smartrecruiters.com/v1/companies/{tok}/postings/{pid}")
                    text = " ".join(strip_html(v.get("text", "")) for v in ((x.get("jobAd") or {}).get("sections") or {}).values())
                    M["cache"].put_desc(key, text[:M["sm"].TEXT_KEEP])
                except Exception:
                    text = ""
            terms = M["sm"].term_hits(norm(text), M["terms"])
            row.update(_title_hit=th, _loose=loose, _terms=terms, _text=text[:M["sm"].TEXT_KEEP])
            out.append(row)
    return out, True, len(jobs), unread

# ---------------------------------------------------------------- Workday (opt-in)

def parse_workday(path, exclude):
    """Rows of workday-companies.md: | Company | Tenant | wdN | Site | Careers URL | ~Jobs |"""
    out, section = [], ""
    for line in open(path, encoding="utf-8"):
        if line.startswith("#"):
            section = line.lstrip("#").strip()
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if line.startswith("| ") and len(c) >= 4 and re.fullmatch(r"wd\d+", c[2]) and re.fullmatch(r"[A-Za-z0-9_\-]+", c[1]):
            if any(e.lower() in section.lower() for e in exclude):
                continue
            out.append({"company": c[0], "tenant": c[1], "wd": int(c[2][2:]), "site": c[3], "section": section})
    return out

class WorkdayClient:
    """Serial, globally paced, read-only client. Honors Retry-After; exponential backoff on 429/5xx."""
    BLOCK = {403, 429}
    def __init__(self, interval=1.0, max_retries=3, max_wait=60):
        self.interval, self.max_retries, self.max_wait = interval, max_retries, max_wait
        self.last, self.requests, self.blocked_responses = 0.0, 0, 0
        self.lock = threading.Lock()
    def _pace(self, extra=0.0):
        wait = self.last + self.interval + extra - time.time()
        if wait > 0:
            time.sleep(wait)
        self.last = time.time()
    def call(self, url, body=None):
        """Returns (kind, data): kind in ok | invalid | blocked."""
        with self.lock:
            delay = 0.0
            for attempt in range(self.max_retries + 1):
                self._pace(delay)
                self.requests += 1
                headers = {"User-Agent": WORKDAY_UA, "Accept": "application/json"}
                data = None
                if body is not None:
                    headers["Content-Type"] = "application/json"
                    data = json.dumps(body).encode()
                try:
                    with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=30) as r:
                        return "ok", json.loads(r.read().decode("utf-8", "replace"))
                except urllib.error.HTTPError as e:
                    code, ra = e.code, e.headers.get("Retry-After") if e.headers else None
                except Exception:
                    code, ra = 0, None
                if code in (400, 404, 410, 422):
                    return "invalid", code
                self.blocked_responses += code in self.BLOCK
                if attempt == self.max_retries:
                    return "blocked", code
                try:
                    delay = min(float(ra), self.max_wait) if ra else min(2.0 * 2 ** attempt, self.max_wait)
                except ValueError:
                    delay = min(2.0 * 2 ** attempt, self.max_wait)
            return "blocked", code

PAY = re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?\s?[kK]?(?:\s*(?:-|–|to)\s*\$?\s?\d[\d,]*(?:\.\d+)?\s?[kK]?)?")

def workday_detail(client, co, path):
    base = f"https://{co['tenant']}.wd{co['wd']}.myworkdayjobs.com/wday/cxs/{co['tenant']}/{co['site']}"
    kind, d = client.call(base + path)
    if kind != "ok":
        return {}
    i = d.get("jobPostingInfo") or {}
    text = re.sub(r"<[^>]+>", " ", i.get("jobDescription") or "")
    pay = [m.group(0).strip() for m in PAY.finditer(text) if re.search(r"\d{2,3}[,.]?\d{3}|\d+\s?[kK]", m.group(0))]
    return {"location": i.get("location"), "additional_locations": i.get("additionalLocations") or [],
            "remote_type": i.get("remoteType"), "time_type": i.get("timeType"), "start_date": i.get("startDate"),
            "pay_text": pay[:3], "job_req_id": i.get("jobReqId"), "_text": re.sub(r"\s+", " ", html.unescape(text)).strip()[:6000]}

def search_workday(companies, kws, terms, a, log=sys.stderr):
    """Each search term is sent as searchText; results are kept only if the title passes our phrase filter."""
    client = WorkdayClient(interval=a.workday_interval)
    stats = {"companies_planned": len(companies), "companies_searched": 0, "companies_blocked": [],
             "companies_invalid": [], "aborted": False}
    out, t0 = [], time.time()
    hit = lambda t: any(rx.search(norm(t)) for _, rx in kws)
    for idx, co in enumerate(companies, 1):
        attempted = stats["companies_searched"] + len(stats["companies_blocked"])
        if attempted >= 5 and len(stats["companies_blocked"]) / attempted > a.workday_block_ratio:
            stats["aborted"] = True
            print(f"  workday: stopping, {len(stats['companies_blocked'])}/{attempted} companies blocked", file=log)
            break
        host = f"https://{co['tenant']}.wd{co['wd']}.myworkdayjobs.com"
        url = f"{host}/wday/cxs/{co['tenant']}/{co['site']}/jobs"
        seen, consec, reqs, status = {}, 0, 0, "ok"
        for term in terms:
            offset, total = 0, None
            while reqs < a.workday_company_request_cap:
                kind, d = client.call(url, {"appliedFacets": {}, "limit": 20, "offset": offset, "searchText": term})
                reqs += 1
                if kind == "invalid":
                    status = "invalid"
                    break
                if kind == "blocked":
                    consec += 1
                    if consec >= 2:
                        status = "blocked"
                        break
                    continue
                consec = 0
                if total is None:
                    total = int(d.get("total") or 0)  # only the first page reports total
                page = d.get("jobPostings") or []
                page_hits = 0
                for j in page:
                    title = j.get("title") or ""
                    if title and hit(title):
                        page_hits += 1
                        u = host + "/en-US/" + co["site"] + (j.get("externalPath") or "")
                        if u not in seen:
                            bf = j.get("bulletFields") or []
                            seen[u] = {"title": title, "company": co["company"], "location": j.get("locationsText", ""),
                                       "url": u, "platform": "workday", "ats": "workday", "token": f"{co['tenant']}/{co['site']}",
                                       "tenant": co["tenant"], "wd": co["wd"], "site": co["site"], "section": co["section"],
                                       "job_id": bf[0] if bf else None, "posted_on": j.get("postedOn"),
                                       "external_path": j.get("externalPath")}
                offset += 20
                # Results are relevance-ranked: page further only while the total is above what we read,
                # the last page still produced phrase matches, and we stay under the per-term page cap.
                if offset >= min(total, 2000) or page_hits == 0 or offset >= 20 * a.workday_pages_per_term or not page:
                    break
            if status != "ok" or reqs >= a.workday_company_request_cap:
                break
        if status == "blocked":
            stats["companies_blocked"].append(co["company"])
        elif status == "invalid":
            stats["companies_invalid"].append(co["company"])
        else:
            stats["companies_searched"] += 1
        found = list(seen.values())
        if a.workday_details:
            for m in found[: a.workday_detail_cap_per_company]:
                m.update({k: v for k, v in workday_detail(client, co, m["external_path"]).items() if v})
        out.extend(found)
        print(f"  workday [{idx}/{len(companies)}] {co['company']}: {len(found)} matches, {reqs} requests, {status}"
              f" ({time.time()-t0:.0f}s, {client.requests} total requests)", file=log)
    stats.update({"requests": client.requests, "blocked_responses": client.blocked_responses,
                  "seconds": round(time.time() - t0, 1), "matches": len(out)})
    return out, stats

def score_rows(rows, M, a, st):
    """Pass 2: semantic_score, matched_terms, match_reason on rows that carry _text (others keep title reason only)."""
    sm, t_start = M["sm"], time.time()
    for r in rows:
        if "_terms" not in r:
            r["_terms"] = sm.term_hits(norm(r.get("_text") or ""), M["terms"]) if r.get("_text") else []
            r["_title_hit"] = True
    todo = [(i, r["title"], r["_text"]) for i, r in enumerate(rows) if r.get("_text")]
    try:
        sc = M["backend"].score(M["pieces"], todo, M["phrases"])
    except Exception as e:
        print(f"  semantic: {M['backend'].label} failed ({type(e).__name__}); using TF-IDF fallback", file=sys.stderr)
        M["backend"] = sm.TfIdf(); M["cutoff"] = a.semantic_min if a.semantic_min is not None else sm.DEFAULT_MIN["tfidf"]
        st["backend"], st["cutoff"] = "tfidf", M["cutoff"]
        sc = M["backend"].score(M["pieces"], todo, M["phrases"])
    for i, r in enumerate(rows):
        if i in sc:
            sem, d, t = sc[i]
            r["semantic_score"] = round(sem, 3)
            r["description_similarity"] = round(d, 3)
            if t is not None:
                r["title_similarity"] = round(t, 3)
        r["matched_terms"] = r["_terms"]
        desc_ok = r.get("semantic_score", -1) >= M["cutoff"] and (r["_terms"] or r.get("_loose"))
        r["match_reason"] = ("title+description" if desc_ok else "title") if r.get("_title_hit") else "description"
    st["seconds_score"] = round(st.get("seconds_score", 0) + time.time() - t_start, 1)

def run_description(boards, kws, a, t0):
    import semantic_match as sm
    terms_raw, pieces = sm.load_profile(a.profile)
    terms = sm.compile_terms(terms_raw)
    cache = sm.Cache(os.path.join(a.cache_dir, "match-cache.sqlite"))
    backend = sm.make_backend(a.embed_backend, a.embed_model or sm.DEFAULT_MODEL, cache, a.cache_dir)
    cutoff = a.semantic_min if a.semantic_min is not None else sm.DEFAULT_MIN[backend.name]
    M = {"sm": sm, "terms": terms, "phrases": [raw.rstrip("*") for raw, _ in kws], "pieces": pieces, "cache": cache, "backend": backend, "cutoff": cutoff,
         "loose": sm.loose_words([raw for raw, _ in kws]), "lock": threading.Lock(), "df": __import__("collections").Counter()}
    with ThreadPoolExecutor(a.workers) as ex:
        res4 = list(ex.map(lambda b: search_desc(b, kws, M, a), boards))
    surv = [m for r in res4 for m in r[0]]
    st = {"_M": M, "backend": backend.label, "cutoff": cutoff, "profile_terms": len(terms), "profile_sections": len(pieces),
          "boards": len(boards), "boards_ok": sum(1 for r in res4 if r[1]), "jobs_read": sum(r[2] for r in res4),
          "sr_unread": sum(r[3] for r in res4), "pass1": len(surv),
          "pass1_title": sum(1 for m in surv if m["_title_hit"]),
          "pass1_loose": sum(1 for m in surv if not m["_title_hit"] and m["_loose"]),
          "pass1_terms": sum(1 for m in surv if not m["_title_hit"] and not m["_loose"]),
          "seconds_fetch": round(time.time() - t0, 1)}
    # Terms that show up in a large share of all postings (company boilerplate such as "AI" tool names) do not count
    # toward the pass-1 description gate; they still show in matched_terms.
    common = {t for t, n in M["df"].items() if st["jobs_read"] and n / st["jobs_read"] > a.common_term_share}
    st["common_terms"] = sorted(common)
    def keep(m):
        return m["_title_hit"] or m["_loose"] or len([t for t in m["_terms"] if t not in common]) >= a.min_term_hits
    surv = [m for m in surv if keep(m)]
    st["pass1_after_common"] = len(surv)
    st.update(pass1_title=sum(1 for m in surv if m["_title_hit"]),
              pass1_loose=sum(1 for m in surv if not m["_title_hit"] and m["_loose"]),
              pass1_terms=sum(1 for m in surv if not m["_title_hit"] and not m["_loose"]))
    # Cheap pre-rank: TF-IDF against the profile, keep every title hit plus the best --prerank-keep others for the
    # embedding model. Embedding every survivor costs about 1 s per 40 postings on 8 CPU cores.
    if M["backend"].name != "tfidf" and a.prerank_keep and sum(1 for m in surv if not m["_title_hit"]) > a.prerank_keep:
        t1 = time.time()
        pre = sm.TfIdf()._desc(M["pieces"], [(i, m["title"], m["_text"]) for i, m in enumerate(surv) if not m["_title_hit"]])
        top = set(sorted(pre, key=lambda i: -pre[i])[: a.prerank_keep])
        surv = [m for i, m in enumerate(surv) if m["_title_hit"] or i in top]
        st["seconds_prerank"] = round(time.time() - t1, 1)
    st["pass2_scored"] = len(surv)
    if a.dump_pass1:  # testing aid: the scored survivors with text, for tuning cutoffs offline
        json.dump([{k: v for k, v in m.items()} for m in surv], open(a.dump_pass1, "w"))
    print(f"  description mode: {st['jobs_read']} jobs read from {st['boards_ok']}/{len(boards)} boards in {st['seconds_fetch']}s; "
          f"pass 1 kept {st['pass1']} ({st['pass1_after_common']} after ignoring {len(common)} common terms); "
          f"scoring {len(surv)} with {backend.label}", file=sys.stderr)
    score_rows(surv, M, a, st)
    st["backend"] = M["backend"].label
    title_rows = [m for m in surv if m["_title_hit"]]
    desc = sorted((m for m in surv if not m["_title_hit"] and m.get("semantic_score", -1) >= M["cutoff"]),
                  key=lambda m: -m["semantic_score"])
    st["description_above_cutoff"] = len(desc)
    desc = desc[: a.max_description_only]
    st.update(out_title=sum(1 for m in title_rows if m["match_reason"] == "title"),
              out_both=sum(1 for m in title_rows if m["match_reason"] == "title+description"), out_description=len(desc),
              embed_chunks=getattr(M["backend"], "stats", {}).get("chunks"), embed_cached=getattr(M["backend"], "stats", {}).get("cached"))
    res = [(None, r[1]) for r in res4]
    return title_rows + desc, res, st

def main():
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument("--boards", required=True,
                    help="target-companies.md. If that path is missing, use ~/careermate/target-companies.md, "
                         "then the copy next to this script")
    ap.add_argument("--keyword", action="append", default=[],
                    help='one title phrase, repeatable, e.g. --keyword "VP, Sales" --keyword "head of operations"')
    ap.add_argument("--keywords-file", action="append", default=[],
                    help="file of phrases, one per line or pipe-separated (commas stay inside a phrase); repeatable")
    ap.add_argument("--keywords", help=argparse.SUPPRESS)
    ap.add_argument("--exclude-section", action="append", default=[], help="skip a section/industry heading, repeatable")
    ap.add_argument("--workers", type=int, default=15)
    dm = ap.add_argument_group("Description matching (off unless --match description)")
    dm.add_argument("--match", choices=["title", "description"], default="title",
                    help="title (default, fast): phrase hits in job titles. description: also read every description and rank "
                         "by similarity to --profile, so roles with unusual titles can surface")
    dm.add_argument("--semantic", action="store_true", help="same as --match description")
    dm.add_argument("--profile", help="match profile file (skills, tools, outcomes, target problems); needed for --match description")
    dm.add_argument("--embed-backend", choices=["auto", "fastembed", "tfidf"], default="auto",
                    help="auto (default): local embedding model if fastembed is installed, else stdlib TF-IDF")
    dm.add_argument("--embed-model", default=None, help="fastembed model (default sentence-transformers/all-MiniLM-L6-v2)")
    dm.add_argument("--semantic-min", type=float, default=None,
                    help="similarity cutoff for description-only rows (default 0.45 fastembed, 0.12 tfidf)")
    dm.add_argument("--max-description-only", type=int, default=400, help="cap on description-only rows, best first (default 400)")
    dm.add_argument("--min-term-hits", type=int, default=2,
                    help="distinct profile terms a description needs to pass pass 1 without a title hit (default 2)")
    dm.add_argument("--common-term-share", type=float, default=0.05,
                    help="profile terms found in more than this share of all postings do not count toward --min-term-hits (default 0.05)")
    dm.add_argument("--prerank-keep", type=int, default=3000,
                    help="before the embedding model, keep the best N non-title survivors by TF-IDF (default 3000; 0 = embed all)")
    dm.add_argument("--detail-cap-per-board", type=int, default=40,
                    help="SmartRecruiters only: per-posting description fetches per board for loose-title jobs (default 40)")
    dm.add_argument("--detail-interval", type=float, default=0.25, help="seconds between SmartRecruiters detail calls per board (default 0.25)")
    dm.add_argument("--cache-dir", default=os.path.expanduser("~/.cache/careermate"),
                    help="embedding and description cache (default ~/.cache/careermate)")
    dm.add_argument("--with-text", action="store_true", help="include each row's plain description (first 6,000 characters) as `description`")
    dm.add_argument("--dump-pass1", help=argparse.SUPPRESS)
    dm.add_argument("--match-stats", help="write description-mode counts and timings to this JSON file")
    wd = ap.add_argument_group("Workday (opt-in; off unless --include-workday is given)")
    wd.add_argument("--include-workday", action="store_true",
                    help="also search public Workday career sites (slow, read-only; Workday's site terms restrict automated access)")
    wd.add_argument("--workday-companies", help="workday-companies.md (default: ~/careermate/workday-companies.md, else the sibling file)")
    wd.add_argument("--workday-max-companies", type=int, default=150, help="cap on Workday companies searched (default 150)")
    wd.add_argument("--workday-search", action="append", default=[],
                    help="searchText to send to Workday, repeatable (default: every --keyword phrase). Fewer, broader terms run faster; "
                         "results are still filtered by the --keyword phrases")
    wd.add_argument("--workday-interval", type=float, default=1.0, help="seconds between Workday requests overall (default 1.0, minimum 1.0)")
    wd.add_argument("--workday-pages-per-term", type=int, default=3, help="max 20-result pages per search term per company (default 3)")
    wd.add_argument("--workday-company-request-cap", type=int, default=40, help="max list requests per company (default 40)")
    wd.add_argument("--workday-block-ratio", type=float, default=0.20, help="stop Workday entirely if more than this share of companies block (default 0.20)")
    wd.add_argument("--workday-details", action="store_true", help="fetch each Workday match's detail page for pay text, locations and remote type")
    wd.add_argument("--workday-detail-cap-per-company", type=int, default=10)
    wd.add_argument("--workday-stats", help="write Workday run stats (requests, blocks, runtime) to this JSON file")
    a = ap.parse_args()
    a.workday_interval = max(1.0, a.workday_interval)
    if a.keywords is not None:
        ap.error("--keywords (comma-separated) was removed because it split phrases like 'VP, Sales'. "
                 "Use repeatable --keyword PHRASE or --keywords-file FILE (one phrase per line or pipe-separated).")
    kws = compile_phrases(load_phrases(a))
    if not kws:
        ap.error("give at least one --keyword or --keywords-file")
    boards = parse_boards(resolve_boards(a.boards), a.exclude_section)
    wd_result = {}
    wd_thread = None
    if a.include_workday:
        wpath = a.workday_companies or next((p for p in (os.path.expanduser("~/careermate/workday-companies.md"),
                                                          os.path.join(HERE, "workday-companies.md")) if os.path.exists(p)), None)
        if not wpath:
            ap.error("--include-workday needs workday-companies.md (pass --workday-companies PATH)")
        companies = parse_workday(wpath, a.exclude_section)[: a.workday_max_companies]
        terms = list(dict.fromkeys(t.strip() for t in (a.workday_search or [raw.rstrip("*") for raw, _ in kws]) if t.strip()))
        print(f"--- WORKDAY (opt-in): {len(companies)} companies x {len(terms)} search terms from {wpath}; "
              f"paced at {a.workday_interval:.1f}s/request, est. {len(companies)*len(terms)*a.workday_interval/60:.0f}-{len(companies)*len(terms)*a.workday_interval*1.5/60:.0f} min ---", file=sys.stderr)
        def run_wd():
            wd_result["matches"], wd_result["stats"] = search_workday(companies, kws, terms, a)
        wd_thread = threading.Thread(target=run_wd)
        wd_thread.start()
    t0 = time.time()
    desc_mode = a.match == "description" or a.semantic
    if desc_mode and not (a.profile and os.path.exists(a.profile)):
        print(f"--- description mode needs --profile FILE ({a.profile or 'not given'} not found); running title mode ---", file=sys.stderr)
        desc_mode = False
    if not desc_mode:
        with ThreadPoolExecutor(a.workers) as ex:
            res = list(ex.map(lambda b: search(b, kws), boards))
        matches = [m for r, _ in res for m in r]
        dstats = None
    else:
        matches, res, dstats = run_description(boards, kws, a, t0)
    if wd_thread:
        wd_thread.join()
        wdm = wd_result.get("matches", [])
        if desc_mode and wdm:
            score_rows(wdm, dstats["_M"], a, dstats)
        matches += wdm
    for m in matches:
        n = norm(m["title"])
        m["matched"] = [raw for raw, rx in kws if rx.search(n)]
    ok = sum(1 for _, s in res if s)
    if dstats:
        M = dstats.pop("_M")
        M["cache"].close()
        for m in matches:
            if a.with_text and m.get("_text"):
                m["description"] = m["_text"]
        dstats["seconds_total"] = round(time.time() - t0, 1)
        if a.match_stats:
            json.dump(dstats, open(a.match_stats, "w"), indent=2)
    matches = [{k: v for k, v in m.items() if not k.startswith("_")} for m in matches]
    print(json.dumps(matches, indent=2))
    print(f"--- PHRASES: {len(kws)} | SEARCHED: {len(boards)} boards ({ok} reachable) | MATCHED: {len(matches)} roles"
          f" | {round(time.time() - t0)}s ---", file=sys.stderr)
    if dstats:
        print(f"--- DESCRIPTION MODE ({dstats['backend']}): {dstats['jobs_read']} jobs read | pass 1 kept {dstats['pass1_after_common']} "
              f"(title {dstats['pass1_title']}, loose title {dstats['pass1_loose']}, description terms {dstats['pass1_terms']}) | "
              f"scored {dstats['pass2_scored']} | output: {dstats['out_title']} title, {dstats['out_both']} title+description, {dstats['out_description']} description-only "
              f"(cutoff {dstats['cutoff']}) | fetch {dstats['seconds_fetch']}s, score {dstats['seconds_score']}s"
              f"{' | SmartRecruiters jobs not read: ' + str(dstats['sr_unread']) if dstats['sr_unread'] else ''} ---", file=sys.stderr)
    if wd_result.get("stats"):
        st = wd_result["stats"]
        print(f"--- WORKDAY: {st['companies_searched']}/{st['companies_planned']} companies searched | "
              f"{len(st['companies_blocked'])} blocked | {len(st['companies_invalid'])} invalid | {st['requests']} requests | "
              f"{st['blocked_responses']} 403/429 responses | {st['seconds']}s | MATCHED: {st['matches']}"
              f"{' | ABORTED (block ratio)' if st['aborted'] else ''} ---", file=sys.stderr)
        if a.workday_stats:
            json.dump(st, open(a.workday_stats, "w"), indent=2)

if __name__ == "__main__":
    main()
