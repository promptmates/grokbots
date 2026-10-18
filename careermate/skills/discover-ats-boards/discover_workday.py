#!/usr/bin/env python3
"""
CareerMate Workday tenant discovery (opt-in feature).

Finds a company's public Workday career site (tenant, wdN data center, site name), verifies it with
one read-only CXS request, and optionally appends it to workday-companies.md.

Disclaimer: this checks public Workday job pages directly. Workday's site terms restrict automated
access, so Workday support is an optional, use-at-your-own-discretion feature. This script reads
public pages only, never logs in or applies, and paces its requests.

Order of attempts per company:
  1. Careers-page link sniffing: fetch the careers URL you pass (or a few common careers URLs built
     from the company name) and look for *.wdN.myworkdayjobs.com/<site> links.
  2. Pattern guess: tenant slugs from the name x wd1-wd12 (plus any --wd-extra), reading each host's
     robots.txt, which lists the public site names. If robots.txt lists none, try common site names.
  3. Verify: one POST to /wday/cxs/<tenant>/<site>/jobs (limit 1); keep the site with the most jobs.

Usage:
  python3 discover_workday.py --company "Zendesk"
  python3 discover_workday.py --company "Flex|flextronics"            # name|slug hint(s), comma-separated
  python3 discover_workday.py --company "Acme" --careers-url https://www.acme.com/careers
  python3 discover_workday.py --file companies.txt --append ~/careermate/workday-companies.md --section "Tech"
  python3 discover_workday.py --url https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite
File lines: "Company", "Company|slug1,slug2", or "Company|slug|wdN" (# comments allowed).
Stdlib only, Python 3.8+.
"""
import argparse, json, re, sys, threading, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = "CareerMate/1.1 (read-only public job listing search; low request rate)"
WD_DEFAULT = list(range(1, 13))
COMMON_SITES = ["External", "Careers", "careers", "External_Careers", "ExternalCareerSite",
                "External_Career_Site", "{T}", "{T}Careers", "{T}_Careers", "{T}External", "jobs", "Search"]
BAD_SITE = re.compile(r"(agency|intern(al)?\b|incumbent|employee|referr|contingent|alumni|internal|"
                      r"staffing|vendor|test|sandbox|impl|naukri|_emp|emp_|current)", re.I)
# Sites that are real but narrow (campus, early careers, agency feeds, private/confidential): keep as last resort.
LOW_SITE = re.compile(r"(early|campus|univ|student|graduate|newgrad|futureforce|broadbean|equest|private|"
                      r"confidential|college|faculty|immigration|sourced|scholarship|event|conversion|contractor)", re.I)
WD_LINK = re.compile(r"https?://([a-z0-9-]+)\.wd(\d+)\.myworkdayjobs\.com/(?:[a-z]{2}-[A-Z]{2}/)?([A-Za-z0-9_\-]+)")

_lock = threading.Lock()
_last = [0.0]
def pace(min_interval):
    with _lock:
        wait = _last[0] + min_interval - time.time()
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()

def http(url, data=None, timeout=12, min_interval=0.25, accept="application/json"):
    """Returns (status, body_text). Never raises."""
    pace(min_interval)
    headers = {"User-Agent": UA, "Accept": accept}
    if data is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""

def cxs_total(tenant, wd, site, min_interval=0.25):
    """One read-only CXS request. Returns job total (int) or None if the site is not valid."""
    url = f"https://{tenant}.wd{wd}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
    st, body = http(url, {"appliedFacets": {}, "limit": 1, "offset": 0, "searchText": ""}, min_interval=min_interval)
    if st != 200:
        return None
    try:
        d = json.loads(body)
        return int(d.get("total") or 0) if "jobPostings" in d else None
    except Exception:
        return None

def robots_sites(tenant, wd, min_interval=0.25):
    """None if the host is not a Workday tenant; else (allowed_sites, disallowed_sites) from robots.txt."""
    st, body = http(f"https://{tenant}.wd{wd}.myworkdayjobs.com/robots.txt", min_interval=min_interval, accept="text/plain")
    if st != 200 or "User-agent" not in body:
        return None
    disallow = {d for d in re.findall(r"Disallow:\s*/([^/\s]+)/", body) if d != "refreshFacet"}
    sites = []
    for s in re.findall(r"(?:Allow:\s*/|myworkdayjobs\.com/)([^/\s]+)/", body):
        if s not in disallow and s not in sites and s != "refreshFacet":
            sites.append(s)
    return sites, disallow

