#!/usr/bin/env python3
"""
Build wordshaping.org from words.json.

    python3 build.py

Generates:
    lexicon.html        the lexicon, linking to every word page
    leaderboard.html    words ranked by documented public use
    w/<slug>.html       one page per word

Sightings are the only thing the leaderboard ranks. To add one, put an
entry in a word's "sightings" array in words.json and re-run this script.
"""

import json
import os
import html
from pathlib import Path

ROOT = Path(__file__).parent
REPO = "https://github.com/PlanetaryCouncil/wordshaping.org"

CSS = """
:root{--bg:#fbfaf8;--fg:#1a1a18;--muted:#6f6e68;--faint:#94928b;--line:#e3e0d9;
--panel:#fff;--accent:#8a5a2b;--y-bg:#fdf3e3;--y-fg:#8a5a2b;--m-bg:#eef1f5;--m-fg:#4a5768;
--w-bg:#e9f0e7;--w-fg:#4a6b45}
@media (prefers-color-scheme:dark){:root{--bg:#151519;--fg:#e9e7e2;--muted:#9d9a92;
--faint:#77746d;--line:#31313a;--panel:#1c1c22;--accent:#d9a86c;--y-bg:#3a2c17;
--y-fg:#e8bd82;--m-bg:#242a33;--m-fg:#9fb2c9;--w-bg:#222e21;--w-fg:#9dc094}}
:root[data-theme=dark]{--bg:#151519;--fg:#e9e7e2;--muted:#9d9a92;--faint:#77746d;
--line:#31313a;--panel:#1c1c22;--accent:#d9a86c;--y-bg:#3a2c17;--y-fg:#e8bd82;
--m-bg:#242a33;--m-fg:#9fb2c9;--w-bg:#222e21;--w-fg:#9dc094}
:root[data-theme=light]{--bg:#fbfaf8;--fg:#1a1a18;--muted:#6f6e68;--faint:#94928b;
--line:#e3e0d9;--panel:#fff;--accent:#8a5a2b;--y-bg:#fdf3e3;--y-fg:#8a5a2b;
--m-bg:#eef1f5;--m-fg:#4a5768;--w-bg:#e9f0e7;--w-fg:#4a6b45}
*{box-sizing:border-box}
body{margin:0;padding:2.5rem 1.5rem 6rem;background:var(--bg);color:var(--fg);
font:17px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;
overflow-x:hidden}
.wrap{max-width:760px;margin:0 auto}
nav{font-size:.85rem;margin-bottom:2.5rem;color:var(--faint)}
nav a{color:var(--accent);text-decoration:none;margin-right:1.1rem}
nav a:hover{text-decoration:underline}
h1{font-family:Georgia,"Iowan Old Style",serif;font-size:clamp(2rem,5.5vw,3rem);
letter-spacing:-.02em;margin:0 0 .3rem;font-weight:400;word-break:break-word}
.tag-line{color:var(--muted);margin:0 0 2rem}
blockquote.epi{margin:0 0 2.5rem;padding:.1rem 0 .1rem 1.2rem;border-left:2px solid var(--accent);
font-family:Georgia,serif;font-size:1.15rem;line-height:1.5}
h2{font-family:Georgia,serif;font-weight:400;font-size:1.4rem;margin:3rem 0 .3rem}
h2+.lede{color:var(--muted);font-size:.92rem;margin:0 0 1.4rem;max-width:62ch}
.badge{display:inline-block;font-size:.66rem;text-transform:uppercase;letter-spacing:.07em;
font-weight:700;padding:.15rem .45rem;border-radius:3px;vertical-align:2px}
.b-marsita{background:var(--y-bg);color:var(--y-fg)}
.b-claude{background:var(--m-bg);color:var(--m-fg)}
.b-wild{background:var(--w-bg);color:var(--w-fg)}
.pos{font-style:italic;color:var(--faint);font-size:.92rem}
.say{color:var(--faint);font-size:.82rem;letter-spacing:.04em;margin:0 0 1.4rem}
.def{font-size:1.12rem;margin:0 0 1.2rem}
.cite{font-family:Georgia,serif;font-style:italic;color:var(--muted);padding-left:1rem;
border-left:2px solid var(--line);margin:0 0 1.6rem}
.field{margin:0 0 1.1rem;font-size:.94rem}
.field b{display:block;font-family:Georgia,serif;font-size:.98rem;margin-bottom:.1rem}
.field span{color:var(--muted)}
.entry{border-top:1px solid var(--line);padding:1.3rem 0}
.entry:last-of-type{border-bottom:1px solid var(--line)}
.entry a.w{font-family:Georgia,serif;font-size:1.35rem;font-weight:600;color:var(--fg);
text-decoration:none;word-break:break-word}
.entry a.w:hover{color:var(--accent)}
.entry p{margin:.3rem 0 0;color:var(--muted);font-size:.94rem}
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
.sight{border-left:2px solid var(--accent);padding:.1rem 0 .1rem 1rem;margin:0 0 1rem}
.sight .when{font-size:.78rem;color:var(--faint);letter-spacing:.04em;text-transform:uppercase}
.sight .what{margin:.15rem 0 0}
.empty{background:var(--panel);border:1px dashed var(--line);border-radius:8px;
padding:1.3rem 1.4rem;color:var(--muted);font-size:.94rem}
.cta{display:inline-block;margin-top:.8rem;padding:.5rem .9rem;border:1px solid var(--accent);
border-radius:5px;color:var(--accent);text-decoration:none;font-size:.88rem;font-weight:600}
.cta:hover{background:var(--accent);color:var(--bg)}
.score{font-size:.8rem;color:var(--faint);font-variant-numeric:tabular-nums}
table{border-collapse:collapse;width:100%;font-size:.9rem;margin-top:1rem}
th,td{text-align:left;padding:.55rem .7rem;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:.72rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
td code{font-size:.9em}
.win{color:var(--accent);font-weight:700;font-size:.75rem;letter-spacing:.05em}
footer{margin-top:4rem;padding-top:1.4rem;border-top:1px solid var(--line);
color:var(--faint);font-size:.85rem}
footer a{color:var(--accent)}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.87em}
"""

