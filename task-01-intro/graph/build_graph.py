"""
Builds the relationship graph between glossary terms and the report.

For every term from terms.json it counts:
  - explicit mentions: the term itself is written in the text (or abbreviation/plural)
  - implicit mentions: the idea is there but described with other words
    (patterns are listed by hand in terms.json)

Text matched as explicit is masked before counting implicit, so nothing is counted twice.

Output:
  term_stats.json   - all numbers
  terms_graph.png   - picture: terms <-> report sections + bar chart
  terms_graph.html  - same graph, but you can hover a term to see its links

Usage: python build_graph.py
"""
import json
import re
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

HERE = Path(__file__).parent
REPORT = HERE.parent / "research.md"
TERMS = HERE / "terms.json"

EXPLICIT_COLOR = "#3b6ea8"
IMPLICIT_COLOR = "#e08a3c"


def load_terms():
    data = json.loads(TERMS.read_text(encoding="utf-8"))
    data.pop("_comment", None)
    return data


def split_sections(text):
    """Split report by '## ' headers. Text before the first header is 'Intro'."""
    text = re.sub(r"https?://\S+", " ", text)  # links are not part of the text
    sections = []
    current_name, current_lines = "Intro", []
    for line in text.splitlines():
        if line.startswith("# "):
            continue  # document title
        if line.startswith("## "):
            sections.append((current_name, "\n".join(current_lines)))
            current_name = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)
    sections.append((current_name, "\n".join(current_lines)))
    return sections


def short_name(section):
    # "1. Code generation and AI assistants in the IDE" -> "1. Code generation..."
    names = {
        "1": "1. Code assistants",
        "2": "2. Coding agents",
        "3": "3. Test generation",
        "4": "4. Code review & security",
        "5": "5. Docs & knowledge search",
        "6": "6. Support bots",
        "7": "7. Data analysis / SQL",
        "8": "8. Content generation",
    }
    m = re.match(r"(\d+)\.", section)
    if m and m.group(1) in names:
        return names[m.group(1)]
    return section


def count_in_text(text, patterns_explicit, patterns_implicit):
    explicit_hits, implicit_hits = [], []
    masked = text
    for p in patterns_explicit:
        for m in re.finditer(p, masked, flags=re.IGNORECASE):
            explicit_hits.append(m.group(0))
        masked = re.sub(p, lambda m: "#" * len(m.group(0)), masked, flags=re.IGNORECASE)
    for p in patterns_implicit:
        for m in re.finditer(p, masked, flags=re.IGNORECASE):
            implicit_hits.append(m.group(0))
        masked = re.sub(p, lambda m: "#" * len(m.group(0)), masked, flags=re.IGNORECASE)
    return explicit_hits, implicit_hits


def analyze():
    terms = load_terms()
    report = REPORT.read_text(encoding="utf-8")
    sections = split_sections(report)

    stats = {}
    for term, pats in terms.items():
        per_section = {}
        tot_e, tot_i = 0, 0
        examples_i = set()
        for name, body in sections:
            e, i = count_in_text(body, pats["explicit"], pats["implicit"])
            if e or i:
                per_section[short_name(name)] = {"explicit": len(e), "implicit": len(i)}
            tot_e += len(e)
            tot_i += len(i)
            examples_i.update(x.lower() for x in i)
        stats[term] = {
            "explicit": tot_e,
            "implicit": tot_i,
            "total": tot_e + tot_i,
            "sections": per_section,
            "implicit_examples": sorted(examples_i),
        }

    # which terms show up together in the same paragraph
    pairs = defaultdict(int)
    paragraphs = [p for _, body in sections for p in body.split("\n\n") if p.strip()]
    for p in paragraphs:
        present = []
        for term, pats in terms.items():
            e, i = count_in_text(p, pats["explicit"], pats["implicit"])
            if e or i:
                present.append(term)
        for a, b in combinations(sorted(present), 2):
            pairs[(a, b)] += 1
    co = [{"a": a, "b": b, "paragraphs": n} for (a, b), n in sorted(pairs.items(), key=lambda x: -x[1])]

    section_names = [short_name(n) for n, _ in sections]
    return {
        "method": "explicit = term written directly; implicit = concept described in other words "
                  "(hand-made patterns in terms.json). URLs are ignored.",
        "sections": section_names,
        "terms": stats,
        "cooccurrence": co,
    }


def layout(result):
    terms = sorted(result["terms"], key=lambda t: -result["terms"][t]["total"])
    sections = result["sections"]
    ty = {t: i for i, t in enumerate(terms)}
    # spread sections over the same height as terms
    n_t, n_s = len(terms), len(sections)
    sy = {s: (i + 0.5) * (n_t / n_s) - 0.5 for i, s in enumerate(sections)}
    return terms, sections, ty, sy


