#!/usr/bin/env python3
"""
Build wordshaping.org from words.json.      python3 build.py

    /                     lexicon
    /leaderboard/         ranked by documented public use
    /<slug>/              one dedicated URL per word
    /sitemap.xml

Every word page leads with `proposed` — the form exactly as first written
by its author. That field is the record of authorial intention and is
never presented as an erratum.
"""

import json, html, shutil
from pathlib import Path

ROOT = Path(__file__).parent
REPO = "https://github.com/PlanetaryCouncil/wordshaping.org"

CSS = """
:root{--bg:#fbfaf8;--fg:#1a1a18;--muted:#6f6e68;--faint:#94928b;--line:#e3e0d9;
--panel:#fff;--accent:#8a5a2b;--glow:#fdf3e3;--y-bg:#fdf3e3;--y-fg:#8a5a2b;
--m-bg:#eef1f5;--m-fg:#4a5768;--w-bg:#e9f0e7;--w-fg:#4a6b45}
@media (prefers-color-scheme:dark){:root{--bg:#141418;--fg:#e9e7e2;--muted:#9d9a92;
--faint:#77746d;--line:#31313a;--panel:#1c1c22;--accent:#e0ad6f;--glow:#2a2114;
--y-bg:#3a2c17;--y-fg:#e8bd82;--m-bg:#242a33;--m-fg:#9fb2c9;--w-bg:#222e21;--w-fg:#9dc094}}
:root[data-theme=dark]{--bg:#141418;--fg:#e9e7e2;--muted:#9d9a92;--faint:#77746d;
--line:#31313a;--panel:#1c1c22;--accent:#e0ad6f;--glow:#2a2114;--y-bg:#3a2c17;
--y-fg:#e8bd82;--m-bg:#242a33;--m-fg:#9fb2c9;--w-bg:#222e21;--w-fg:#9dc094}
:root[data-theme=light]{--bg:#fbfaf8;--fg:#1a1a18;--muted:#6f6e68;--faint:#94928b;
--line:#e3e0d9;--panel:#fff;--accent:#8a5a2b;--glow:#fdf3e3;--y-bg:#fdf3e3;
--y-fg:#8a5a2b;--m-bg:#eef1f5;--m-fg:#4a5768;--w-bg:#e9f0e7;--w-fg:#4a6b45}
*{box-sizing:border-box}
body{margin:0;padding:2.5rem 1.5rem 6rem;background:var(--bg);color:var(--fg);
font:17px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;
overflow-x:hidden;-webkit-font-smoothing:antialiased}
.wrap{max-width:760px;margin:0 auto}
nav{font-size:.84rem;margin-bottom:2.8rem;color:var(--faint)}
nav a{color:var(--accent);text-decoration:none;margin-right:1.1rem}
nav a:hover{text-decoration:underline}
h1{font-family:Georgia,"Iowan Old Style",serif;font-size:clamp(2rem,5.5vw,3rem);
letter-spacing:-.022em;margin:0 0 .35rem;font-weight:400;word-break:break-word;line-height:1.1}
.byline{color:var(--muted);margin:0 0 .1rem;font-size:.95rem}
.byline b{color:var(--fg);font-weight:600}
.tag-line{color:var(--muted);margin:0 0 2rem}
.say{color:var(--faint);font-size:.82rem;letter-spacing:.05em;margin:.5rem 0 2rem}
blockquote.epi{margin:0 0 2.5rem;padding:.1rem 0 .1rem 1.2rem;border-left:2px solid var(--accent);
font-family:Georgia,serif;font-size:1.15rem;line-height:1.5}
h2{font-family:Georgia,serif;font-weight:400;font-size:1.4rem;margin:3.2rem 0 .3rem}
h2+.lede{color:var(--muted);font-size:.92rem;margin:0 0 1.4rem;max-width:62ch}
.origin{background:var(--glow);border:1px solid var(--line);border-left:3px solid var(--accent);
border-radius:7px;padding:1.3rem 1.5rem;margin:0 0 2rem}
.origin .k{font-size:.68rem;text-transform:uppercase;letter-spacing:.13em;font-weight:700;
color:var(--accent);margin-bottom:.5rem}
.origin .p{font-family:Georgia,serif;font-size:clamp(1.3rem,3.6vw,1.9rem);font-weight:600;
letter-spacing:-.015em;word-break:break-word;line-height:1.2;color:var(--fg)}
.origin .who{font-size:.85rem;color:var(--muted);margin-top:.55rem}
.origin .same{font-size:.85rem;color:var(--muted);margin-top:.5rem;font-style:italic}
.badge{display:inline-block;font-size:.65rem;text-transform:uppercase;letter-spacing:.07em;
font-weight:700;padding:.15rem .45rem;border-radius:3px;vertical-align:2px}
.b-marsita{background:var(--y-bg);color:var(--y-fg)}
.b-claude{background:var(--m-bg);color:var(--m-fg)}
.b-wild{background:var(--w-bg);color:var(--w-fg)}
.pos{font-style:italic;color:var(--faint);font-size:.92rem}
.def{font-size:1.14rem;margin:0 0 1.2rem}
.cite{font-family:Georgia,serif;font-style:italic;color:var(--muted);padding-left:1rem;
border-left:2px solid var(--line);margin:0 0 1.8rem}
.field{margin:0 0 1.15rem;font-size:.94rem}
.field b{display:block;font-family:Georgia,serif;font-size:.98rem;margin-bottom:.12rem;font-weight:600}
.field span{color:var(--muted)}
.entry{border-top:1px solid var(--line);padding:1.3rem 0}
.entry:last-of-type{border-bottom:1px solid var(--line)}
.entry a.w{font-family:Georgia,serif;font-size:1.35rem;font-weight:600;color:var(--fg);
text-decoration:none;word-break:break-word}
.entry a.w:hover{color:var(--accent)}
.entry p{margin:.3rem 0 0;color:var(--muted);font-size:.94rem}
.entry .orig{font-size:.82rem;color:var(--faint);margin-top:.3rem}
.count{display:inline-block;min-width:2.2rem;font-family:Georgia,serif;font-size:1.5rem;
font-weight:700;color:var(--accent)}
.zero{color:var(--faint);font-weight:400}
.rank{display:flex;gap:1rem;align-items:baseline;border-top:1px solid var(--line);padding:.9rem 0}
.rank:last-of-type{border-bottom:1px solid var(--line)}
.rank .n{font-variant-numeric:tabular-nums;color:var(--faint);font-size:.85rem;min-width:2rem}
.rank .body{flex:1}
.rank a{font-family:Georgia,serif;font-size:1.15rem;font-weight:600;color:var(--fg);
text-decoration:none;word-break:break-word}
.rank a:hover{color:var(--accent)}
.sight{border-left:2px solid var(--accent);padding:.1rem 0 .1rem 1rem;margin:0 0 1.1rem}
.sight .when{font-size:.76rem;color:var(--faint);letter-spacing:.05em;text-transform:uppercase}
.sight .what{margin:.15rem 0 0}
.empty{background:var(--panel);border:1px dashed var(--line);border-radius:8px;
padding:1.3rem 1.4rem;color:var(--muted);font-size:.94rem}
.cta{display:inline-block;margin-top:.9rem;padding:.55rem .95rem;border:1px solid var(--accent);
border-radius:5px;color:var(--accent);text-decoration:none;font-size:.88rem;font-weight:600}
.cta:hover{background:var(--accent);color:var(--bg)}
.score{font-size:.79rem;color:var(--faint);font-variant-numeric:tabular-nums}
table{border-collapse:collapse;width:100%;font-size:.9rem;margin-top:1rem}
th,td{text-align:left;padding:.55rem .7rem;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:.72rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.win{color:var(--accent);font-weight:700;font-size:.75rem;letter-spacing:.05em}
footer{margin-top:4rem;padding-top:1.4rem;border-top:1px solid var(--line);
color:var(--faint);font-size:.85rem}
footer a{color:var(--accent)}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.87em}
figure{margin:0 0 2rem}
figure img{width:100%;height:auto;display:block;border:1px solid var(--line);border-radius:8px}
figcaption{font-size:.82rem;color:var(--faint);margin-top:.5rem}
.wotd{background:var(--glow);border:1px solid var(--line);border-left:3px solid var(--accent);
border-radius:7px;padding:1.4rem 1.6rem;margin:0 0 2.6rem}
.wotd .k{font-size:.68rem;text-transform:uppercase;letter-spacing:.13em;font-weight:700;
color:var(--accent);margin-bottom:.55rem}
.wotd a.w{font-family:Georgia,serif;font-size:clamp(1.5rem,4.2vw,2.1rem);font-weight:600;
color:var(--fg);text-decoration:none;letter-spacing:-.015em;word-break:break-word}
.wotd a.w:hover{color:var(--accent)}
.wotd p{margin:.45rem 0 0;color:var(--muted);font-size:.95rem}
.stamp{display:inline-block;font-size:.68rem;text-transform:uppercase;letter-spacing:.1em;
font-weight:700;padding:.2rem .5rem;border-radius:3px;background:var(--accent);color:var(--bg);
vertical-align:2px}
"""

