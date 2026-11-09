"""3단계: 검색어 트렌드 36개월 — 실제 검색 형태로 묶어 검색량·꾸준함·스테디 점수, 참고용 작년 대비 성장률 계산."""
import json, urllib.request, datetime as dt
from naver import load_env, ROOT
from places import PLACES
cid, sec = load_env()
D = json.loads((ROOT / "data/places.json").read_text(encoding="utf-8"))
ALS = {n: al for n, c, r, al in PLACES}
CHAIN = {"이케이섬": ["이케이섬", "이케이지마", "이케이 섬", "이케이 비치", "이케이비치", "오키나와 이케이섬"],
         "이아스몰": ["이아스몰", "이아스 오키나와", "이아스 쇼핑몰", "오키나와 이아스"],
         "나미노우에궁": ["나미노우에궁", "나미노우에 궁", "나미노우에 신사", "나미노우에신사", "나미노우에 비치", "나미노우에비치", "오키나와 나미노우에", "나미노우에"],
         "비세 후쿠기 가로수길": ["비세 후쿠기 가로수길", "비세후쿠기 가로수길", "후쿠기 가로수길", "비세 후쿠기", "비세마을", "비세 마을", "후쿠기 가로수", "오키나와 후쿠기"],
         "나시로 비치": ["나시로 비치", "나시로비치", "나시로 해변", "오키나와 나시로비치", "오키나와 나시로 비치"],
         "해중도로": ["해중도로", "해중 도로", "오키나와 해중도로", "카이츄도로"],
         "제1마키시 공설시장": ["마키시 공설시장", "마키시공설시장", "제1마키시 공설시장", "제1 마키시 공설시장", "마키시 시장", "마키시시장", "오키나와 공설시장", "나하 공설시장"],
         "츠보야 야치문 거리": ["츠보야", "츠보야 야치문 거리", "츠보야 도자기 거리", "츠보야 거리", "쓰보야"],
"돈키호테(오키나와)": ["오키나와 돈키호테", "돈키호테 국제거리", "국제거리 돈키호테", "나하 돈키호테"],
         "A&W 버거": ["오키나와 A&W", "A&W 버거", "A&W 오키나와", "에이앤더블유", "오키나와 에이앤더블유"],
         "구루메 회전초밥": ["구루메 회전초밥", "구루메스시", "구루메 스시", "오키나와 구루메스시", "오키나와 회전초밥"],
"모토무라 규카츠": ["오키나와 모토무라", "모토무라 국제거리", "오키나와 규카츠"],
         "이치란 라멘(국제거리)": ["오키나와 이치란", "이치란 국제거리", "국제거리 이치란"],
         "단보라멘": ["오키나와 단보라멘", "단보라멘 국제거리", "단보라멘 오키나와", "단보라멘"]}
EXTRA = {"동남식물원": ["동남식물원", "동남 식물원", "동남식물낙원", "동남 식물낙원", "오키나와 동남식물원", "오키나와 동남식물낙원"],
"21세기 숲 공원": ["21세기 숲 공원", "21세기의 숲 공원", "21세기 숲", "나고 21세기 숲"],
"치넨미사키 공원": ["치넨미사키 공원", "치넨 미사키"], "코우리 오션타워": ["코우리 오션타워", "오션타워"], "쿄다 휴게소": ["쿄다 휴게소", "쿄다휴게소"],
         "DMM 카리유시 수족관": ["카리유시 수족관", "DMM 카리유시 수족관", "DMM 수족관"], "부세나 해중공원": ["부세나 해중공원", "부세나 해중전망탑", "부세나 마린파크", "부세나 글라스보트"],
         "츠보야 야치문 거리": ["츠보야 야치문 거리", "츠보야 도자기 거리"], "강가라 계곡": ["강가라 계곡"], "케라마 제도": ["케라마 제도", "자마미섬", "토카시키섬", "자마미 섬"],
         "안치 비치": ["안치 비치"], "자네 비치": ["자네 비치"], "오도 비치": ["오도 비치"], "오쿠마 비치": ["오쿠마 비치"], "이토만 어시장(이유마치)": ["이토만 어시장", "이토만 수산시장", "이유마치 수산시장"],
         "얏빠리 스테이크": ["얏빠리 스테이크", "얏빠리스테이크"], "야치문 킷사 시사엔": ["야치문 킷사 시사엔", "시사엔 카페"], "슈리 킨조초 돌다다미길": ["킨조초 돌다다미길", "슈리 킨조초"],
         "평화기념공원": ["평화기념공원", "오키나와 평화기념공원", "평화기념 공원"], "이아스몰": ["이아스 오키나와", "이아스몰"],
"비세 후쿠기 가로수길": ["비세 후쿠기 가로수길", "후쿠기 가로수길", "비세 후쿠기"], "츄라우미 수족관": ["츄라우미 수족관", "추라우미 수족관"],
         "코우리섬·코우리대교": ["코우리 대교", "고우리 대교"], "해중도로": ["해중 도로"], "푸른동굴(마에다곶)": ["마에다 곶", "푸른 동굴"],
         "아시비나 아울렛": ["아시비나 아울렛", "오키나와 아울렛"], "나시로 비치": ["나시로 비치"], "이온몰 라이카무": ["이온몰 라이카무", "라이카무 이온몰"],
         "카페 쿠루쿠마": ["카페 쿠루쿠마"], "하마베노차야": ["하마베노 차야"], "니라이카나이 다리": ["니라이카나이 다리", "니라이카나이 브릿지"]}
def kws(name):
    if name in CHAIN: return CHAIN[name]
    base = EXTRA.get(name, []) + [a for a in ALS[name] if all(ord(ch) > 127 or ch.isdigit() for ch in a)]
    out = []
    for a in base:
        for k in (a, "오키나와 " + a):
            if k not in out: out.append(k)
    return out[:20]
ANCHOR = {"groupName": "__anchor", "keywords": ["만좌모", "만자모", "오키나와 만좌모", "오키나와 만자모"]}
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
base = call([{"groupName": "오키나와", "keywords": ["오키나와", "오키나와 여행", "오키나와여행", "오키나와 자유여행", "오키나와 날씨", "오키나와 항공권"]}])[0]
D["okinawaTrend"] = base; D["okinawaYoy"] = round(yoy(base))
print("오키나와 전체 YoY", D["okinawaYoy"], "%")
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
        p["relYoy"] = None if y is None else round(((1 + y / 100) / (1 + D["okinawaYoy"] / 100) - 1) * 100)
(ROOT / "data/places.json").write_text(json.dumps(D, ensure_ascii=False, indent=1), encoding="utf-8")
for p in sorted(P, key=lambda p: -p["steady"]):
    print(f"{p['name'][:16]:16s} steady {p['steady']:6.1f} vol36 {p['vol36']:6.1f} cons {p['consistency']:3d}% yrs {p['yearAvg']} rel {str(p['relYoy']):>5} 30일 {p['blog30']}")