def draw_png(result, out):
    terms, sections, ty, sy = layout(result)
    data = result["terms"]

    fig = plt.figure(figsize=(17, 11))
    ax = fig.add_axes([0.02, 0.05, 0.62, 0.86])
    bx = fig.add_axes([0.73, 0.05, 0.25, 0.86])

    # graph part
    x_t, x_s = 0.0, 1.0
    for t in terms:
        for s, c in data[t]["sections"].items():
            for kind, color, style in (("explicit", EXPLICIT_COLOR, "-"), ("implicit", IMPLICIT_COLOR, "--")):
                n = c[kind]
                if not n:
                    continue
                rad = 0.08 if kind == "explicit" else -0.08
                arrow = FancyArrowPatch(
                    (x_t + 0.02, -ty[t]), (x_s - 0.02, -sy[s]),
                    connectionstyle=f"arc3,rad={rad}", arrowstyle="-",
                    linewidth=0.6 + 0.6 * min(n, 6), linestyle=style,
                    color=color, alpha=0.55,
                )
                ax.add_patch(arrow)
    for t in terms:
        d = data[t]
        size = 30 + 18 * d["total"]
        ax.scatter([x_t], [-ty[t]], s=size, color="#555", zorder=3)
        ax.text(x_t - 0.03, -ty[t], f"{t}  (E {d['explicit']} / I {d['implicit']})",
                ha="right", va="center", fontsize=10)
    for s in sections:
        ax.scatter([x_s], [-sy[s]], s=220, marker="s", color="#999", zorder=3)
        ax.text(x_s + 0.03, -sy[s], s, ha="left", va="center", fontsize=10.5, fontweight="bold")
    ax.set_xlim(-0.75, 1.55)
    ax.set_ylim(-len(terms) + 0.3, 0.8)
    ax.axis("off")
    ax.plot([], [], color=EXPLICIT_COLOR, lw=2, label="explicit mention")
    ax.plot([], [], color=IMPLICIT_COLOR, lw=2, ls="--", label="implicit mention")
    ax.legend(loc="upper left", frameon=False, fontsize=10, bbox_to_anchor=(0.0, 1.04))

    # bar part
    y = list(range(len(terms)))
    e = [data[t]["explicit"] for t in terms]
    i = [data[t]["implicit"] for t in terms]
    h = 0.38
    bx.barh([v - h / 2 for v in y], e, height=h, color=EXPLICIT_COLOR, label="explicit")
    bx.barh([v + h / 2 for v in y], i, height=h, color=IMPLICIT_COLOR, label="implicit")
    bx.set_yticks(y)
    bx.set_yticklabels(terms, fontsize=9)
    bx.invert_yaxis()
    bx.set_xlabel("mentions in research.md")
    bx.grid(axis="x", alpha=0.3)
    bx.spines[["top", "right"]].set_visible(False)
    bx.legend(frameon=False, loc="lower right")

    total_e = sum(e)
    total_i = sum(i)
    fig.suptitle(f"Glossary terms and where they are used in the report   "
                 f"(explicit: {total_e}, implicit: {total_i})", fontsize=14, x=0.02, ha="left")
    fig.savefig(out, dpi=120)
    plt.close(fig)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Glossary terms graph</title>