LABEL = {"marsita": "coined here", "claude": "suggested", "wild": "found in the wild"}


def e(s):
    return html.escape(str(s or ""))


def page(title, desc, canon, body, depth, jsonld=None, og_image=None):
    up = "../" * depth
    ld = f'<script type="application/ld+json">{json.dumps(jsonld)}</script>' if jsonld else ""
    card = "summary_large_image" if og_image else "summary"
    img_tag = f'<meta property="og:image" content="{e(og_image)}">' if og_image else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canon)}">
<meta property="og:type" content="article">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(canon)}">
<meta property="og:site_name" content="Wordshaping">
<meta name="twitter:card" content="{card}">
{img_tag}
{ld}
<style>{CSS}</style>
</head>
<body><div class="wrap">
<nav><a href="{up if depth else ''}">the lexicon</a><a href="{up}leaderboard/">leaderboard</a><a href="{up}working-table.html">working table</a><a href="{REPO}">source</a></nav>
{body}
<footer>
<a href="{up if depth else ''}">Wordshaping</a> — a lexicon of words that should already exist.<br>
Sightings are the only thing ranked here. Add one by
<a href="{REPO}/issues/new">opening an issue</a> or editing <code>words.json</code>.
</footer>
</div></body>
</html>
"""


MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def pretty(iso):
    """2026-08-25 -> 25 August 2026."""
    y, m, dd = iso.split("-")
    return f"{int(dd)} {MONTHS[int(m) - 1]} {y}"


def word_of_the_day(ws):
    """The entry with the latest wotd date. Ties break on document order."""
    dated = [w for w in ws if w.get("wotd")]
    return max(dated, key=lambda w: w["wotd"]) if dated else None


def badge(c):
    return f'<span class="badge b-{c}">{LABEL.get(c, c)}</span>'


def origin_block(w, author):
    """The author's original, presented as the record it is."""
    who = f'{e(author["name"])}' if w["coiner"] == "marsita" else e(LABEL[w["coiner"]]).capitalize()
    if w["proposed"] == w["word"]:
        return (f'<div class="origin"><div class="k">As first written</div>'
                f'<div class="p">{e(w["proposed"])}</div>'
                f'<div class="same">Stands today exactly as it was first set down.</div></div>')
    return (f'<div class="origin"><div class="k">As first written</div>'
            f'<div class="p">{e(w["proposed"])}</div>'
            f'<div class="who">The original, by {who}. '
            f'The headword above is where it settled — the intention was here first.</div></div>')


