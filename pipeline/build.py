"""4단계: 수집 결과(data/<city>/)로 공개용 데이터 파일과 페이지를 만든다.

- docs/<city>/index.html, docs/<city>/data/*.json : 도시별 페이지 (GitHub Pages 공개)
- docs/index.html                                  : 도시 목록 페이지
- dist/<city>_artifact_index.html                  : Claude 대시보드에 올리는 페이지 본문

사용법: python3 build.py            # 데이터가 준비된 모든 도시 + 도시 목록
        python3 build.py --city okinawa
"""
import json, sys, shutil, datetime as dt, html
from naver import clean, ROOT
from cities import CITIES, load


def ko_date(s):
    g = dt.date.fromisoformat(s)
    return f"{g.year}년 {g.month}월 {g.day}일"


def build_city(C):
    src = ROOT / "data" / C.SLUG
    D = json.loads((src / "places.json").read_text(encoding="utf-8"))
    raw = json.loads((src / "raw.json").read_text(encoding="utf-8"))
    pk_path = ROOT / "web/picks" / f"{C.SLUG}.json"
    picks = json.loads(pk_path.read_text(encoding="utf-8")) if pk_path.exists() else []
    months = D["months"]
    assert len(months) == 36, f"{C.NAME}: trend.py 를 먼저 실행해 36개월 추세를 만들어 주세요"

    al = {n: a for n, c, r, a in C.PLACES}
    cats = {n: (c, r) for n, c, r, a in C.PLACES}  # 분류·지역은 설정 파일 기준
    T = [(clean(i["title"]) + clean(i["description"])).replace(" ", "").lower() for i in raw]
    P = [p for p in D["places"] if p["name"] in al and "trend" in p]

    places = []
    for p in P:
        a = [x.lower() for x in al[p["name"]]]
        places.append({
            "name": p["name"], "cat": cats[p["name"]][0], "region": cats[p["name"]][1],
            "steady": p["steady"], "vol36": p["vol36"], "consistency": p["consistency"],
            "yr1": p["yearAvg"][0], "yr2": p["yearAvg"][1], "yr3": p["yearAvg"][2],
            "searchIndex": p["searchIndex"], "relYoy": p["relYoy"],
            "blog30": p["blog30"], "blog30est": p["blog30est"],
            "mentions": sum(1 for t in T if any(x in t for x in a)),
            "blogTotal": p["blogTotal"], "cafeTotal": p["cafeTotal"],
            "mapQuery": C.MAPQ.get(p["name"]), "trendKeywords": ", ".join(p["trendKw"]),
        })
    trend = [{"name": p["name"], "month": m[:7], "index": v} for p in P for m, v in zip(months, p["trend"])]
    trend += [{"name": f"{C.NAME} 전체", "month": m[:7], "index": v} for m, v in zip(months, D["cityTrend"])]
    posts = []
    for p in P:
        for kind, lst in (("블로그", p["posts"]), ("카페", p["cafe"])):
            for x in lst:
                posts.append({"name": p["name"], "type": kind, "title": x["title"], "summary": x["desc"],
                              "link": x["link"], "date": x["date"], "author": x["src"]})
    names = {p["name"] for p in places}
    missing = [k["name"] for k in picks if k["name"] not in names]
    if missing:
        print(f"경고: picks/{C.SLUG}.json 에 장소 목록에 없는 이름이 있어요 →", missing)
    stats = [{"collected": len(raw), "blog": sum(i["_kind"] == "blog" for i in raw), "cafe": sum(i["_kind"] == "cafearticle" for i in raw),
              "places": len(places), "cityYoy": D["cityYoy"], "collectedOn": D["generated"],
              "trendFrom": months[0][:7], "trendTo": months[-1][:7]}]

    out = ROOT / "docs" / C.SLUG / "data"
    out.mkdir(parents=True, exist_ok=True)
    for n, o in (("places", places), ("trend", trend), ("posts", posts), ("stats", stats), ("picks", picks)):
        (out / f"{n}.json").write_text(json.dumps(o, ensure_ascii=False), encoding="utf-8")
    print(f"[{C.NAME}] docs/{C.SLUG}/data  장소 {len(places)} · 추세 {len(trend)} · 글 {len(posts)} · 픽 {len(picks)}")

    # 기간·도시 문구 채우기
    ym = lambda s: (int(s[:4]), int(s[5:7]))
    ko = lambda s: f"{ym(s)[0]}년 {ym(s)[1]}월"
    short = lambda a, b: f"{a[2:4]}.{a[5:7]}~{b[2:4]}.{b[5:7]}"
    r0, r1 = months[-3], months[-1]
    recent = f"{ym(r0)[0]}년 {ym(r0)[1]}~{ym(r1)[1]}월" if ym(r0)[0] == ym(r1)[0] else f"{ko(r0)}~{ko(r1)}"
    ctx = " 또는 ".join(f'"{c}"' for c in C.CONTEXT[:3])
    fill = {"{{CITY}}": C.NAME, "{{PREFIX}}": C.PREFIX, "{{ANCHOR}}": C.ANCHOR[0], "{{CONTEXT_KO}}": ctx,
            "{{NQUERIES}}": str(len(C.QUERIES) + len(C.QUERIES_EXTRA)),
            "{{CHAIN_NOTE}}": html.escape(C.CHAIN_NOTE, quote=False), "{{EXCLUDE_NOTE}}": html.escape(C.EXCLUDE_NOTE, quote=False),
            "{{COLLECTED_KO}}": ko_date(D["generated"]), "{{FROM_KO}}": ko(months[0]), "{{TO_KO}}": ko(months[-1]),
            "{{Y1}}": short(months[0], months[11]), "{{Y2}}": short(months[12], months[23]), "{{Y3}}": short(months[24], months[35]),
            "{{RECENT3_KO}}": recent}
    page = (ROOT / "web/page.template.html").read_text(encoding="utf-8")
    if not picks:  # 픽이 없는 도시는 silk pick! 섹션을 뺀다
        a0 = page.index('  <section class="okr-sec" id="picks">'); a1 = page.index("</section>", a0) + len("</section>\n")
        page = page[:a0] + page[a1:].lstrip("\n")
    head = (ROOT / "web/standalone_head.html").read_text(encoding="utf-8")
    for k, v in fill.items():
        page = page.replace(k, v); head = head.replace(k, v)

    (ROOT / "dist").mkdir(exist_ok=True)
    artifact = page.replace('    <p class="okr-meta"><a class="okr-map" href="../">← 도시 목록</a></p>\n', "").replace("<!--OTHER_CITIES-->\n", "")
    (ROOT / "dist" / f"{C.SLUG}_artifact_index.html").write_text(artifact, encoding="utf-8")
    body = page.replace('<meta name="dash-one-writer">\n', "")
    foot = (f'<p class="okr-foot">데이터: 네이버 검색 API·검색어 트렌드(NAVER API HUB) · 마지막 갱신 {fill["{{COLLECTED_KO}}"]}</p>\n'
            "</div>\n</body>\n</html>\n")
    (ROOT / "docs" / C.SLUG / "index.html").write_text(head + body + foot, encoding="utf-8")
    return {"slug": C.SLUG, "name": C.NAME, "updated": ko_date(D["generated"]), "tagline": getattr(C, "TAGLINE", ""),
            "top": [p["name"] for p in sorted(places, key=lambda p: -p["steady"])[:5]], "count": len(places), "picks": len(picks)}


