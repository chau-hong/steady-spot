"""3단계: 검색어 트렌드 36개월 (사용법: python3 trend.py --city okinawa) — 실제 검색 형태로 묶어 검색량·꾸준함·스테디 점수, 참고용 작년 대비 성장률 계산."""
import json, re, urllib.request, datetime as dt
from naver import load_env, city_dir
from cities import load

C = load()
cid, sec = load_env()
D = json.loads((city_dir(C) / "places.json").read_text(encoding="utf-8"))
ALS = {n: al for n, c, r, al in C.PLACES}
CHAIN, EXTRA = C.CHAIN, C.EXTRA
def kws(name):
    if name in CHAIN: return CHAIN[name]
    nm = re.sub(r"\(.*?\)", "", name).strip()
    named = [nm, nm.replace(" ", "")] if getattr(C, "QUERY_USE_NAME", False) else []
    base = EXTRA.get(name, []) + named + [a for a in ALS[name] if all(ord(ch) > 127 or ch.isdigit() for ch in a)]
    out = []
    for a in base:
        for k in ((a,) if a.startswith(C.PREFIX) else (a, C.PREFIX + " " + a)):
            if k not in out: out.append(k)
    return out[:20]
ANCHOR = {"groupName": "__anchor", "keywords": C.ANCHOR[1]}
_last = dt.date.today().replace(day=1) - dt.timedelta(days=1)  # 지난달 말일 = 마지막 완결 월
_y, _m = _last.year, _last.month
months = []
for k in range(35, -1, -1):
    mm = _m - k; yy = _y + (mm - 1) // 12; mm = (mm - 1) % 12 + 1
    months.append(f"{yy}-{mm:02d}-01")
END_DATE = _last.isoformat()
D["months"] = months
def call(groups):
    body = {"startDate": months[0], "endDate": END_DATE, "timeUnit": "month", "keywordGroups": groups + [ANCHOR]}
    req = urllib.request.Request("https://naverapihub.apigw.ntruss.com/search-trend/v1/search", data=json.dumps(body).encode(),
          headers={"X-NCP-APIGW-API-KEY-ID": cid, "X-NCP-APIGW-API-KEY": sec, "Content-Type": "application/json"}, method="POST")
    res = json.load(urllib.request.urlopen(req))["results"]
    a = {d["period"]: d["ratio"] for d in res[-1]["data"]}; asum = sum(a.values()) or 1
    return [[round({d["period"]: d["ratio"] for d in r["data"]}.get(x, 0) / asum * 36 * 100, 2) for x in months] for r in res[:-1]]
yoy = lambda s: (sum(s[-3:]) / sum(s[-15:-12]) - 1) * 100 if sum(s[-15:-12]) >= 3 else None
base = call([{"groupName": C.NAME, "keywords": C.BASE}])[0]
by = yoy(base)
D["cityTrend"] = base; D["cityYoy"] = round(by) if by is not None else 0
print(f"[{C.NAME}] 도시 전체 작년 대비 {D['cityYoy']}%")
P = D["places"]
for k in range(0, len(P), 4):
    ch = P[k:k+4]
    for p, s in zip(ch, call([{"groupName": p["name"], "keywords": kws(p["name"])} for p in ch])):
        p["trendKw"] = kws(p["name"]); p["trend"] = s
        p["searchIndex"] = round(sum(s[-12:]) / 12, 1)
        p["vol36"] = round(sum(s) / 36, 1)
        ys = [sum(s[0:12]) / 12, sum(s[12:24]) / 12, sum(s[24:36]) / 12]
        p["yearAvg"] = [round(v, 1) for v in ys]
        p["consistency"] = round(min(ys) / max(ys) * 100) if max(ys) > 0 else 0
        p["steady"] = round(p["vol36"] * p["consistency"] / 100, 1)
        y = yoy(s); p["yoy"] = None if y is None else round(y)
        p["relYoy"] = None if y is None else round(((1 + y / 100) / (1 + D["cityYoy"] / 100) - 1) * 100)
(city_dir(C) / "places.json").write_text(json.dumps(D, ensure_ascii=False, indent=1), encoding="utf-8")
for p in sorted(P, key=lambda p: -p["steady"]):
    print(f"[{C.NAME}] {p['name'][:16]:16s} steady {p['steady']:6.1f} vol36 {p['vol36']:6.1f} cons {p['consistency']:3d}% yrs {p['yearAvg']} rel {str(p['relYoy']):>5} 30일 {p['blog30']}")