def word_page(w, site, author):
    canon = f'{site}/{w["slug"]}/'
    s = w.get("score")
    score = ""
    if s:
        score = (f'<p class="score">slot {s["slot"]} · form {s["form"]} · clarity {s["clarity"]}'
                 f' · music {s["music"]} → {s["total"]}/25 · one reader\'s opinion, ranks nothing</p>')

    author_line = (f'<p class="byline">Coined by <b>{e(author["name"])}</b></p>'
                   if w["coiner"] == "marsita" else
                   f'<p class="byline">{e(LABEL[w["coiner"]]).capitalize()}</p>')

    stamp = ""
    if w.get("wotd"):
        stamp = (f'<p class="tag-line"><span class="stamp">Word of the day</span> '
                 f'<span class="pos">{e(pretty(w["wotd"]))}</span></p>')

    p = [f'<h1>{e(w["word"])}</h1>',
         author_line,
         stamp,
         f'<p class="tag-line"><span class="pos">{e(w["pos"])}</span> {badge(w["coiner"])}</p>',
         f'<p class="say">{e(w["say"])}</p>',
         origin_block(w, author),
         f'<p class="def">{e(w["def"])}</p>']

    im = w.get("image")
    og_image = None
    if im:
        og_image = f'{canon}{im["file"]}'
        cap = f'<figcaption>{e(im.get("caption"))}</figcaption>' if im.get("caption") else ""
        p.append(f'<figure><img src="{e(im["file"])}" alt="{e(im.get("alt"))}" '
                 f'loading="lazy">{cap}</figure>')
    if w.get("cite"):
        p.append(f'<p class="cite">{e(w["cite"])}</p>')
    if w.get("etym"):
        p.append(f'<p class="field"><b>Etymology</b><span>{e(w["etym"])}</span></p>')
    if w.get("note"):
        p.append(f'<p class="field"><b>Note</b><span>{e(w["note"])}</span></p>')
    p.append(score)

    sg = w.get("sightings", [])
    n = len(sg)
    p.append(f'<h2>Sightings in public <span class="count{"" if n else " zero"}">{n}</span></h2>')
    if sg:
        p.append('<p class="lede">Documented uses outside this project.</p>')
        for si in sg:
            link = f' — <a href="{e(si["url"])}">link</a>' if si.get("url") else ""
            p.append(f'<div class="sight"><div class="when">{e(si.get("date"))} · '
                     f'{e(si.get("where"))}{link}</div>'
                     f'<p class="what">{e(si.get("what"))}</p></div>')
    else:
        p.append('<div class="empty">No documented use yet. Every word in every dictionary '
                 'started exactly here, and the only thing that ever moved one was somebody '
                 'using it where other people could see.</div>')
    p.append(f'<a class="cta" href="{REPO}/issues/new?title=Sighting:+{e(w["slug"])}">'
             f'Document a sighting →</a>')

    ld = {"@context": "https://schema.org", "@type": "DefinedTerm",
          "name": w["word"], "description": w["def"], "url": canon,
          "alternateName": w["proposed"],
          "inDefinedTermSet": {"@type": "DefinedTermSet", "name": "Wordshaping", "url": site + "/"}}
    if w["coiner"] == "marsita":
        ld["creator"] = {"@type": "Person", "name": author["name"], "url": author.get("url", "")}

    if og_image:
        ld["image"] = og_image

    return page(f'{w["word"]} — Wordshaping', w["def"][:180], canon,
                "\n".join(p), 1, ld, og_image)


