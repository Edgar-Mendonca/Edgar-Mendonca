"""Collect the brain's corpus: every document of every source, split into labelled chunks.

Each chunk is one section of a document (40-220 words), with the heading path in front of it, and three labels:
  project  which project it belongs to (datum-plan, centriforge, shpb, ...)
  area     the area of work (piping, impact-mechanics, ...), from sources.json
  kind     what sort of knowledge it is: feature, release, decision, session, plan, practice, research, note
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # the Edgar-Mendonca repository
BRAIN = ROOT / "brain"

DOC_NAMES = re.compile(r"(README|CHANGELOG|MEMORY|FAMILY|BRAND|BRAIN|ARCHITECTURE|ROADMAP|VALIDATION|LIBRARY_EVALUATION|"
                       r"PLAN[\w.-]*|BRAINSTORM[\w.-]*|CLAUDE|CONTRIBUTING|STATUS[\w.-]*|\d{4}-\d{2}-\d{2}[\w.-]*)\.md$", re.I)
SKIP_DIRS = {"node_modules", ".git", "target", "dist", "build", ".venv", "venv", "__pycache__", "frontend", "tests_ui"}
MIN_WORDS, MAX_WORDS = 40, 220
DOC_DIRS = {"docs", "status", "brain", "home"}


def clone_or_update(repo: str, cache: Path) -> Path:
    """Shallow-clone a public GitHub repository into the cache, or fast-forward it if it is already there."""
    dest = cache / repo.split("/")[1]
    if (dest / ".git").exists():
        subprocess.run(["git", "-C", str(dest), "pull", "-q", "--depth", "1", "--ff-only"], check=False)
    else:
        cache.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "-q", "--depth", "1", f"https://github.com/{repo}.git", str(dest)], check=True)
    return dest


def doc_files(repo_dir: Path) -> list[Path]:
    """The documents worth learning from: Markdown docs and docs/site.json, never code or vendored files."""
    out = []
    for p in sorted(repo_dir.rglob("*")):
        parts = p.relative_to(repo_dir).parts
        if any(part in SKIP_DIRS for part in parts):
            continue
        if len(parts) > 1 and parts[0] not in DOC_DIRS:          # only the repo root, docs/, status/, brain/
            continue
        if p.is_file() and (DOC_NAMES.search(p.name) or (p.name == "site.json" and p.parent.name == "docs")):
            if p.name.upper() not in {"SECURITY.MD"}:
                out.append(p)
    return out


def kind_of(path: Path, heading: str) -> str:
    name, h = path.name.upper(), heading.lower()
    if name.startswith("CHANGELOG"):
        return "release"
    if name.startswith(("PLAN", "BRAINSTORM", "ROADMAP")) or "roadmap" in h or "next steps" in h:
        return "plan"
    if name.startswith(("CLAUDE", "CONTRIBUTING", "FAMILY", "BRAND")) or "how we work" in h:
        return "practice"
    if name.startswith("MEMORY") or re.match(r"\d{4}-\d{2}-\d{2}", name):
        if "decision" in h:
            return "decision"
        if "session" in h or re.search(r"\bsession \d+", h):
            return "session"
        return "memory"
    return "feature"


# ---------- Markdown, Astro and JSON to plain sections ----------

def strip_md(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)                    # code blocks
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)                     # images
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)                  # links -> their text
    text = re.sub(r"<[^>]+>", " ", text)                                  # html
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"^\s*\|?\s*:?-{3,}.*$", " ", text, flags=re.M)         # table rules
    text = text.replace("|", " ; ").replace("**", "").replace("`", "")
    text = re.sub(r"(\s*;\s*){2,}", " ; ", text)                     # empty table cells
    text = re.sub(r"^\s*[;>]\s*", "", text, flags=re.M)
    return text


def sections(md: str) -> list[tuple[str, str]]:
    """Split Markdown into (heading path, body) pairs."""
    path: list[str] = []
    out, buf = [], []
    for line in md.splitlines():
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            if buf:
                out.append((" › ".join(path), "\n".join(buf)))
                buf = []
            level = len(m.group(1))
            path = path[: level - 1] + [re.sub(r"[#*`]", "", m.group(2)).strip()]
        else:
            buf.append(line)
    if buf:
        out.append((" › ".join(path), "\n".join(buf)))
    return out


def astro_sections(src: str) -> list[tuple[str, str]]:
    """The article text of an Astro case-study page: drop frontmatter, components and expressions."""
    body = src.split("---", 2)[-1]
    desc = re.search(r'description="([^"]+)"', src)
    title = re.search(r'title="([^"]+)"', src)
    body = re.sub(r"<Eq[^>]*/>", " ", body)
    body = re.sub(r'<Fig src="[^"]*" alt="([^"]*)"[^>]*/>', r"Figure: \1.", body)
    body = re.sub(r"<h2>.*?</span>(.*?)</h2>", r"\n## \1\n", body)
    body = re.sub(r"<h3>(.*?)</h3>", r"\n### \1\n", body)
    body = re.sub(r"\{[^{}]*\}", " ", body)
    body = re.sub(r"<li>", "\n- ", body)
    body = re.sub(r"</p>", "\n\n", body)
    md = f"# {title.group(1) if title else ''}\n{desc.group(1) if desc else ''}\n" + re.sub(r"<[^>]+>", " ", body)
    return sections(md)


def json_sections(src: str) -> list[tuple[str, str]]:
    """docs/site.json: the app's own public description, roadmap and highlights."""
    data = json.loads(src)
    out = []

    def walk(v, key):
        if isinstance(v, str) and len(v.split()) >= 4:
            out.append((key, v))
        elif isinstance(v, list):
            for x in v:
                walk(x, key)
        elif isinstance(v, dict):
            for k, x in v.items():
                if k not in {"repo", "accent", "icon", "shot", "screenshots", "url", "href", "src"}:
                    walk(x, f"{key} › {k}" if key else k)

    walk(data, "")
    grouped: dict[str, list[str]] = {}
    for k, v in out:
        grouped.setdefault(k.split(" › ")[0], []).append(v)
    return [(k, "\n".join(v)) for k, v in grouped.items()]


