"""4단계: 수집 결과(data/)로 공개용 데이터 파일과 페이지를 만든다.

- docs/data/*.json     : 페이지가 읽는 데이터 (GitHub Pages 공개)
- docs/index.html      : GitHub Pages 에서 혼자 돌아가는 페이지
- dist/artifact_index.html : Claude 대시보드에 올리는 페이지 본문
"""
import json, datetime as dt
from naver import clean, ROOT
from places import PLACES, MAPQ

D = json.loads((ROOT / "data/places.json").read_text(encoding="utf-8"))
raw = json.loads((ROOT / "data/raw.json").read_text(encoding="utf-8"))
picks = json.loads((ROOT / "web/picks.json").read_text(encoding="utf-8"))
months = D["months"]
assert len(months) == 36, "trend.py 를 먼저 실행해 36개월 추세를 만들어 주세요"

al = {n: a for n, c, r, a in PLACES}
T = [(clean(i["title"]) + clean(i["description"])).replace(" ", "").lower() for i in raw]
P = [p for p in D["places"] if p["name"] in al and "trend" in p]

places = []
for p in P:
    a = [x.lower() for x in al[p["name"]]]
    places.append({
        "name": p["name"], "cat": p["cat"], "region": p["region"],
        "steady": p["steady"], "vol36": p["vol36"], "consistency": p["consistency"],
        "yr1": p["yearAvg"][0], "yr2": p["yearAvg"][1], "yr3": p["yearAvg"][2],
        "searchIndex": p["searchIndex"], "relYoy": p["relYoy"],
        "blog30": p["blog30"], "blog30est": p["blog30est"],
        "mentions": sum(1 for t in T if any(x in t for x in a)),
        "blogTotal": p["blogTotal"], "cafeTotal": p["cafeTotal"],
        "mapQuery": MAPQ.get(p["name"]), "trendKeywords": ", ".join(p["trendKw"]),
    })
trend = [{"name": p["name"], "month": m[:7], "index": v} for p in P for m, v in zip(months, p["trend"])]
trend += [{"name": "오키나와 전체", "month": m[:7], "index": v} for m, v in zip(months, D["okinawaTrend"])]
posts = []
for p in P:
    for kind, lst in (("블로그", p["posts"]), ("카페", p["cafe"])):
        for x in lst:
            posts.append({"name": p["name"], "type": kind, "title": x["title"], "summary": x["desc"],
                          "link": x["link"], "date": x["date"], "author": x["src"]})
names = {p["name"] for p in places}
missing = [k["name"] for k in picks if k["name"] not in names]
if missing:
    print("경고: picks.json 에 장소 목록에 없는 이름이 있어요 →", missing)
stats = [{"collected": len(raw), "blog": sum(i["_kind"] == "blog" for i in raw), "cafe": sum(i["_kind"] == "cafearticle" for i in raw),
          "places": len(places), "okinawaYoy": D["okinawaYoy"], "collectedOn": D["generated"],
          "trendFrom": months[0][:7], "trendTo": months[-1][:7]}]

out = ROOT / "docs/data"; out.mkdir(parents=True, exist_ok=True)
for n, o in (("places", places), ("trend", trend), ("posts", posts), ("stats", stats), ("picks", picks)):
    (out / f"{n}.json").write_text(json.dumps(o, ensure_ascii=False), encoding="utf-8")
    print(f"docs/data/{n}.json  {len(o)}행")

# 기간 문구 채우기
ym = lambda s: (int(s[:4]), int(s[5:7]))
ko = lambda s: f"{ym(s)[0]}년 {ym(s)[1]}월"
short = lambda a, b: f"{a[2:4]}.{a[5:7]}~{b[2:4]}.{b[5:7]}"
r0, r1 = months[-3], months[-1]
recent = f"{ym(r0)[0]}년 {ym(r0)[1]}~{ym(r1)[1]}월" if ym(r0)[0] == ym(r1)[0] else f"{ko(r0)}~{ko(r1)}"
g = dt.date.fromisoformat(D["generated"])
fill = {"{{COLLECTED_KO}}": f"{g.year}년 {g.month}월 {g.day}일", "{{FROM_KO}}": ko(months[0]), "{{TO_KO}}": ko(months[-1]),
        "{{Y1}}": short(months[0], months[11]), "{{Y2}}": short(months[12], months[23]), "{{Y3}}": short(months[24], months[35]),
        "{{RECENT3_KO}}": recent}
page = (ROOT / "web/page.template.html").read_text(encoding="utf-8")
for k, v in fill.items():
    page = page.replace(k, v)

(ROOT / "dist").mkdir(exist_ok=True)
(ROOT / "dist/artifact_index.html").write_text(page, encoding="utf-8")
body = page.replace('<meta name="dash-one-writer">\n', "")
head = (ROOT / "web/standalone_head.html").read_text(encoding="utf-8")
foot = (f'<p class="okr-foot">데이터: 네이버 검색 API·검색어 트렌드(NAVER API HUB) · 마지막 갱신 {fill["{{COLLECTED_KO}}"]}</p>\n'
        "</div>\n</body>\n</html>\n")
(ROOT / "docs/index.html").write_text(head + body + foot, encoding="utf-8")
(ROOT / "docs/.nojekyll").write_text("", encoding="utf-8")
print("docs/index.html, dist/artifact_index.html 생성 완료")