def lexicon_page(d, site, author):
    ws = d["words"]
    groups = [("The lexicon",
               "Every word has its own page and its own URL, where the original wording is preserved "
               "and public use is documented. Nothing here is removed for scoring badly.",
               [w for w in ws if w["status"] == "coined"]),
              ("Kept as a record",
               "Built on reasoning that later turned out to be wrong. Retained rather than deleted, "
               "because the reasoning is the point.",
               [w for w in ws if w["status"] == "deprecated"]),
              ("Words that turned out to be real",
               "Proposed here, then found already living in the language. Half the work of coining "
               "is discovering you did not need to.",
               [w for w in ws if w["status"] == "already-real"])]

    def block(lst):
        out = []
        for w in lst:
            n = len(w.get("sightings", []))
            seen = f' <span class="score">· {n} sighting{"" if n == 1 else "s"}</span>' if n else ""
            orig = ("" if w["proposed"] == w["word"] else
                    f'<div class="orig">first written <b>{e(w["proposed"])}</b></div>')
            out.append(f'<div class="entry"><a class="w" href="{w["slug"]}/">{e(w["word"])}</a> '
                       f'<span class="pos">{e(w["pos"])}</span> {badge(w["coiner"])}{seen}'
                       f'<p>{e(w["def"])}</p>{orig}</div>')
        return "\n".join(out)

    seams = "\n".join(
        f'<tr><td><code>{e(s["seam"])}</code></td><td>{e(s["truth"])}</td>'
        f'<td>{"<span class=win>" + e(s["verdict"]) + "</span>" if s["verdict"] != "does not parse" else e(s["verdict"])}</td></tr>'
        for s in d["seams"])
    rules = "\n".join(f'<p class="field"><b>{e(r["rule"])}</b><span>{e(r["body"])}</span></p>'
                      for r in d["rules"])

    body = (f'<h1>Wordshaping</h1>'
            f'<p class="byline">A lexicon by <b>{e(author["name"])}</b></p>'
            f'<p class="tag-line">Words that should already exist.</p>'
            f'<blockquote class="epi">Subtle nuances like this matter. '
            f'Good wordsmithing and wordshaping matters.</blockquote>')
    wd = word_of_the_day(ws)
    if wd:
        body += (f'<div class="wotd"><div class="k">Word of the day · {e(pretty(wd["wotd"]))}</div>'
                 f'<a class="w" href="{wd["slug"]}/">{e(wd["word"])}</a>'
                 f'<p>{e(wd["def"])}</p></div>')

    for title, lede, lst in groups:
        body += f'<h2>{title}</h2><p class="lede">{lede}</p>{block(lst)}'
    body += (f'<h2>Eight false seams</h2><p class="lede">Chunks heard as single suffixes where the '
             f'join actually falls elsewhere. Three of the eight are now in dictionaries or academic '
             f'use. Nothing distinguishes them from the other five except that enough people repeated '
             f'them.</p><table><thead><tr><th>heard as</th><th>actually</th><th>fate</th></tr></thead>'
             f'<tbody>{seams}</tbody></table>'
             f'<h2>How the words were made</h2>{rules}')

    ld = {"@context": "https://schema.org", "@type": "DefinedTermSet",
          "name": "Wordshaping", "url": site + "/",
          "description": "A lexicon of words that should already exist.",
          "creator": {"@type": "Person", "name": author["name"], "url": author.get("url", "")}}
    return page("Wordshaping — a lexicon of words that should already exist",
                "A lexicon of coined words, each with its own page: the original wording as first "
                "written, the etymology, and documented use in public.", site + "/", body, 0, ld)


