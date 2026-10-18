#!/usr/bin/env python3
"""Description matching for search_boards.py --match description.

Pass 1 (recall): a job survives if its title hits a keyword phrase, OR a single meaningful word from those phrases or
the profile terms appears in the title ("loose title"), OR at least --min-term-hits distinct profile terms appear in
the description.
Pass 2 (ranking): semantic similarity between each surviving description and the profile text.

Embedding backends, tried in order when --embed-backend auto:
  fastembed  small local ONNX model on CPU (default sentence-transformers/all-MiniLM-L6-v2, about 90 MB, downloaded once
             to ~/.cache/careermate/models). Needs fastembed; if it is missing, one quiet `pip install --user` is tried once
             (marker file in the cache dir; set CAREERMATE_NO_AUTO_INSTALL=1 to skip).
  tfidf      stdlib TF-IDF cosine. Always available, used when fastembed is missing, the model cannot be downloaded,
             or anything in the model path fails. Scores are on a different scale, so each backend has its own cutoff.
Cache: ~/.cache/careermate/match-cache.sqlite (embeddings keyed by model + text hash; SmartRecruiters descriptions keyed
by posting id). Entries unused for 45 days are pruned. Delete the file to reset; nothing else depends on it.
Stdlib only unless fastembed is installed."""
import array, datetime as dt, hashlib, html, math, os, re, sqlite3, sys, threading, time
from collections import Counter

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# Cutoffs for description-only rows, from test runs on 1,260 boards (Oct 2026). See SKILL.md for how they were chosen.
DEFAULT_MIN = {"fastembed": 0.45, "tfidf": 0.12}
TITLE_WEIGHT = 0.2   # semantic_score = 0.8 x description similarity + 0.2 x title similarity to the keyword phrases
CHUNK_CHARS, MAX_CHUNKS, TEXT_KEEP = 1000, 4, 6000

def norm(text):
    text = (text or "").lower().replace("&", " and ")
    return " ".join(re.sub(r"[^a-z0-9+#*]+", " ", text).split())

def strip_html(h):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(html.unescape(h or "")))).strip()

# ---------------------------------------------------------------- profile file

TERM_HEADINGS = re.compile(r"skill|tool|term|keyword", re.I)

def load_profile(path):
    """Markdown-ish file. '## Heading' lines start sections. Lines under a heading that mentions skills, tools or terms
    are match terms (one per line or pipe-separated, '*' for a prefix match, '#' or '>' lines ignored). Every section,
    terms included, feeds the semantic profile. Returns (terms, pieces) where pieces is [(heading, text)]."""
    terms, pieces, head, buf = [], [], "Profile", []
    def flush():
        txt = " ".join(x for x in buf if x).strip()
        if txt:
            pieces.append((head, txt))
    for line in open(path, encoding="utf-8"):
        s = line.strip()
        if s.startswith("## ") or s.startswith("# "):
            flush(); buf = []
            head = s.lstrip("#").strip()
            continue
        if not s or s.startswith(">") or s.startswith("<!--"):
            continue
        s = re.sub(r"^[-*]\s+", "", s)
        if TERM_HEADINGS.search(head):
            parts = [x.strip() for x in s.split("|") if x.strip()]
            terms.extend(parts)
            buf.append(", ".join(p.rstrip("*") for p in parts) + ".")
        else:
            buf.append(s)
    flush()
    pieces = [(h, f"{h}: {t}") for h, t in pieces]
    return terms, pieces

def piece_weight(heading):
    """Prose about the person and the problems they want next says more than tool lists, so it counts more."""
    h = heading.lower()
    if re.search(r"summary|target|problem|want|next|about", h):
        return 2.0
    if re.search(r"outcome|result|core", h):
        return 1.0
    return 0.5

def compile_terms(terms):
    out, seen = [], set()
    for raw in terms:
        p = norm(raw)
        prefix = p.endswith("*")
        p = p.rstrip("*").replace("*", "").strip()
        if not p or (p, prefix) in seen:
            continue
        seen.add((p, prefix))
        rx = r"(?<![a-z0-9+#])" + re.escape(p) + (r"[a-z0-9+#]*" if prefix else r"(?![a-z0-9+#])")
        out.append((raw.strip(), re.compile(rx)))
    return out

