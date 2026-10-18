#!/usr/bin/env python3
"""Fetch one job posting for a CareerMate fit check or interview prep. Stdlib only.

  python3 fetch_posting.py --url "https://job-boards.greenhouse.io/acme/jobs/123" > /tmp/cm_posting.json
  python3 fetch_posting.py --text-file /tmp/pasted_jd.txt                       # text the user pasted
  python3 fetch_posting.py --url "<company site link with ?gh_jid=...>" --token acme   # Greenhouse board token if known

Uses the public ATS posting APIs (Greenhouse, Ashby, Lever, Workable, SmartRecruiters), the same ones the live
board search uses, and falls back to the page itself (schema.org JobPosting data, else page text). Workday links
are read only with --allow-workday (the user's saved Workday yes, or a yes for this one link).

Output JSON: ok, url, platform, company, title, location, workplace, remote, posted, pay_text, pay_top_usd,
agency_signals, text (plain description, first 15,000 characters), text_chars, note. Pay and location are only
what the posting states; missing stays missing. ok is false when the posting could not be read or the text is too
short to judge (usually a page that needs JavaScript): ask the user to paste the job description.
"""
import argparse, html, json, re, sys, urllib.error, urllib.parse, urllib.request

UA = "CareerMate/1.1 (reads one public job posting at the user's request; never logs in or applies)"
MIN_TEXT = 400

def get(url, data=None, accept="application/json", timeout=20):
    headers = {"User-Agent": UA, "Accept": accept}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode("utf-8", "replace")
    return json.loads(body) if accept == "application/json" else body

def strip_html(h):
    h = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", h or "")
    h = re.sub(r"(?i)<br\s*/?>|</(p|li|h[1-6]|div)>", "\n", h)
    t = re.sub(r"<[^>]+>", " ", html.unescape(html.unescape(h)))
    return "\n".join(" ".join(l.split()) for l in t.splitlines() if l.strip())

PAYRX = re.compile(r"([$£€])\s?(\d[\d,]*(?:\.\d+)?)\s?([kK])?(?:\s*(?:-|–|—|to)\s*[$£€]?\s?(\d[\d,]*(?:\.\d+)?)\s?([kK])?)?")

def pay_from_text(text):
    """(top USD per year or None, text as shown). Skips hourly figures and non-USD amounts."""
    tops, shown = [], []
    for m in PAYRX.finditer(text or ""):
        if re.search(r"hour|/hr|per hr|/h\b", (text or "")[m.end(): m.end() + 20].lower()) or m.group(1) != "$":
            continue
        vals = [float(n.replace(",", "")) * (1000 if k else 1) for n, k in ((m.group(2), m.group(3)), (m.group(4), m.group(5))) if n]
        vals = [v for v in vals if v >= 20000]
        if vals:
            tops.append(max(vals)); shown.append(m.group(0).strip())
    return (max(tops), shown[0]) if tops else (None, "")

def money(v):
    return f"${v / 1000:,.0f}K" if v else ""

AGENCY_TEXT = [r"\bstaffing (agency|firm|company|partner)\b", r"\bour client\b", r"\bon behalf of (our|a|an) client\b",
               r"\brecruit(ing|ment) (agency|firm)\b", r"\bcontract[- ]to[- ]hire\b", r"\bcorp[- ]to[- ]corp\b|\bc2c\b",
               r"\bw-?2 contract\b", r"\bconfidential (client|company|search)\b", r"\bplacement (agency|firm)\b"]
AGENCY_NAME = r"\b(staffing|personnel|recruit(ing|ment|ers)?|search partners|talent solutions|workforce solutions)\b"

def agency_signals(company, text):
    out = []
    if company and re.search(AGENCY_NAME, company, re.I):
        out.append(f'company name "{company}" sounds like a staffing or search firm')
    for rx in AGENCY_TEXT:
        m = re.search(rx, text or "", re.I)
        if m:
            out.append(f'posting says "{m.group(0)}"')
    return out

def greenhouse(tok, jid):
    x = get(f"https://boards-api.greenhouse.io/v1/boards/{tok}/jobs/{jid}?pay_transparency=true")
    d = {"platform": "greenhouse", "company": x.get("company_name") or tok, "title": x.get("title"),
         "location": (x.get("location") or {}).get("name"), "posted": x.get("first_published") or x.get("updated_at"),
         "text": strip_html(x.get("content")), "url_api": x.get("absolute_url")}
    ranges = [r for r in x.get("pay_input_ranges") or [] if (r.get("currency_type") or "USD") == "USD"]
    if ranges:
        top = max((r.get("max_cents") or 0) for r in ranges) / 100
        lo = min((r.get("min_cents") or 0) for r in ranges) / 100
        d.update(pay_top_usd=top, pay_text=f"{money(lo)}-{money(top)}" + (" (varies by location)" if len(ranges) > 1 else ""))
    return d