def city_image(slug):
    """web/images/<slug>.(jpg|jpeg|png|webp|svg) 중 있는 것을 docs/images/ 로 복사하고 파일 이름을 돌려준다.
    직접 찍은 사진(jpg 등)을 넣으면 그림(svg)보다 먼저 쓴다."""
    out = ROOT / "docs/images"; out.mkdir(parents=True, exist_ok=True)
    for ext in ("jpg", "jpeg", "png", "webp", "svg"):
        src = ROOT / "web/images" / f"{slug}.{ext}"
        if src.exists():
            shutil.copyfile(src, out / src.name)
            return src.name
    return None


def city_card(c, prefix):
    img = c.get("image")
    pic = f'<img src="{prefix}images/{img}" alt="" loading="lazy">' if img else ""
    sub = html.escape(c.get("tagline") or "") or f'장소 {c["count"]}곳'
    return (f'    <a class="okr-city" href="{prefix}{c["slug"]}/">{pic}'
            f'<span class="cap"><b>{html.escape(c["name"])}</b><span>{sub}</span></span></a>')


def add_other_cities(cards):
    """도시 페이지 맨 아래에 다른 도시 카드를 넣는다. 다음 도시부터 순서대로 돌아서 마지막 도시는 첫 도시로 이어진다."""
    if len(cards) < 2:
        return
    for i, c in enumerate(cards):
        others = [cards[(i + k) % len(cards)] for k in range(1, len(cards))]
        block = ('  <section class="okr-sec" id="other-cities">\n    <h2>다른 도시 둘러보기</h2>\n    <div class="okr-cities">\n'
                 + "\n".join(city_card(o, "../") for o in others) + "\n    </div>\n  </section>\n")
        f = ROOT / "docs" / c["slug"] / "index.html"
        if f.exists():
            f.write_text(f.read_text(encoding="utf-8").replace("<!--OTHER_CITIES-->\n", block), encoding="utf-8")


def build_hub(cards):
    """docs/index.html: 도시 목록."""
    items = []
    for c in cards:
        top = "".join(f"<li>{html.escape(n)}</li>" for n in c["top"])
        pick = f' · <span class="silk">silk pick!</span> {c["picks"]}곳' if c["picks"] else ""
        img = f'<img src="images/{c["image"]}" alt="" loading="lazy">' if c.get("image") else ""
        items.append(f'''    <a class="city" href="{c["slug"]}/">
      <div class="pic">{img}<span class="cap"><b>{html.escape(c["name"])}</b><span>{html.escape(c.get("tagline") or "")}</span></span></div>
      <div class="body">
        <p class="meta">장소 {c["count"]}곳{pick} · {c["updated"]} 갱신</p>
        <ol>{top}</ol>
        <span class="go">스테디 명소 보기 →</span>
      </div>
    </a>''')
    page = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>steady-spot</title>