COINER_LABEL = {"marsita": "coined here", "claude": "suggested", "wild": "found in the wild"}


def e(s):
    return html.escape(s or "")


def page(title, body, depth=0):
    up = "../" * depth
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<style>{CSS}</style>
</head>
<body><div class="wrap">
<nav><a href="{up}lexicon.html">the lexicon</a><a href="{up}leaderboard.html">leaderboard</a><a href="{up}index.html">working table</a><a href="{REPO}">source</a></nav>
{body}
<footer>
<a href="{up}lexicon.html">wordshaping</a> — a lexicon of words that should already exist.<br>
Sightings are the only thing ranked here. Add one by
<a href="{REPO}/issues/new">opening an issue</a> or editing <code>words.json</code>.
</footer>
</div></body>
</html>
"""


def badge(coiner):
    return f'<span class="badge b-{coiner}">{COINER_LABEL.get(coiner, coiner)}</span>'


def word_page(w):
    s = w.get("score")
    score_line = ""
    if s:
        score_line = (
            f'<p class="score">slot {s["slot"]} · form {s["form"]} · clarity {s["clarity"]}'
            f' · music {s["music"]} &nbsp;→&nbsp; {s["total"]}/25 &nbsp;·&nbsp; '
            f'one reader\'s opinion, ranks nothing</p>'
        )

    parts = [
        f'<h1>{e(w["word"])}</h1>',
        f'<p class="tag-line"><span class="pos">{e(w["pos"])}</span> &nbsp; {badge(w["coiner"])}</p>',
        f'<p class="say">{e(w["say"])}</p>',
        f'<p class="def">{e(w["def"])}</p>',
    ]
    if w.get("cite"):
        parts.append(f'<p class="cite">{e(w["cite"])}</p>')
    if w.get("etym"):
        parts.append(f'<p class="field"><b>Etymology</b><span>{e(w["etym"])}</span></p>')
    if w.get("note"):
        parts.append(f'<p class="field"><b>Note</b><span>{e(w["note"])}</span></p>')
    parts.append(score_line)

    sightings = w.get("sightings", [])
    n = len(sightings)
    parts.append(f'<h2>Sightings in public &nbsp;<span class="count{"" if n else " zero"}">{n}</span></h2>')

    if sightings:
        parts.append('<p class="lede">Documented uses outside this project.</p>')
        for si in sightings:
            link = f' — <a href="{e(si["url"])}">link</a>' if si.get("url") else ""
            parts.append(
                f'<div class="sight"><div class="when">{e(si.get("date",""))} · '
                f'{e(si.get("where",""))}{link}</div>'
                f'<p class="what">{e(si.get("what",""))}</p></div>'
            )
    else:
        parts.append(
            '<div class="empty">No documented use yet. Every word in every dictionary '
            'started here, and the only thing that moved it was somebody using it where '
            'other people could see.</div>'
        )

    parts.append(
        f'<a class="cta" href="{REPO}/issues/new?title=Sighting:+{e(w["slug"])}">'
        f'Document a sighting →</a>'
    )
    return page(f'{w["word"]} — wordshaping', "\n".join(parts), depth=1)


def lexicon_page(data):
    words = data["words"]
    coined = [w for w in words if w["status"] == "coined"]
    depr = [w for w in words if w["status"] == "deprecated"]
    real = [w for w in words if w["status"] == "already-real"]

    def block(ws):
        out = []
        for w in ws:
            n = len(w.get("sightings", []))
            seen = f' &nbsp;<span class="score">{n} sighting{"" if n==1 else "s"}</span>' if n else ""
            out.append(
                f'<div class="entry"><a class="w" href="w/{w["slug"]}.html">{e(w["word"])}</a> '
                f'<span class="pos">{e(w["pos"])}</span> {badge(w["coiner"])}{seen}'
                f'<p>{e(w["def"])}</p></div>'
            )
        return "\n".join(out)

    seams = "\n".join(
        f'<tr><td><code>{e(s["seam"])}</code></td><td>{e(s["truth"])}</td>'
        f'<td>{"<span class=win>"+e(s["verdict"])+"</span>" if s["verdict"]!="does not parse" else e(s["verdict"])}</td></tr>'
        for s in data["seams"]
    )
    rules = "\n".join(
        f'<p class="field"><b>{e(r["rule"])}</b><span>{e(r["body"])}</span></p>'
        for r in data["rules"]
    )

    body = f"""