def ashby(slug, pid):
    jobs = get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true").get("jobs", [])
    x = next((j for j in jobs if pid in (j.get("jobUrl") or "") or j.get("id") == pid), None)
    if not x:
        raise LookupError("posting not on the board (it may have closed)")
    comp = x.get("compensation") or {}
    d = {"platform": "ashby", "company": slug, "title": x.get("title"), "workplace": x.get("workplaceType"),
         "location": "; ".join(l for l in [x.get("location")] + [s.get("location") for s in x.get("secondaryLocations") or []] if l),
         "remote": x.get("isRemote"), "posted": x.get("publishedAt"), "text": x.get("descriptionPlain") or strip_html(x.get("descriptionHtml"))}
    sal = [c for c in comp.get("summaryComponents") or [] if c.get("compensationType") == "Salary"
           and (c.get("currencyCode") or "USD") == "USD" and c.get("maxValue")]
    if sal:
        d.update(pay_top_usd=max(c["maxValue"] for c in sal),
                 pay_text=comp.get("scrapeableCompensationSalarySummary") or comp.get("compensationTierSummary"))
    elif comp.get("compensationTierSummary"):
        d["pay_text"] = comp["compensationTierSummary"]
    return d

def lever(slug, pid):
    x = get(f"https://api.lever.co/v0/postings/{slug}/{pid}?mode=json")
    text = "\n".join([x.get("descriptionPlain") or ""] + [f"{l.get('text', '')}:\n{strip_html(l.get('content', ''))}"
                                                           for l in x.get("lists") or []] + [x.get("additionalPlain") or ""])
    c = x.get("categories") or {}
    d = {"platform": "lever", "company": slug, "title": x.get("text"), "location": c.get("location"),
         "workplace": x.get("workplaceType"), "posted": x.get("createdAt"), "text": text.strip()}
    sr = x.get("salaryRange") or {}
    if sr.get("max") and (sr.get("currency") or "USD") == "USD":
        d.update(pay_top_usd=float(sr["max"]), pay_text=f"{money(sr.get('min'))}-{money(sr['max'])} ({sr.get('interval', '')})")
    return d

def workable(slug, code):
    for j in get(f"https://apply.workable.com/api/v1/widget/accounts/{slug}?details=true").get("jobs", []):
        if code.lower() in (j.get("url") or "").lower() or code.lower() in (j.get("shortlink") or "").lower() or j.get("shortcode") == code:
            loc = ", ".join(x for x in (j.get("city"), j.get("state"), j.get("country")) if x)
            return {"platform": "workable", "company": slug, "title": j.get("title"), "location": loc,
                    "remote": j.get("telecommuting"), "posted": j.get("published_on"), "text": strip_html(j.get("description"))}
    raise LookupError("posting not on the board (it may have closed)")

def smartrecruiters(co, pid):
    x = get(f"https://api.smartrecruiters.com/v1/companies/{co}/postings/{pid}")
    l = x.get("location") or {}
    secs = ((x.get("jobAd") or {}).get("sections") or {})
    text = "\n".join(f"{v.get('title', '')}\n{strip_html(v.get('text', ''))}" for v in secs.values() if v)
    return {"platform": "smartrecruiters", "company": (x.get("company") or {}).get("name") or co, "title": x.get("name"),
            "location": ", ".join(v for v in (l.get("city"), l.get("region"), l.get("country")) if v),
            "remote": l.get("remote"), "posted": x.get("releasedDate"), "text": text.strip()}

def workday(tenant, wd, site, path):
    x = get(f"https://{tenant}.{wd}.myworkdayjobs.com/wday/cxs/{tenant}/{site}{path}")
    i = x.get("jobPostingInfo") or {}
    return {"platform": "workday", "company": ((x.get("hiringOrganization") or {}).get("name")) or tenant,
            "title": i.get("title"), "location": "; ".join([i.get("location") or ""] + list(i.get("additionalLocations") or [])).strip("; "),
            "remote": bool(re.search(r"remote", i.get("remoteType") or "", re.I)) or None, "posted": i.get("startDate"),
            "text": strip_html(i.get("jobDescription"))}