<meta name="description" content="여행지별로 꾸준히 많이 찾는 스테디 명소 순위">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500&family=Noto+Serif+KR:wght@400&display=swap">
<style>
:root {{ --fg: #1d2326; --muted: #5f6b70; --bg: #fbfcfc; --panel: #f1f4f4; --line: #dfe5e6; --accent: #1d7f8c; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --fg: #e8eced; --muted: #9aa6aa; --bg: #14181a; --panel: #1c2224; --line: #2e3639; --accent: #4fb7c4; color-scheme: dark; }} }}
:root[data-theme="dark"] {{ --fg: #e8eced; --muted: #9aa6aa; --bg: #14181a; --panel: #1c2224; --line: #2e3639; --accent: #4fb7c4; color-scheme: dark; }}
body {{ margin: 0; background: var(--bg); color: var(--fg); font-family: "Noto Sans KR", system-ui, -apple-system, sans-serif; line-height: 1.5; }}
main {{ max-width: 1000px; margin: 0 auto; padding-block: 48px 64px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }}
h1 {{ font-family: "Noto Serif KR", Georgia, serif; font-weight: 400; font-size: 32px; margin: 0 0 8px; }}
.lede {{ color: var(--muted); margin: 0 0 32px; max-width: 60ch; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }}
.city {{ display: flex; flex-direction: column; border: 1px solid var(--line); border-radius: 12px; background: var(--panel); color: inherit; text-decoration: none; overflow: hidden; }}
.city:hover, .city:focus-visible {{ border-color: var(--accent); outline: none; }}
.pic {{ position: relative; aspect-ratio: 16 / 9; overflow: hidden; background: var(--line); }}
.pic img {{ width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .4s ease; }}
.city:hover .pic img, .city:focus-visible .pic img {{ transform: scale(1.04); }}
@media (prefers-reduced-motion: reduce) {{ .pic img {{ transition: none; }} }}
.cap {{ position: absolute; inset: auto 0 0 0; padding: 14px 16px; color: #fff; background: linear-gradient(to top, rgba(10, 14, 30, .78), rgba(10, 14, 30, 0)); display: flex; flex-direction: column; gap: 2px; }}
.cap b {{ font-family: "Noto Serif KR", Georgia, serif; font-weight: 400; font-size: 28px; line-height: 1.1; }}
.cap span {{ font-size: 13px; opacity: .92; }}
.body {{ display: flex; flex-direction: column; gap: 6px; padding: 14px 16px 18px; flex: 1; }}
.meta {{ color: var(--muted); font-size: 13px; margin: 0; }}
.silk {{ font-size: 11px; font-weight: 500; padding: 0 6px; border-radius: 999px; background: var(--fg); color: var(--bg); }}
ol {{ margin: 6px 0 4px; padding-left: 1.3em; }}
.go {{ color: var(--accent); font-size: 14px; font-weight: 500; margin-top: auto; }}
footer {{ color: var(--muted); font-size: 12px; margin-top: 40px; }}
</style>
</head>
<body>
<main>
  <h1>steady-spot</h1>
  <p class="lede">여행지에서 꾸준히 많이 찾는 스테디 명소예요. 네이버 검색 3년 추세와 블로그·카페 글로 고르고, 매달 갱신해요.</p>
  <div class="grid">
{chr(10).join(items)}
  </div>
  <footer>데이터: 네이버 검색 API·검색어 트렌드(NAVER API HUB)</footer>
</main>
</body>
</html>
'''
    (ROOT / "docs/index.html").write_text(page, encoding="utf-8")
    (ROOT / "docs/.nojekyll").write_text("", encoding="utf-8")
    print("docs/index.html (도시 목록) 생성:", ", ".join(c["name"] for c in cards))


if __name__ == "__main__":
    only = sys.argv[sys.argv.index("--city") + 1] if "--city" in sys.argv else None
    cards = []
    for slug in CITIES:
        C = load(slug)
        ready = (ROOT / "data" / slug / "places.json").exists() and C.PLACES
        if ready and (only is None or only == slug):
            cards.append(build_city(C))
        elif ready and (ROOT / "docs" / slug / "data/stats.json").exists():
            # 이번에 다시 만들지 않은 도시는 기존 공개 데이터로 목록 카드만 만든다
            st = json.loads((ROOT / "docs" / slug / "data/stats.json").read_text(encoding="utf-8"))[0]
            pl = json.loads((ROOT / "docs" / slug / "data/places.json").read_text(encoding="utf-8"))
            pk = json.loads((ROOT / "docs" / slug / "data/picks.json").read_text(encoding="utf-8"))
            cards.append({"slug": slug, "name": C.NAME, "updated": ko_date(st["collectedOn"]), "count": len(pl), "picks": len(pk),
                          "top": [p["name"] for p in sorted(pl, key=lambda p: -p["steady"])[:5]]})
    for c in cards:
        c["image"] = city_image(c["slug"])
        c.setdefault("tagline", getattr(load(c["slug"]), "TAGLINE", ""))
    add_other_cities(cards)
    build_hub(cards)