def robots_allows(tenant, wd, site, min_interval=0.25):
    """True unless the tenant's robots.txt disallows this site (or the host is not a tenant)."""
    r = robots_sites(tenant, wd, min_interval)
    if r is None:
        return False
    allowed, disallowed = r
    return site.lower() not in {d.lower() for d in disallowed}

def slugs_for(name):
    base = re.sub(r"\(.*?\)", "", name).lower().replace("&", "and")
    words = re.findall(r"[a-z0-9]+", base)
    drop = {"inc", "corp", "corporation", "company", "co", "llc", "ltd", "plc", "group", "holdings", "the"}
    core = [w for w in words if w not in drop] or words
    out = []
    for s in ("".join(core), "-".join(core), core[0] if core else "", "".join(words)):
        if s and s not in out:
            out.append(s)
    return out[:3]

def pick_sites(tenant, wd, sites, min_interval):
    """Verify candidate sites; return [(site, total)] sorted best first."""
    good = [s for s in sites if not BAD_SITE.search(s)] or sites
    if not good:
        good = [s.replace("{T}", tenant) for s in COMMON_SITES]
    found = []
    for s in good[:6]:
        t = cxs_total(tenant, wd, s, min_interval)
        if t is not None:
            found.append((s, t))
            if not sites and t > 0:
                break
    found.sort(key=lambda x: (x[1] > 0, not LOW_SITE.search(x[0]), x[1]), reverse=True)
    return found

def sniff(url, min_interval):
    st, body = http(url, timeout=15, min_interval=min_interval, accept="text/html")
    if st != 200:
        return []
    hits = []
    for t, wd, site in WD_LINK.findall(body):
        if site.lower() in ("wday", "en-us") or BAD_SITE.search(site):
            continue
        if (t, wd, site) not in hits:
            hits.append((t, wd, site))
    return hits

def discover(entry, careers_url=None, wd_list=None, min_interval=0.25, sniff_pages=True):
    parts = [p.strip() for p in entry.split("|")]
    name = parts[0]
    slugs = [s.strip() for s in parts[1].split(",")] if len(parts) > 1 and parts[1] else slugs_for(name)
    wds = [int(parts[2].lower().lstrip("wd"))] if len(parts) > 2 and parts[2] else []
    wds += [w for w in (wd_list or WD_DEFAULT) if w not in wds]
    # 1. sniff careers pages
    urls = [careers_url] if careers_url else []
    if sniff_pages and not careers_url and not (len(parts) > 2 and parts[2]):
        s0 = slugs_for(name)[0]
        urls += [f"https://www.{s0}.com/careers", f"https://careers.{s0}.com/"]
    for u in urls:
        for t, wd, site in sniff(u, min_interval):
            if not robots_allows(t, wd, site, min_interval):
                continue
            tot = cxs_total(t, wd, site, min_interval)
            if tot is not None:
                return {"company": name, "tenant": t, "wd": int(wd), "site": site, "jobs": tot, "method": "careers-page", "source": u}
    # 2. pattern guess via robots.txt, 3. verify via CXS
    for slug in slugs:
        for wd in wds:
            r = robots_sites(slug, wd, min_interval)
            if r is None:
                continue
            sites, disallowed = r
            if not sites and disallowed:
                return {"company": name, "tenant": None, "skipped": f"robots.txt disallows all sites on {slug}.wd{wd}"}
            found = pick_sites(slug, wd, sites, min_interval)
            if found:
                s, tot = found[0]
                return {"company": name, "tenant": slug, "wd": wd, "site": s, "jobs": tot, "method": "pattern",
                        "other_sites": [x for x, _ in found[1:]]}
            break  # tenant exists on this wd but no verifiable site; do not try other wd numbers
    return {"company": name, "tenant": None}

def from_url(url, min_interval=0.25):
    m = WD_LINK.search(url)
    if not m:
        return None
    t, wd, site = m.groups()
    if not robots_allows(t, wd, site, min_interval):
        print(f"  {url}: skipped (robots.txt disallows {site})", file=sys.stderr)
        return None
    tot = cxs_total(t, wd, site, min_interval)
    return {"company": t, "tenant": t, "wd": int(wd), "site": site, "jobs": tot, "method": "url"} if tot is not None else None

def row(r):
    url = f"https://{r['tenant']}.wd{r['wd']}.myworkdayjobs.com/en-US/{r['site']}"
    return f"| {r['company']} | {r['tenant']} | wd{r['wd']} | {r['site']} | {url} | {r['jobs']} |"

def load_existing(path):
    keys = set()
    try:
        for line in open(path, encoding="utf-8"):
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if len(c) >= 4 and c[2].startswith("wd"):
                keys.add((c[1].lower(), c[3].lower()))
    except FileNotFoundError:
        pass
    return keys

