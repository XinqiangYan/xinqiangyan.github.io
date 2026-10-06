#!/usr/bin/env python3
"""Convert a BibTeX export (e.g. from Google Scholar) into data/publications.yaml.

Usage:
    python3 scripts/bib2yaml.py citations.bib                 # all types
    python3 scripts/bib2yaml.py citations.bib --only journal  # journal articles only

Existing entries in data/publications.yaml are kept; their `featured`, `note`,
`pdf`, `url` and `doi` values are preserved when the same title is imported again.
Entries whose title already exists are not duplicated. Standard library only.
"""
import argparse
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "publications.yaml"

ACCENTS = {"'": "\u0301", "`": "\u0300", "^": "\u0302", '"': "\u0308", "~": "\u0303", "c": "\u0327", "v": "\u030c", "=": "\u0304"}


def latex_to_text(s):
    s = re.sub(r"\\([\'`^\"~=cv])\s*\{?\\?([A-Za-z])\}?", lambda m: unicodedata.normalize("NFC", m.group(2) + ACCENTS[m.group(1)]), s)
    s = s.replace("\\&", "&").replace("\\%", "%").replace("\\_", "_").replace("--", "–").replace("~", " ")
    s = re.sub(r"\\[a-zA-Z]+\s*", "", s)
    s = s.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip()


def parse_bibtex(text):
    entries, i = [], 0
    while True:
        at = text.find("@", i)
        if at < 0:
            break
        m = re.match(r"@(\w+)\s*\{", text[at:])
        if not m:
            i = at + 1
            continue
        etype = m.group(1).lower()
        j = at + m.end()
        depth, k = 1, j
        while k < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[k], 0)
            k += 1
        body = text[j:k - 1]
        i = k
        if etype in ("comment", "preamble", "string"):
            continue
        _, _, rest = body.partition(",")
        fields, p = {}, 0
        while p < len(rest):
            fm = re.match(r"\s*,?\s*([\w-]+)\s*=\s*", rest[p:])
            if not fm:
                break
            name = fm.group(1).lower()
            p += fm.end()
            if p < len(rest) and rest[p] == "{":
                depth, q = 1, p + 1
                while q < len(rest) and depth:
                    depth += {"{": 1, "}": -1}.get(rest[q], 0)
                    q += 1
                val, p = rest[p + 1:q - 1], q
            elif p < len(rest) and rest[p] == '"':
                q = rest.index('"', p + 1)
                val, p = rest[p + 1:q], q + 1
            else:
                vm = re.match(r"[^,]*", rest[p:])
                val, p = vm.group(0), p + vm.end()
            fields[name] = val.strip()
        entries.append((etype, fields))
    return entries


def short_author(name):
    name = latex_to_text(name)
    if name.lower() == "others":
        return "et al."
    if "," in name:
        last, first = [x.strip() for x in name.split(",", 1)]
    else:
        parts = name.split()
        last, first = parts[-1], " ".join(parts[:-1])
    initials = "".join(w[0].upper() for w in re.split(r"[\s\-.]+", first) if w)
    return f"{last} {initials}".strip()


def classify(etype, f):
    venue = (f.get("journal") or f.get("booktitle") or "").lower()
    if etype == "patent" or "patent" in venue or "patent" in f.get("note", "").lower():
        return "patent"
    if "arxiv" in venue or "biorxiv" in venue or "medrxiv" in venue or "preprint" in venue:
        return "preprint"
    if etype == "article":
        return "journal"
    if etype in ("inproceedings", "conference", "proceedings"):
        return "conference"
    if etype in ("book", "incollection", "inbook"):
        return "book"
    return "other"


def norm(title):
    return re.sub(r"[^a-z0-9]", "", title.lower())


def yaml_str(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def load_existing():
    """Minimal reader for the simple list-of-maps format this script writes."""
    if not OUT.exists():
        return []
    items, cur = [], None
    for line in OUT.read_text(encoding="utf-8").splitlines():
        if line.startswith("- "):
            cur = {}
            items.append(cur)
            line = "  " + line[2:]
        m = re.match(r"\s{2}(\w+):\s*(.*)$", line)
        if cur is not None and m:
            key, val = m.group(1), m.group(2).strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1].replace('\\"', '"').replace("\\\\", "\\")
            elif val in ("true", "false"):
                val = val == "true"
            elif val.isdigit():
                val = int(val)
            cur[key] = val
    return items


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bibfile")
    ap.add_argument("--only", help="keep only this type (journal, conference, patent, preprint, book)")
    args = ap.parse_args()

    existing = load_existing()
    by_title = {norm(e.get("title", "")): e for e in existing}
    added = 0
    for etype, f in parse_bibtex(Path(args.bibfile).read_text(encoding="utf-8")):
        title = latex_to_text(f.get("title", ""))
        year = re.search(r"\d{4}", f.get("year", "") or f.get("date", ""))
        if not title or not year:
            continue
        ptype = classify(etype, f)
        if args.only and ptype != args.only:
            continue
        details = f.get("volume", "")
        if f.get("number"):
            details += f"({f['number']})"
        if f.get("pages"):
            details += (":" if details else "") + latex_to_text(f["pages"])
        new = {
            "title": title,
            "authors": ", ".join(short_author(a) for a in re.split(r"\s+and\s+", f.get("author", "")) if a.strip()),
            "venue": latex_to_text(f.get("journal") or f.get("booktitle") or (f.get("note") if ptype == "patent" else "") or f.get("publisher") or ""),
            "details": details,
            "year": int(year.group(0)),
            "type": ptype,
            "doi": f.get("doi", ""),
            "url": f.get("url", "") or ("" if f.get("doi") else "https://scholar.google.com/scholar?q=" + quote_plus(title)),
        }
        old = by_title.get(norm(title))
        if old:
            for k, v in new.items():  # fill gaps only; never overwrite hand edits
                if k == "url" and old.get("doi"):
                    continue
                if v and not old.get(k):
                    old[k] = v
            continue
        existing.append(new)
        by_title[norm(title)] = new
        added += 1

    existing.sort(key=lambda e: (-int(e.get("year", 0)), e.get("title", "").lower()))
    keys = ["title", "authors", "venue", "details", "year", "type", "doi", "url", "pdf", "featured", "note"]
    lines = [
        "# Publications list, rendered on /publications/ (newest first).",
        "# Regenerate/merge from a Google Scholar BibTeX export with:",
        "#   python3 scripts/bib2yaml.py citations.bib [--only journal]",
        "# Fields: title, authors (\"Yan X\" is bolded), venue, details, year,",
        "#   type (journal | conference | patent | preprint | book), doi, url, pdf,",
        "#   featured (true = also on the home page), note (badge text).",
        "",
    ]
    for e in existing:
        first = True
        for k in keys + [k for k in e if k not in keys]:
            v = e.get(k)
            if v in (None, "", False):
                continue
            val = ("true" if v is True else str(v)) if isinstance(v, (bool, int)) else yaml_str(v)
            lines.append(f"{'- ' if first else '  '}{k}: {val}")
            first = False
        lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Added {added} new entries; {len(existing)} total -> {OUT.relative_to(ROOT)}", file=sys.stderr)


if __name__ == "__main__":
    main()
