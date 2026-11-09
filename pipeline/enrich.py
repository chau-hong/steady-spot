"""2단계: 장소별 블로그·카페 결과 수, 최근 30일 블로그 글 수, 대표 글 수집.
사용법: python3 enrich.py --city okinawa [--only "장소1|장소2"]"""
import json, re, sys, datetime as dt
from naver import search, clean, city_dir, has_context
from cities import load

C = load()
today = dt.date.today()
ONLY = set(sys.argv[sys.argv.index("--only") + 1].split("|")) if "--only" in sys.argv else None


def item(it, kind):
    return {"title": clean(it["title"]), "desc": clean(it["description"])[:160], "link": it["link"],
            "date": it.get("postdate", ""), "src": clean(it.get("bloggername") or it.get("cafename") or ""), "kind": kind}


out = []
for name, cat, reg, al in C.PLACES:
    if ONLY and name not in ONLY:
        continue
    word = C.Q.get(name) or (re.sub(r"\(.*?\)", "", name).strip() if getattr(C, "QUERY_USE_NAME", False) else al[0])
    q = word if word.startswith(C.PREFIX) else C.PREFIX + " " + word
    als = [a.lower() for a in al]

    def match(it):
        t = (clean(it["title"]) + clean(it["description"])).replace(" ", "").lower()
        return any(a in t for a in als) and has_context(t, C)

    first = None; matched = []; scanned = 0; oldest = today; est = False
    for start in range(1, 1001, 100):
        r = search("blog", q, display=100, start=start, sort="date")
        first = first or r
        its = [i for i in r["items"] if i.get("postdate")]
        scanned += len(its)
        matched += [i for i in its if match(i)]
        if its:
            oldest = dt.datetime.strptime(its[-1]["postdate"], "%Y%m%d").date()
        if (today - oldest).days > 30 or len(r["items"]) < 100:
            break
    last30 = sum(1 for i in matched if (today - dt.datetime.strptime(i["postdate"], "%Y%m%d").date()).days <= 30)
    if (today - oldest).days <= 30:  # 1000건을 다 봐도 30일이 안 채워짐 → 하루 평균으로 환산
        est = True; last30 = round(last30 * 30 / max(1, (today - oldest).days))
    bs = [i for i in search("blog", q, display=10, sort="sim")["items"] if match(i)]
    cs_res = search("cafearticle", q, display=10, sort="sim")
    cs = [i for i in cs_res["items"] if match(i)][:3]
    seen = set(); posts = []
    for it in bs[:3] + matched[:2]:
        if it["link"] in seen:
            continue
        seen.add(it["link"]); posts.append(item(it, "blog"))
    out.append({"name": name, "cat": cat, "region": reg, "query": q, "blogTotal": first["total"], "cafeTotal": cs_res["total"],
                "blog30": last30, "blog30est": est, "matchRate": round(len(matched) / max(1, scanned), 2),
                "posts": posts, "cafe": [item(i, "cafe") for i in cs]})
    print(f"[{C.NAME}] {name}: blog {first['total']:,} / cafe {cs_res['total']:,} / 30일 {last30}", flush=True)

path = city_dir(C) / "places.json"
if ONLY and path.exists():  # 일부만 다시 모았으면 기존 결과에 합치기
    old = json.loads(path.read_text(encoding="utf-8"))
    order = [n for n, *_ in C.PLACES]
    out = sorted([p for p in old["places"] if p["name"] not in ONLY and p["name"] in order] + out,
                 key=lambda p: order.index(p["name"]))
path.write_text(json.dumps({"months": [], "generated": str(today), "places": out}, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"[{C.NAME}] 장소 {len(out)}곳 저장")