# Words too generic to carry a loose title match on their own.
GENERIC = set("""of and the for to a an in at on with or by from head vp vice president chief director senior sr svp evp avp
lead leader manager management principal global us usa remote staff associate executive officer team new role
north america americas emea apac hybrid onsite based internal external work future platform native program programs
operations ops business strategy strategic services service partner specialist analyst coordinator support general
intern junior mid level i ii iii iv v engineer engineering design product""".split())

def loose_words(phrases):
    ws = set()
    for raw in phrases:
        for w in norm(raw).rstrip("*").split():
            w = w.rstrip("*")
            if len(w) >= 4 and w not in GENERIC and not w.isdigit():
                ws.add(w)
    return ws

def term_hits(text_norm, compiled):
    return [raw for raw, rx in compiled if rx.search(text_norm)]

# ---------------------------------------------------------------- cache

class Cache:
    def __init__(self, path):
        self.path, self.lock = path, threading.Lock()
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.db = sqlite3.connect(path, check_same_thread=False)
            self.db.execute("create table if not exists emb (h text primary key, vec blob, used text)")
            self.db.execute("create table if not exists desc (k text primary key, text text, used text)")
            self.db.commit()
        except Exception as e:
            print(f"  match cache unavailable ({type(e).__name__}); continuing without it", file=sys.stderr)
            self.db = None
        self.today = dt.date.today().isoformat()
    def get_desc(self, k):
        if not self.db:
            return None
        with self.lock:
            r = self.db.execute("select text from desc where k=?", (k,)).fetchone()
            if r:
                self.db.execute("update desc set used=? where k=?", (self.today, k))
            return r[0] if r else None
    def put_desc(self, k, text):
        if self.db:
            with self.lock:
                self.db.execute("insert or replace into desc values (?,?,?)", (k, text, self.today))
    def get_vecs(self, hashes):
        out = {}
        if not self.db:
            return out
        with self.lock:
            hs = list(hashes)
            for i in range(0, len(hs), 500):
                part = hs[i:i + 500]
                q = "select h, vec from emb where h in (%s)" % ",".join("?" * len(part))
                for h, blob in self.db.execute(q, part):
                    a = array.array("f"); a.frombytes(blob); out[h] = a.tolist()
                self.db.execute("update emb set used=? where h in (%s)" % ",".join("?" * len(part)), [self.today] + part)
        return out
    def put_vecs(self, items):
        if self.db and items:
            with self.lock:
                self.db.executemany("insert or replace into emb values (?,?,?)",
                                    [(h, array.array("f", v).tobytes(), self.today) for h, v in items])
    def close(self, prune_days=45):
        if not self.db:
            return
        cut = (dt.date.today() - dt.timedelta(days=prune_days)).isoformat()
        with self.lock:
            self.db.execute("delete from emb where used < ?", (cut,))
            self.db.execute("delete from desc where used < ?", (cut,))
            self.db.commit(); self.db.close()

# ---------------------------------------------------------------- backends

def chunks(title, text):
    text = (text or "")[:TEXT_KEEP]
    out = []
    for i in range(0, max(1, len(text)), CHUNK_CHARS):
        part = text[i:i + CHUNK_CHARS]
        if part.strip() or not out:
            out.append(part)
        if len(out) >= MAX_CHUNKS:
            break
    out[0] = f"{title}. {out[0]}"
    return out

def cos(a, b):
    s = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(y * y for y in b))
    return s / (na * nb) if na and nb else 0.0

