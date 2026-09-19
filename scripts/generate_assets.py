"""
Generates the SVG assets referenced by README.md, into profile-3d-contrib/.
Some are static (banner, link strip, skills flow, build map) and rebuilt from
the CONTENT dict below. One (language-pulse.svg) is built from live GitHub
API data, so it changes automatically as your repos and languages change.

Run manually with:  python scripts/generate_assets.py
Runs automatically via .github/workflows/update-profile.yml
"""

import os
import sys
from collections import defaultdict

import requests

# ---- Your content — edit this, not the SVG builders below --------------
USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER", "BRIAN-pixel275")

TAGLINE = "Hi, I'm Brian. I build finance & POS systems that work."
LINKS = [
    ("Portfolio", "https://brianportfolio-eight.vercel.app/"),
    ("LinkedIn", "https://www.linkedin.com/in/brian-muchiru-b0b057356/"),
    ("Email", "mailto:brayo2933@gmail.com"),
    ("Kreative Studio", "#"),
]
PRIMARY_LINK = LINKS[0][1]

SKILLS = [
    "React", "Vite", "Next.js", "Tailwind CSS", "JavaScript", "Java",
    "Node.js", "Firebase", "Supabase", "SQLite", "Git", "Netlify", "Vercel",
]

BUILD_MAP = {
    "Fintech": ["ClubVault", "FinnanceClub", "CreditScore Africa", "Chama Finance"],
    "POS Systems": ["SmartPOS Lite", "Anns Interior Decors POS"],
    "PWAs": ["Campus Budget", "FinnanceClub"],
    "Client Sites": ["Elevara Legacy"],
}

# ---- Palette -------------------------------------------------------------
BG = "#0A0E17"
SURFACE = "#101828"
ACCENT = "#00E5CC"
ACCENT_DIM = "#0B8C7D"
TEXT = "#E6EDF3"
TEXT_MUTED = "#8B98A9"
LANG_COLORS = ["#00E5CC", "#5EEAD4", "#2DD4BF", "#0EA5A0", "#0B8C7D", "#065F5A"]

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "profile-3d-contrib")