def from_page(url):
    page = get(url, accept="text/html,application/xhtml+xml", timeout=25)
    for blob in re.findall(r'(?is)<script[^>]+application/ld\+json[^>]*>(.*?)</script>', page):
        try:
            data = json.loads(blob.strip())
        except ValueError:
            continue
        for item in data if isinstance(data, list) else data.get("@graph", [data]) if isinstance(data, dict) else []:
            if isinstance(item, dict) and "JobPosting" in str(item.get("@type")):
                org = item.get("hiringOrganization") or {}
                locs = item.get("jobLocation") or []
                locs = locs if isinstance(locs, list) else [locs]
                addr = ["; ".join(filter(None, [((l.get("address") or {}) if isinstance(l, dict) else {}).get(k)
                                                for k in ("addressLocality", "addressRegion", "addressCountry")])) for l in locs]
                d = {"platform": "page (JobPosting data)", "company": org.get("name") if isinstance(org, dict) else org,
                     "title": item.get("title"), "location": " | ".join(a for a in addr if a),
                     "remote": item.get("jobLocationType") == "TELECOMMUTE" or None, "posted": item.get("datePosted"),
                     "text": strip_html(item.get("description"))}
                bs = item.get("baseSalary") or {}
                v = bs.get("value") if isinstance(bs, dict) else None
                if isinstance(v, dict) and (bs.get("currency") or "USD") == "USD" and (v.get("maxValue") or v.get("value")):
                    unit = (v.get("unitText") or "YEAR").upper()
                    top = float(v.get("maxValue") or v.get("value"))
                    d["pay_text"] = f"{money(v.get('minValue'))}-{money(top)} per {unit.lower()}" if unit == "YEAR" else f"${top:,.2f} per {unit.lower()}"
                    if unit == "YEAR":
                        d["pay_top_usd"] = top
                return d, page
    t = re.search(r"(?is)<title[^>]*>(.*?)</title>", page)
    return {"platform": "page text", "title": strip_html(t.group(1)) if t else "", "text": strip_html(page)}, page

def gh_token_guesses(url):
    """Greenhouse board tokens worth trying for a company-site link: the site name, then board-list tokens whose
    company or token starts with it (sibling or user copy of target-companies.md)."""
    import os
    host = urllib.parse.urlparse(url).netloc.lower().split(":")[0]
    parts = [p for p in host.split(".") if p not in ("www", "careers", "jobs", "com", "io", "co", "ai", "org", "net")]
    stem = re.sub(r"[^a-z0-9]", "", parts[0]) if parts else ""
    if not stem:
        return []
    out = [stem]
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (os.path.expanduser("~/careermate/target-companies.md"),
              os.path.join(here, "..", "live-ats-board-search", "target-companies.md")):
        if not os.path.exists(p):
            continue
        gh = False
        for line in open(p, encoding="utf-8"):
            if line.startswith("## "):
                gh = "greenhouse" in line.lower()
            elif gh and line.startswith("| "):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) >= 2:
                    comp, tok = re.sub(r"[^a-z0-9]", "", cells[0].lower()), cells[1].strip("` ").lower()
                    if tok and (tok.startswith(stem) or comp.startswith(stem) or stem.startswith(tok)) and tok not in out:
                        out.append(tok)
    return out