class FastEmbed:
    name = "fastembed"
    def __init__(self, model, cache, cache_dir):
        os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")   # set before import: huggingface_hub reads them then
        os.environ.setdefault("HF_HUB_VERBOSITY", "error")
        from fastembed import TextEmbedding  # ImportError -> caller falls back
        self.model_name, self.cache = model, cache
        import warnings
        with warnings.catch_warnings():   # fastembed asks for progress bars that the env above disables
            warnings.simplefilter("ignore")
            self.m = TextEmbedding(model, cache_dir=os.path.join(cache_dir, "models"))
        self.label = f"fastembed:{model}"
        self.stats = {"chunks": 0, "cached": 0}
    def embed(self, texts):
        hs = [hashlib.sha1((self.model_name + "\n" + t).encode()).hexdigest() for t in texts]
        have = self.cache.get_vecs(set(hs)) if self.cache else {}
        need = [(h, t) for h, t in dict(zip(hs, texts)).items() if h not in have]
        self.stats["chunks"] += len(texts); self.stats["cached"] += len(texts) - len(need)
        if need:
            vecs = [list(map(float, v)) for v in self.m.embed([t for _, t in need], batch_size=64)]
            new = list(zip([h for h, _ in need], vecs))
            if self.cache:
                self.cache.put_vecs(new)
            have.update(new)
        return [have[h] for h in hs]
    def score(self, profile_pieces, jobs, phrases=()):
        """jobs: [(key, title, text)] -> {key: (semantic, description_sim, title_sim)}. description_sim = weighted mean over
        profile sections of the cosine with the best-matching description chunk (see piece_weight). title_sim = best
        cosine between the job title and any keyword phrase."""
        desc = self._desc(profile_pieces, jobs)
        tsim = {}
        if phrases and jobs:
            import numpy as np
            Q = np.array(self.embed(list(phrases)), dtype="float32"); Q /= np.linalg.norm(Q, axis=1, keepdims=True) + 1e-9
            T = np.array(self.embed([t for _, t, _ in jobs]), dtype="float32"); T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-9
            tsim = dict(zip([k for k, _, _ in jobs], (T @ Q.T).max(1).tolist()))
        return blend(desc, tsim)
    def _desc(self, profile_pieces, jobs):
        P = self.embed([t for _, t in profile_pieces])
        allc, owner = [], []
        for key, title, text in jobs:
            for c in chunks(title, text):
                allc.append(c); owner.append(key)
        V = self.embed(allc) if allc else []
        try:
            import numpy as np
            Pm = np.array(P, dtype="float32"); Pm /= np.linalg.norm(Pm, axis=1, keepdims=True) + 1e-9
            Vm = np.array(V, dtype="float32") if V else np.zeros((0, Pm.shape[1]), "float32")
            Vm /= np.linalg.norm(Vm, axis=1, keepdims=True) + 1e-9
            S = Vm @ Pm.T if len(Vm) else np.zeros((0, len(P)))
            sims = S.tolist()
        except ImportError:
            sims = [[cos(v, p) for p in P] for v in V]
        best = {}
        for key, row in zip(owner, sims):
            cur = best.setdefault(key, [-1.0] * len(P))
            for i, s in enumerate(row):
                if s > cur[i]:
                    cur[i] = s
        w = [piece_weight(h) for h, _ in profile_pieces]
        return {k: sum(x * y for x, y in zip(v, w)) / sum(w) for k, v in best.items()}

STOPWORDS = set("""a about above after again all also am an and any are as at be because been before being below between both
but by can could did do does doing down during each few for from further had has have having he her here hers him his how i
if in into is it its itself just me more most my no nor not now of off on once only or other our ours out over own same she
should so some such than that the their them then there these they this those through to too under until up very was we were
what when where which while who whom why will with would you your yours etc including include includes within across per
role roles job jobs candidate candidates position company team teams work working experience years year ability strong
excellent responsible responsibilities requirements required preferred qualifications plus benefits apply equal opportunity
employer status gender race religion disability veteran age national origin sexual orientation identity law us we're you'll
new help join looking great best world well like make makes using use used""".split())

def toks(text):
    ws = [w for w in norm(text).split() if w not in STOPWORDS and len(w) > 1 and not w.isdigit()]
    return ws + [a + "_" + b for a, b in zip(ws, ws[1:])]

def blend(desc, tsim):
    out = {}
    for k, d in desc.items():
        t = tsim.get(k)
        out[k] = ((1 - TITLE_WEIGHT) * d + TITLE_WEIGHT * t if t is not None else d, d, t)
    return out