def esc(text):
    """Escape text for safe inclusion inside SVG/XML content."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def write_svg(name, content):
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"wrote {path}")


# ---- 1. Intro banner -------------------------------------------------------
def build_intro_banner():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 220" width="1200" height="220">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{BG}"/>
      <stop offset="100%" stop-color="{SURFACE}"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="220" fill="url(#bg)"/>
  <g stroke="{ACCENT_DIM}" stroke-opacity="0.25" stroke-width="1">
    <line x1="0" y1="55" x2="1200" y2="55"/>
    <line x1="0" y1="165" x2="1200" y2="165"/>
    <line x1="300" y1="0" x2="300" y2="220"/>
    <line x1="900" y1="0" x2="900" y2="220"/>
  </g>
  <circle cx="300" cy="55" r="4" fill="{ACCENT}"/>
  <circle cx="900" cy="165" r="4" fill="{ACCENT}"/>
  <text x="60" y="100" font-family="Consolas, Menlo, monospace" font-size="34" fill="{TEXT}" font-weight="600">Brian Muchiru</text>
  <text x="60" y="140" font-family="Consolas, Menlo, monospace" font-size="18" fill="{ACCENT}">{esc(TAGLINE)}</text>
  <text x="60" y="170" font-family="Consolas, Menlo, monospace" font-size="13" fill="{TEXT_MUTED}">Economics &amp; Finance @ Kenyatta University &#183; Founder, Kreative Studio</text>
</svg>'''


# ---- 2. Link strip ----------------------------------------------------------
def build_link_strip():
    pills = []
    x = 40
    for label, _ in LINKS:
        w = 46 + len(label) * 9
        pills.append(f'''
    <rect x="{x}" y="20" width="{w}" height="40" rx="20" fill="{SURFACE}" stroke="{ACCENT_DIM}" stroke-width="1.5"/>
    <circle cx="{x + 22}" cy="40" r="5" fill="{ACCENT}"/>
    <text x="{x + 38}" y="45" font-family="Consolas, Menlo, monospace" font-size="15" fill="{TEXT}">{esc(label)}</text>''')
        x += w + 16

    total_width = x + 20
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_width} 80" width="{total_width}" height="80">
  <rect width="{total_width}" height="80" fill="{BG}"/>
  {"".join(pills)}
</svg>'''


# ---- 3. Skills flow (animated marquee) --------------------------------------
def build_skills_flow():
    gap = 40
    items = []
    x = 0
    widths = []
    for skill in SKILLS:
        w = 20 + len(skill) * 10
        widths.append(w)

    def render_row(offset_x):
        row = []
        cx = offset_x
        for skill, w in zip(SKILLS, widths):
            row.append(f'''
    <rect x="{cx}" y="15" width="{w}" height="34" rx="17" fill="{SURFACE}" stroke="{ACCENT_DIM}"/>
    <text x="{cx + w/2}" y="37" text-anchor="middle" font-family="Consolas, Menlo, monospace" font-size="14" fill="{ACCENT}">{esc(skill)}</text>''')
            cx += w + gap
        return "".join(row), cx

    row1, end_x = render_row(0)
    row2, _ = render_row(end_x)
    loop_width = end_x

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 64" width="1200" height="64">
  <rect width="1200" height="64" fill="{BG}"/>
  <clipPath id="clip"><rect width="1200" height="64"/></clipPath>
  <g clip-path="url(#clip)">
    <g>
      {row1}
      {row2}
      <animateTransform attributeName="transform" type="translate" from="0,0" to="-{loop_width},0" dur="{max(loop_width/60, 12):.0f}s" repeatCount="indefinite"/>
    </g>
  </g>
</svg>'''


# ---- 4. Language pulse (from live GitHub API data) --------------------------
def fetch_language_totals():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USERNAME}-profile-readme-script",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    totals = defaultdict(int)
    page = 1
    while True:
        resp = requests.get(
            f"https://api.github.com/users/{USERNAME}/repos",
            params={"per_page": 100, "page": page},
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        for repo in batch:
            if repo.get("fork"):
                continue
            lang_resp = requests.get(repo["languages_url"], headers=headers, timeout=30)
            if lang_resp.ok:
                for lang, bytes_count in lang_resp.json().items():
                    totals[lang] += bytes_count
        page += 1

    return totals


def build_language_pulse(totals):
    if not totals:
        totals = {"JavaScript": 1}  # fallback so the SVG isn't empty pre-first-run

    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:6]
    grand_total = sum(v for _, v in ranked)

    bars = []
    y = 30
    for i, (lang, value) in enumerate(ranked):
        pct = value / grand_total * 100
        bar_w = pct / 100 * 700
        color = LANG_COLORS[i % len(LANG_COLORS)]
        bars.append(f'''
    <text x="20" y="{y + 15}" font-family="Consolas, Menlo, monospace" font-size="13" fill="{TEXT}">{esc(lang)}</text>
    <rect x="180" y="{y}" width="700" height="18" rx="9" fill="{SURFACE}"/>
    <rect x="180" y="{y}" width="{bar_w:.0f}" height="18" rx="9" fill="{color}"/>
    <text x="{180 + 700 + 12}" y="{y + 15}" font-family="Consolas, Menlo, monospace" font-size="12" fill="{TEXT_MUTED}">{pct:.1f}%</text>''')
        y += 34

    height = y + 10
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 {height}" width="960" height="{height}">
  <rect width="960" height="{height}" fill="{BG}"/>
  {"".join(bars)}
</svg>'''


# ---- 5. Build map -------------------------------------------------------------
def wrap_projects(projects, max_chars=28):
    """Greedily wrap a list of project names into lines no wider than max_chars."""
    lines, current = [], ""
    for p in projects:
        candidate = f"{current}, {p}" if current else p
        if len(candidate) > max_chars and current:
            lines.append(current)
            current = p
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def build_build_map():
    categories = list(BUILD_MAP.items())
    box_w, box_h_base = 260, 40
    line_h = 16

    # Fixed compass layout so nothing collides with the center node or the edges.
    center = (600, 220)
    positions = [
        (center[0], 70),          # top
        (center[0] + 380, center[1]),   # right
        (center[0], 370),         # bottom
        (center[0] - 380, center[1]),   # left
    ]

    nodes = []
    for (category, projects), (nx, ny) in zip(categories, positions):
        lines = wrap_projects(projects)
        box_h = box_h_base + line_h * len(lines)

        nodes.append(
            f'<line x1="{center[0]}" y1="{center[1]}" x2="{nx}" y2="{ny}" '
            f'stroke="{ACCENT_DIM}" stroke-width="1.5"/>'
        )

        text_lines = "".join(
            f'<text x="{nx}" y="{ny - box_h/2 + 40 + i*line_h}" text-anchor="middle" '
            f'font-family="Consolas, Menlo, monospace" font-size="10" fill="{TEXT_MUTED}">{esc(line)}</text>'
            for i, line in enumerate(lines)
        )

        nodes.append(f'''
    <rect x="{nx - box_w/2:.0f}" y="{ny - box_h/2:.0f}" width="{box_w}" height="{box_h}" rx="10" fill="{SURFACE}" stroke="{ACCENT}" stroke-width="1.5"/>
    <text x="{nx}" y="{ny - box_h/2 + 24:.0f}" text-anchor="middle" font-family="Consolas, Menlo, monospace" font-size="15" fill="{ACCENT}" font-weight="600">{esc(category)}</text>
    {text_lines}''')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 460" width="1200" height="460">
  <rect width="1200" height="460" fill="{BG}"/>
  {"".join(nodes)}
  <circle cx="{center[0]}" cy="{center[1]}" r="46" fill="{SURFACE}" stroke="{ACCENT}" stroke-width="2"/>
  <text x="{center[0]}" y="{center[1]+5}" text-anchor="middle" font-family="Consolas, Menlo, monospace" font-size="16" fill="{TEXT}" font-weight="600">BRIAN</text>
  <text x="600" y="440" text-anchor="middle" font-family="Consolas, Menlo, monospace" font-size="12" fill="{TEXT_MUTED}">what I build</text>
</svg>'''


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    write_svg("intro-banner.svg", build_intro_banner())
    write_svg("link-strip.svg", build_link_strip())
    write_svg("skills-flow.svg", build_skills_flow())
    write_svg("build-map.svg", build_build_map())

    try:
        totals = fetch_language_totals()
    except requests.RequestException as exc:
        print(f"Warning: couldn't fetch language data ({exc}); using fallback.", file=sys.stderr)
        totals = {}
    write_svg("language-pulse.svg", build_language_pulse(totals))


if __name__ == "__main__":
    main()