def front_matter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}, text
    meta = dict(re.findall(r"^(\w+):\s*(.+)$", m.group(1), re.M))
    return meta, text[m.end():]


def chunks(heading: str, body: str) -> list[str]:
    """Paragraph-sized pieces of one section, merged up to MAX_WORDS, each prefixed with its heading."""
    paras = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n|\n(?=\s*[-*]\s)", strip_md(body))]
    paras = [p for p in paras if len(p.split()) >= 3]
    out, cur = [], []
    for p in paras:
        words = p.split()
        while len(words) > MAX_WORDS:                       # very long paragraph: cut it
            out.append(" ".join(words[:MAX_WORDS]))
            words = words[MAX_WORDS:]
        if sum(len(c.split()) for c in cur) + len(words) > MAX_WORDS and cur:
            out.append(" ".join(cur))
            cur = []
        cur.append(" ".join(words))
    if cur:
        out.append(" ".join(cur))
    head = strip_md(heading).strip()
    return [f"{head}. {c}" if head else c for c in out if len(c.split()) >= MIN_WORDS or (out and len(out) == 1 and len(c.split()) >= 12)]


def private_sections(rows_add) -> None:
    """Private archives in brain/private/*.md, labelled section by section from brain/private/sections.json:
    {"archive.md": {"kind": "archive", "skip": ["1", "24"], "sections": {"3": {"project": "...", "area": "..."}, ...}}}.
    A top-level section ("## 3. Title") takes the labels of its number; sections without labels are skipped."""
    folder = BRAIN / "private"
    spec_file = folder / "sections.json"
    if not spec_file.exists():
        print("  no private/sections.json: private sources skipped")
        return
    spec = json.loads(spec_file.read_text())
    for name, cfg in spec.items():
        f = folder / name
        if not f.exists():
            print(f"  missing private source {name}")
            continue
        _, body = front_matter(f.read_text(encoding="utf-8"))
        for heading, text in sections(body):
            parts = heading.split(" › ") if heading else []
            # The section number is on the first heading of the form "3. Title" (the document title comes before it).
            at = next((i for i, part in enumerate(parts) if re.match(r"\d+\.\s", part)), None)
            if at is None:
                continue
            num = re.match(r"(\d+)\.", parts[at]).group(1)
            if num in cfg.get("skip", []) or num not in cfg["sections"]:
                continue
            lab = cfg["sections"][num]
            rows_add([(" › ".join(parts[at:]), text)], lab["project"], lab["area"],
                     lambda h, k=cfg.get("kind", "archive"): k, f"private/{name}")