def append(path, rows, section):
    text = open(path, encoding="utf-8").read() if __import__("os").path.exists(path) else ""
    header = "| Company | Tenant | wdN | Site | Careers URL | ~Jobs |\n|---------|--------|-----|------|-------------|-------|\n"
    block = f"\n### {section}\n" + header + "\n".join(rows) + "\n"
    with open(path, "a", encoding="utf-8") as f:
        if not text:
            f.write("# Workday Companies\n\nOpt-in only (search_boards.py --include-workday).\n")
        f.write(block)

def main():
    ap = argparse.ArgumentParser(description="Discover public Workday career sites (opt-in).", allow_abbrev=False)
    ap.add_argument("--company", action="append", default=[], help='"Name" or "Name|slug1,slug2" or "Name|slug|wdN"; repeatable')
    ap.add_argument("--file", help="one company per line, same formats as --company")
    ap.add_argument("--url", action="append", default=[], help="a known myworkdayjobs.com URL to verify; repeatable")
    ap.add_argument("--careers-url", help="company careers page to sniff for Workday links (single --company only)")
    ap.add_argument("--wd-extra", default="", help="extra wd numbers to try, comma-separated (e.g. 100,103,108)")
    ap.add_argument("--no-sniff", action="store_true", help="skip guessing careers-page URLs")
    ap.add_argument("--workers", type=int, default=4, help="parallel companies (requests stay globally paced)")
    ap.add_argument("--min-interval", type=float, default=0.25, help="global seconds between requests (default 0.25)")
    ap.add_argument("--append", help="append verified, new rows to this workday-companies.md")
    ap.add_argument("--section", default="Auto-discovered", help="### section heading for appended rows")
    ap.add_argument("--verify", help="re-check every row of a workday-companies.md (robots.txt + one CXS request) and report failures; read-only")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.verify:
        rows = []
        for line in open(a.verify, encoding="utf-8"):
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if len(c) >= 4 and re.fullmatch(r"wd\d+", c[2]):
                rows.append((c[0], c[1], int(c[2][2:]), c[3]))
        def chk(r):
            name, t, wd, site = r
            if not robots_allows(t, wd, site, a.min_interval):
                return name, t, wd, site, "robots-disallowed-or-gone"
            tot = cxs_total(t, wd, site, a.min_interval)
            return name, t, wd, site, ("FAIL" if tot is None else tot)
        with ThreadPoolExecutor(max(1, a.workers)) as ex:
            res = list(ex.map(chk, rows))
        bad = [x for x in res if not isinstance(x[4], int)]
        for x in res:
            print(f"| {x[0]} | {x[1]} | wd{x[2]} | {x[3]} | {x[4]} |")
        print(f"--- VERIFIED: {len(res)-len(bad)}/{len(res)} ok; failed: {', '.join(x[0] for x in bad) or 'none'} ---", file=sys.stderr)
        return
    wd_list = WD_DEFAULT + [int(x) for x in a.wd_extra.split(",") if x.strip()]
    entries = list(a.company)
    if a.file:
        entries += [l.strip() for l in open(a.file, encoding="utf-8") if l.strip() and not l.lstrip().startswith("#")]
    t0 = time.time()
    results = [r for r in (from_url(u, a.min_interval) for u in a.url) if r]
    with ThreadPoolExecutor(max(1, a.workers)) as ex:
        results += list(ex.map(lambda e: discover(e, a.careers_url if len(entries) == 1 else None, wd_list,
                                                   a.min_interval, not a.no_sniff), entries))
    ok = [r for r in results if r.get("tenant")]
    for r in results:
        msg = (f"wd{r['wd']} {r['tenant']}/{r['site']} ({r['jobs']} jobs, {r['method']})" if r.get("tenant")
               else r.get("skipped") or "not found")
        print(f"  {r['company']}: {msg}", file=sys.stderr)
    print(f"--- WORKDAY: {len(ok)}/{len(results)} verified in {time.time()-t0:.0f}s ---", file=sys.stderr)
    if a.append:
        have = load_existing(a.append)
        new = [r for r in ok if (r["tenant"].lower(), r["site"].lower()) not in have]
        if new:
            append(a.append, [row(r) for r in sorted(new, key=lambda x: x["company"].lower())], a.section)
        print(f"Appended {len(new)} new rows to {a.append} ({len(ok)-len(new)} already listed)", file=sys.stderr)
    print(json.dumps(ok, indent=2) if a.json else "\n".join(row(r) for r in ok))

if __name__ == "__main__":
    main()