def route(url, token=None, allow_workday=False):
    u = url.strip()
    low = u.lower()
    q = urllib.parse.parse_qs(urllib.parse.urlparse(u).query)
    m = re.search(r"greenhouse\.io/(?:embed/job_app\?for=)?([a-z0-9_\-]+)/jobs/(\d+)", low)
    if m and m.group(1) not in ("embed",):
        return greenhouse(m.group(1), m.group(2))
    if "greenhouse.io/embed/job_app" in low and q.get("for") and q.get("token"):
        return greenhouse(q["for"][0], q["token"][0])
    if q.get("gh_jid"):
        tok = token
        if not tok:
            try:
                page = get(u, accept="text/html", timeout=25)
                f = re.search(r"greenhouse\.io/(?:embed/job_board/js\?for=|embed/job_app\?for=|v1/boards/)?([a-z0-9_\-]+)", page.lower())
                f2 = re.search(r"[?&]for=([a-z0-9_\-]+)", page.lower())
                tok = (f2 or f).group(1) if (f2 or f) else None
            except Exception:
                tok = None
        cands = [tok] if tok and tok not in ("embed", "job-boards", "boards") else []
        for c in cands + [c for c in gh_token_guesses(u) if c not in cands][:6]:
            try:
                return greenhouse(c, q["gh_jid"][0])
            except Exception:
                continue
    m = re.search(r"jobs\.ashbyhq\.com/([^/?#]+)/([0-9a-f\-]{36})", low)
    if m:
        return ashby(m.group(1), m.group(2))
    m = re.search(r"jobs\.(?:eu\.)?lever\.co/([^/?#]+)/([0-9a-f\-]{36})", low)
    if m:
        return lever(m.group(1), m.group(2))
    m = re.search(r"apply\.workable\.com/([^/?#]+)/j/([0-9a-z]+)", low)
    if m:
        return workable(m.group(1), m.group(2))
    m = re.search(r"jobs\.smartrecruiters\.com/([^/?#]+)/(\d+)", u)
    if m:
        return smartrecruiters(m.group(1), m.group(2))
    m = re.search(r"https?://([a-z0-9\-]+)\.(wd\d+)\.myworkdayjobs\.com/(?:[a-z]{2}-[a-z]{2}/)?([^/?#]+)(/job/[^?#]+)", u, re.I)
    if m:
        if not allow_workday:
            raise PermissionError("Workday link: read it only with the user's Workday yes (--allow-workday), "
                                  "or ask them to paste the job description")
        return workday(m.group(1).lower(), m.group(2).lower(), m.group(3), m.group(4))
    m = re.search(r"/(\d{7,11})(?:[/?#]|$)", u)
    if m and not q.get("gh_jid"):     # company sites often show Greenhouse jobs under the Greenhouse job id
        for c in ([token] if token else []) + gh_token_guesses(u)[:4]:
            try:
                return greenhouse(c, m.group(1))
            except Exception:
                continue
    d = from_page(u)[0]
    if q.get("gh_jid") and d.get("platform") == "page text":
        d["note"] = ("this company site loads its Greenhouse posting with JavaScript and the board token could not be "
                     "found; pass --token if you know it, or ask the user to paste the job description")
    return d

JD_WORDS = r"responsibilit|requirement|qualification|what you.ll do|you will|experience with|years of|about the role|who you are"

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url"); ap.add_argument("--text-file", help="job description text the user pasted")
    ap.add_argument("--token", help="Greenhouse board token for company-site links with ?gh_jid=")
    ap.add_argument("--allow-workday", action="store_true")
    ap.add_argument("--company"); ap.add_argument("--title")
    a = ap.parse_args()
    if not a.url and not a.text_file:
        ap.error("give --url or --text-file")
    out = {"ok": False, "url": a.url or "", "note": ""}
    try:
        if a.text_file:
            d = {"platform": "pasted text", "text": open(a.text_file, encoding="utf-8").read().strip()}
        else:
            d = route(a.url, a.token, a.allow_workday)
        out.update({k: v for k, v in d.items() if v not in (None, "")})
    except PermissionError as e:
        out["note"] = str(e)
    except urllib.error.HTTPError as e:
        out["note"] = f"could not read the posting (HTTP {e.code}); it may have closed. Ask the user to paste the text."
    except Exception as e:
        out["note"] = f"could not read the posting ({type(e).__name__}: {str(e)[:120]}). Ask the user to paste the text."
    if a.company:
        out["company"] = a.company
    if a.title:
        out["title"] = a.title
    text = out.get("text", "")
    if text and not out.get("pay_text"):
        top, shown = pay_from_text(text)
        if top:
            out.update(pay_top_usd=top, pay_text=shown + " (from the description)")
    out["agency_signals"] = agency_signals(out.get("company", ""), text)
    if out.get("platform") == "page text":
        jd_hits = len(set(m.group(0).lower() for m in re.finditer(JD_WORDS, text, re.I)))
        if jd_hits < 2 or len(text) < 3 * MIN_TEXT:
            out["note"] = out.get("note") or ("the page did not contain a readable job description (it may need "
                                              "JavaScript). Ask the user to paste the job description.")
            text = ""
    out["text_chars"] = len(text)
    out["text"] = text[:15000]
    if text and len(text) >= MIN_TEXT:
        out["ok"] = True
    elif not out["note"]:
        out["note"] = "the page had too little readable text (it may need JavaScript). Ask the user to paste the job description."
    if out["ok"] and out.get("platform") == "page text" and not out["note"]:
        out["note"] = "read from the page text, not an ATS record: title, pay and location may be missing or mixed with page chrome."
    print(json.dumps(out, indent=1))
    sys.exit(0 if out["ok"] else 1)

if __name__ == "__main__":
    main()