_FP = set(json.loads((BRAIN / "redact.json").read_text())["fingerprints"]) if (BRAIN / "redact.json").exists() else set()
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def redact(text: str) -> str:
    """Replace e-mail addresses and every word whose fingerprint is listed in redact.json."""
    import hashlib
    text = _EMAIL.sub("[email]", text)
    def word(m):
        w = m.group(0)
        return "[name]" if hashlib.sha256(w.lower().encode()).hexdigest()[:16] in _FP else w
    return re.sub(r"[A-Za-z][A-Za-z0-9-]*", word, text)


def standards_notes(rows: list[dict]) -> list[dict]:
    """One training note per standard in brain/standards.json: its title, scope and related standards, and where it
    is cited in the rest of the corpus (projects, how often, and in which sections), worked out at every build."""
    cat = json.loads((BRAIN / "standards.json").read_text())["standards"]
    out = []
    for s in cat:
        rx = re.compile(s["match"], re.I)
        hits = [r for r in rows if rx.search(r["text"])]
        by = {}
        for r in hits:
            by.setdefault(r["project"], []).append(r)
        cited = "; ".join(f"{p} ({len(v)} note{'s' if len(v) > 1 else ''})" for p, v in sorted(by.items(), key=lambda kv: -len(kv[1])))
        where = sorted({r["heading"].split(" › ")[-1] for r in hits if r["heading"]})[:6]
        text = (f"{s['code']}: {s['title']}. {s['scope']}"
                + (f" Related standards: {', '.join(s['related'])}." if s["related"] else "")
                + (f" Cited by {cited}" + (f", for example in: {'; '.join(where)}." if where else ".") if hits
                   else " Used in package work; not cited in the repositories yet."))
        out.append({"project": "standards", "area": s["area"], "kind": "standard", "source": "brain/standards.json",
                    "heading": s["code"], "version": None, "date": None, "text": text, "cites": len(hits)})
    return out


def collect(cache: Path, offline: bool = False, private: bool = False) -> list[dict]:
    src = json.loads((BRAIN / "sources.json").read_text())
    rows: list[dict] = []

    def add(text_sections, project, area, kind_fn, origin):
        for heading, body in text_sections:
            version = re.search(r"\b(\d+\.\d+\.\d+)\b", heading)
            date = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", heading)
            for c in chunks(heading, body):
                rows.append({"project": project, "area": area, "kind": kind_fn(heading), "source": origin,
                             "heading": heading[:160], "version": version.group(1) if version else None,
                             "date": date.group(1) if date else None, "text": c})

    for s in src["repos"]:
        d = cache / s["repo"].split("/")[1]
        if not offline:
            d = clone_or_update(s["repo"], cache)
        if not d.exists():
            print(f"  skip {s['repo']} (not in cache)")
            continue
        for f in doc_files(d):
            rel = f"{s['repo']}/{f.relative_to(d).as_posix()}"
            text = f.read_text(encoding="utf-8", errors="ignore")
            secs = json_sections(text) if f.suffix == ".json" else sections(text)
            add(secs, s["project"], s["area"], lambda h, f=f: kind_of(f, h), rel)

    for s in src["local"]:
        p = ROOT / s["path"]
        files = sorted(p.glob("*.md")) if p.is_dir() else [p]
        for f in files:
            if f.name == "README.md":
                continue
            text = f.read_text(encoding="utf-8")
            if f.suffix == ".astro":
                add(astro_sections(text), s["project"], s["area"], lambda h, s=s: s["kind"], f"local/{s['path']}")
            else:
                meta, body = front_matter(text)
                add(sections(body), meta.get("project", "notes"), meta.get("area", "web"), lambda h, s=s: s["kind"],
                    f"local/{f.relative_to(ROOT).as_posix()}")

    if private:
        private_sections(add)

    # Remove names that must not be learnt (fingerprints in redact.json) and any e-mail address.
    rows = [{**r, "text": redact(r["text"]), "heading": redact(r["heading"])} for r in rows]

    # Drop exact duplicates (READMEs repeat the same lines across apps).
    seen, uniq = set(), []
    for r in rows:
        key = r["text"].lower()
        if key not in seen:
            seen.add(key)
            uniq.append(r)
    # The standards catalogue, with its cross-references into everything above.
    return uniq + standards_notes(uniq)