<style>
  body { font-family: Arial, sans-serif; margin: 20px; color: #222; }
  h1 { font-size: 20px; }
  p.note { color: #555; font-size: 13px; max-width: 900px; }
  svg text { font-size: 12px; }
  .edge { fill: none; opacity: 0.5; }
  .dim { opacity: 0.06 !important; }
  .term { cursor: pointer; }
  table { border-collapse: collapse; margin-top: 20px; font-size: 13px; }
  td, th { border: 1px solid #ccc; padding: 4px 8px; text-align: left; }
  th { background: #f2f2f2; }
  td.n { text-align: right; }
  .legend span { display: inline-block; width: 30px; height: 0; margin: 0 6px 3px 14px; vertical-align: middle; }
</style>
</head>
<body>
<h1>Glossary terms and where they are used in the report</h1>
<p class="note">Left: terms from glossary.md (E = explicit, I = implicit mentions). Right: sections of research.md.
Hover a term or a section to highlight its links. Explicit means the term itself is written in the text,
implicit means the idea is there but in other words (patterns in terms.json). Generated by build_graph.py.</p>
<div class="legend">
  <span style="border-top: 3px solid __EC__"></span>explicit
  <span style="border-top: 3px dashed __IC__"></span>implicit
</div>
<svg id="g" width="1000" height="__H__"></svg>

<h2 style="font-size:16px">Counts</h2>
<table id="t"><tr><th>Term</th><th>Explicit</th><th>Implicit</th><th>Total</th><th>Implicit examples</th></tr></table>

<h2 style="font-size:16px">Terms that often appear in the same paragraph</h2>
<table id="co"><tr><th>Term A</th><th>Term B</th><th>Paragraphs</th></tr></table>

<script>
const data = __DATA__;
const terms = __TERMS__;
const sections = data.sections;
const svg = document.getElementById("g");
const NS = "http://www.w3.org/2000/svg";
const rowH = 30, topY = 30, xT = 330, xS = 690;
const ty = {}, sy = {};
terms.forEach((t, i) => ty[t] = topY + i * rowH);
const step = (terms.length * rowH) / sections.length;
sections.forEach((s, i) => sy[s] = topY + (i + 0.5) * step - rowH / 2);

function el(name, attrs, text) {
  const e = document.createElementNS(NS, name);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (text) e.textContent = text;
  svg.appendChild(e);
  return e;
}

const edges = [];
terms.forEach(t => {
  const secs = data.terms[t].sections;
  for (const s in secs) {
    [["explicit", "__EC__", "", 12], ["implicit", "__IC__", "6,4", -12]].forEach(([kind, color, dash, bend]) => {
      const n = secs[s][kind];
      if (!n) return;
      const y1 = ty[t], y2 = sy[s];
      const mx = (xT + xS) / 2;
      const path = el("path", {
        d: `M${xT + 8},${y1} C${mx},${y1 + bend} ${mx},${y2 + bend} ${xS - 8},${y2}`,
        stroke: color, "stroke-width": 1 + Math.min(n, 6) * 0.9,
        "stroke-dasharray": dash, class: "edge"
      });
      const title = document.createElementNS(NS, "title");
      title.textContent = `${t} -> ${s}: ${n} ${kind}`;
      path.appendChild(title);
      edges.push({t, s, path});
    });
  }
});

function highlight(t, s) {
  edges.forEach(e => {
    const on = (t && e.t === t) || (s && e.s === s);
    e.path.classList.toggle("dim", !on);
  });
}
function reset() { edges.forEach(e => e.path.classList.remove("dim")); }

terms.forEach(t => {
  const d = data.terms[t];
  const r = 4 + Math.sqrt(d.total) * 2;
  const g1 = el("circle", {cx: xT, cy: ty[t], r: r, fill: "#555", class: "term"});
  const g2 = el("text", {x: xT - r - 6, y: ty[t] + 4, "text-anchor": "end", class: "term"},
    `${t}  (E ${d.explicit} / I ${d.implicit})`);
  [g1, g2].forEach(x => { x.onmouseenter = () => highlight(t, null); x.onmouseleave = reset; });
});
sections.forEach(s => {
  const r1 = el("rect", {x: xS - 7, y: sy[s] - 7, width: 14, height: 14, fill: "#999", class: "term"});
  const t1 = el("text", {x: xS + 14, y: sy[s] + 4, "font-weight": "bold", class: "term"}, s);
  [r1, t1].forEach(x => { x.onmouseenter = () => highlight(null, s); x.onmouseleave = reset; });
});

const table = document.getElementById("t");
terms.forEach(t => {
  const d = data.terms[t];
  const tr = document.createElement("tr");
  tr.innerHTML = `<td>${t}</td><td class="n">${d.explicit}</td><td class="n">${d.implicit}</td>` +
                 `<td class="n">${d.total}</td><td>${d.implicit_examples.join(", ")}</td>`;
  table.appendChild(tr);
});
const co = document.getElementById("co");
data.cooccurrence.slice(0, 15).forEach(p => {
  const tr = document.createElement("tr");
  tr.innerHTML = `<td>${p.a}</td><td>${p.b}</td><td class="n">${p.paragraphs}</td>`;
  co.appendChild(tr);
});
</script>
</body>
</html>
"""


def write_html(result, out):
    terms, _, _, _ = layout(result)
    html = (HTML_TEMPLATE
            .replace("__DATA__", json.dumps(result))
            .replace("__TERMS__", json.dumps(terms))
            .replace("__EC__", EXPLICIT_COLOR)
            .replace("__IC__", IMPLICIT_COLOR)
            .replace("__H__", str(40 + len(terms) * 30)))
    out.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    result = analyze()
    (HERE / "term_stats.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    draw_png(result, HERE / "terms_graph.png")
    write_html(result, HERE / "terms_graph.html")

    print(f"{'term':<24}{'explicit':>9}{'implicit':>9}")
    for t, d in sorted(result["terms"].items(), key=lambda x: -x[1]["total"]):
        print(f"{t:<24}{d['explicit']:>9}{d['implicit']:>9}")