<h1>Wordshaping</h1>
<p class="tag-line">A lexicon of words that should already exist.</p>
<blockquote class="epi">Subtle nuances like this matter. Good wordsmithing and wordshaping matters.</blockquote>

<h2>The lexicon</h2>
<p class="lede">Every word has its own page, where its use in public is documented.
Nothing here is removed for scoring badly.</p>
{block(coined)}

<h2>Kept as a record</h2>
<p class="lede">Built on reasoning that later turned out to be wrong. Retained rather than deleted,
because the reasoning is the point.</p>
{block(depr)}

<h2>Words that turned out to be real</h2>
<p class="lede">Proposed here, then found already living in the language.
Half the work of coining is discovering you did not need to.</p>
{block(real)}

<h2>Eight false seams</h2>
<p class="lede">Chunks heard as single suffixes where the join actually falls elsewhere.
Three of the eight are now in dictionaries or academic use. Nothing distinguishes them
from the other five except that enough people repeated them.</p>
<table><thead><tr><th>heard as</th><th>actually</th><th>fate</th></tr></thead>
<tbody>{seams}</tbody></table>

<h2>How the words were made</h2>
{rules}
"""
    return page("Wordshaping — a lexicon", body)


def leaderboard_page(data):
    words = [w for w in data["words"] if w["status"] in ("coined", "already-real")]
    words.sort(key=lambda w: (-len(w.get("sightings", [])), w["word"]))
    total = sum(len(w.get("sightings", [])) for w in words)
    live = sum(1 for w in words if w.get("sightings"))

    rows = []
    for i, w in enumerate(words, 1):
        n = len(w.get("sightings", []))
        cls = "" if n else " zero"
        rows.append(
            f'<div class="rank"><div class="n">{i}</div>'
            f'<div class="body"><a href="w/{w["slug"]}.html">{e(w["word"])}</a> '
            f'{badge(w["coiner"])}</div>'
            f'<div class="count{cls}">{n}</div></div>'
        )

    body = f"""
<h1>Leaderboard</h1>
<p class="tag-line">Ranked by documented use in public. Nothing else.</p>

<blockquote class="epi">The only difference between an error and a new word is uptake.</blockquote>

<p class="lede">This project found eight false seams — chunks heard as suffixes where no join
exists. Five of them do not parse in English. Three are in dictionaries. The difference
between those groups is not correctness, elegance, or anyone's opinion; it is that enough
people repeated the last three. So that is the only thing counted here.</p>

<p class="lede"><b>{live}</b> of <b>{len(words)}</b> words have been seen in the wild,
across <b>{total}</b> documented sightings. Scores appear on each word's page and sort nothing.</p>

<h2>Standings</h2>
{"".join(rows)}
"""
    return page("Leaderboard — wordshaping", body)


def main():
    data = json.loads((ROOT / "words.json").read_text())
    wdir = ROOT / "w"
    wdir.mkdir(exist_ok=True)

    for w in data["words"]:
        (wdir / f'{w["slug"]}.html').write_text(word_page(w))

    (ROOT / "lexicon.html").write_text(lexicon_page(data))
    (ROOT / "leaderboard.html").write_text(leaderboard_page(data))

    n = len(data["words"])
    seen = sum(len(w.get("sightings", [])) for w in data["words"])
    print(f"built {n} word pages + lexicon + leaderboard  ({seen} sightings on record)")


if __name__ == "__main__":
    main()