def leaderboard_page(d, site):
    ws = [w for w in d["words"] if w["status"] in ("coined", "already-real")]
    ws.sort(key=lambda w: (-len(w.get("sightings", [])), w["word"]))
    total = sum(len(w.get("sightings", [])) for w in ws)
    live = sum(1 for w in ws if w.get("sightings"))
    rows = "".join(
        f'<div class="rank"><div class="n">{i}</div><div class="body">'
        f'<a href="../{w["slug"]}/">{e(w["word"])}</a> {badge(w["coiner"])}</div>'
        f'<div class="count{"" if w.get("sightings") else " zero"}">'
        f'{len(w.get("sightings", []))}</div></div>'
        for i, w in enumerate(ws, 1))
    body = (f'<h1>Leaderboard</h1><p class="tag-line">Ranked by documented use in public. '
            f'Nothing else.</p>'
            f'<blockquote class="epi">The only difference between an error and a new word '
            f'is uptake.</blockquote>'
            f'<p class="lede">This project found eight false seams — chunks heard as suffixes where '
            f'no join exists. Five do not parse in English. Three are in dictionaries. The difference '
            f'is not correctness, elegance, or anyone\'s opinion; it is that enough people repeated '
            f'the last three. So that is the only thing counted here.</p>'
            f'<p class="lede"><b>{live}</b> of <b>{len(ws)}</b> words have been seen in the wild, '
            f'across <b>{total}</b> documented sightings. Scores appear on each word\'s page and '
            f'sort nothing.</p><h2>Standings</h2>{rows}')
    return page("Leaderboard — Wordshaping",
                "Coined words ranked by documented use in public.",
                f"{site}/leaderboard/", body, 1)


def main():
    d = json.loads((ROOT / "words.json").read_text())
    site = d["site"]["url"].rstrip("/")
    author = d["author"]

    shutil.rmtree(ROOT / "w", ignore_errors=True)

    urls = [f"{site}/", f"{site}/leaderboard/"]
    missing = []
    for w in d["words"]:
        out = ROOT / w["slug"]
        out.mkdir(exist_ok=True)
        (out / "index.html").write_text(word_page(w, site, author))
        urls.append(f'{site}/{w["slug"]}/')
        # Images live beside their page, at /<slug>/<file>, and are never generated.
        im = w.get("image")
        if im and not (out / im["file"]).exists():
            missing.append(f'{w["slug"]}/{im["file"]}')

    (ROOT / "index.html").write_text(lexicon_page(d, site, author))
    lb = ROOT / "leaderboard"
    lb.mkdir(exist_ok=True)
    (lb / "index.html").write_text(leaderboard_page(d, site))

    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {site}/sitemap.xml\n")
    # CNAME is written only once DNS resolves — creating it early makes GitHub
    # redirect the working github.io URL to a domain that does not answer.
    #   dig +short wordshaping.org A   →   then: echo wordshaping.org > CNAME


    print(f"{len(d['words'])} word pages at /<slug>/  ·  lexicon  ·  leaderboard  ·  sitemap")
    wd = word_of_the_day(d["words"])
    if wd:
        print(f'word of the day: {wd["word"]} ({pretty(wd["wotd"])})')
    for m in missing:
        print(f"MISSING IMAGE: {m}")
    print(f"originals preserved: {sum(1 for w in d['words'] if w['proposed'] != w['word'])} "
          f"differ from their settled form")


if __name__ == "__main__":
    main()