class TfIdf:
    name, label = "tfidf", "tfidf"
    def __init__(self):
        self.stats = {"chunks": 0, "cached": 0}
    def score(self, profile_pieces, jobs, phrases=()):
        """Same return shape as FastEmbed.score. title_sim = best share of a phrase's words found in the title."""
        desc = self._desc(profile_pieces, jobs)
        pw = [set(w for w in norm(p).rstrip("*").split() if w not in STOPWORDS) for p in phrases]
        pw = [x for x in pw if x]
        tsim = {}
        if pw:
            for k, title, _ in jobs:
                tw = set(norm(title).split())
                tsim[k] = max(len(x & tw) / len(x) for x in pw)
        return blend(desc, tsim)
    def _desc(self, profile_pieces, jobs):
        docs = {k: Counter(toks((title + " ") * 3 + (text or "")[:TEXT_KEEP])) for k, title, text in jobs}
        prof = Counter(toks(" ".join(t for _, t in profile_pieces)))
        N = len(docs) + 1
        df = Counter()
        for c in list(docs.values()) + [prof]:
            df.update(c.keys())
        idf = {w: math.log((N + 1) / (n + 0.5)) for w, n in df.items()}
        def vec(c):
            v = {w: (1 + math.log(n)) * idf[w] for w, n in c.items()}
            nrm = math.sqrt(sum(x * x for x in v.values())) or 1.0
            return {w: x / nrm for w, x in v.items()}
        pv = vec(prof)
        return {k: sum(x * pv.get(w, 0.0) for w, x in vec(c).items()) for k, c in docs.items()}

INSTALL_TIMEOUT = 180   # seconds for the one-time fastembed install attempt

def try_install_fastembed(cache_dir, log=sys.stderr):
    """One quiet `pip install --user` attempt, ever (a marker file in cache_dir records it). Opt out with
    CAREERMATE_NO_AUTO_INSTALL=1. Returns True when fastembed imports afterwards."""
    import importlib, site, subprocess
    marker = os.path.join(cache_dir, "fastembed-install-attempted")
    if os.environ.get("CAREERMATE_NO_AUTO_INSTALL") or os.path.exists(marker):
        return False
    try:
        os.makedirs(cache_dir, exist_ok=True)
        open(marker, "w").write(dt.datetime.now().isoformat(timespec="seconds") + "\n")
    except OSError:
        pass
    print(f"  semantic: fastembed not installed; trying a one-time pip install (up to {INSTALL_TIMEOUT // 60} min)", file=log)
    try:
        r = subprocess.run([sys.executable, "-m", "pip", "install", "--user", "--quiet", "--disable-pip-version-check",
                            "--break-system-packages", "fastembed"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                           timeout=INSTALL_TIMEOUT)
        if r.returncode != 0:
            print(f"  semantic: fastembed install failed (pip exit {r.returncode})", file=log)
            return False
    except (OSError, subprocess.TimeoutExpired) as e:
        print(f"  semantic: fastembed install did not finish ({type(e).__name__})", file=log)
        return False
    up = site.getusersitepackages()
    if up and up not in sys.path:
        sys.path.append(up)
    importlib.invalidate_caches()
    try:
        import fastembed  # noqa: F401
        return True
    except Exception:
        return False

def make_backend(choice, model, cache, cache_dir, log=sys.stderr):
    b = None
    if choice in ("auto", "fastembed"):
        try:
            b = FastEmbed(model, cache, cache_dir)
        except ImportError:
            if try_install_fastembed(cache_dir, log):
                try:
                    b = FastEmbed(model, cache, cache_dir)
                except Exception as e:
                    print(f"  semantic: embedding model unavailable ({type(e).__name__}: {str(e)[:120]}); using TF-IDF fallback",
                          file=log)
            else:
                print("  semantic: embedding model unavailable (fastembed not installed); using TF-IDF fallback", file=log)
        except Exception as e:
            print(f"  semantic: embedding model unavailable ({type(e).__name__}: {str(e)[:120]}); using TF-IDF fallback",
                  file=log)
    b = b or TfIdf()
    print(f"  semantic: backend {b.label}", file=log)
    return b
