"""2단계: 장소별 언급 수·최근 활발도·검색 추세·대표 글 수집."""
import json, sys, datetime as dt, urllib.request
from collections import Counter
from naver import search, clean, load_env, ROOT
from places import PLACES

Q = {"동남식물원":"동남식물원","부세나 해중공원":"부세나 해중공원","치넨미사키 공원":"치넨미사키 공원","코우리 오션타워":"코우리 오션타워","쿄다 휴게소":"쿄다 휴게소","DMM 카리유시 수족관":"카리유시 수족관","츠보야 야치문 거리":"츠보야 야치문","케라마 제도":"케라마","오쿠마 비치":"오쿠마 비치","야가지섬":"야가지섬","이토만 어시장(이유마치)":"이토만 어시장","얏빠리 스테이크":"얏빠리 스테이크","구루메 회전초밥":"구루메 회전초밥","삿짱소바":"삿짱소바","야치문 킷사 시사엔":"시사엔","돈키호테(오키나와)":"돈키호테","A&W 버거":"A&W","하마히가섬":"하마히가섬","강가라 계곡":"강가라 계곡","이케이섬":"이케이섬","코우리섬·코우리대교":"코우리섬","비세 후쿠기 가로수길":"비세 후쿠기","지바고 커피":"지바고 커피","미바루 비치":"미바루비치",
     "나시로 비치":"나시로비치","세소코섬":"세소코섬","카츠렌 성터":"카츠렌 성터","키시모토 식당":"키시모토 식당",
     "모토무라 규카츠":"모토무라 규카츠","이치란 라멘(국제거리)":"이치란","제1마키시 공설시장":"마키시 공설시장",
     "오키나와 월드(교쿠센도)":"오키나와월드","푸른동굴(마에다곶)":"푸른동굴","오리온 해피파크(맥주공장)":"오리온 해피파크",
     "오우지마(오우섬)":"오우지마","선셋 비치(차탄)":"선셋비치","하테루마(전통공연 이자카야)":"하테루마 국제거리",
     "세나가지마 우미카지테라스":"우미카지테라스","츄라우미 수족관":"츄라우미 수족관","반타 카페":"반타카페"}
TK = {"이치란 라멘(국제거리)":["오키나와 이치란"],"하테루마(전통공연 이자카야)":["하테루마 국제거리"],"반타 카페":["반타카페","카후반타"],
      "지바고 커피":["지바고커피","지바고 커피"],"미바루 비치":["미바루비치","미바루 비치"],"나시로 비치":["나시로비치","나시로 비치"],
      "제1마키시 공설시장":["마키시 공설시장","마키시공설시장"],"키시모토 식당":["키시모토식당","키시모토 식당"],
      "모토무라 규카츠":["모토무라 규카츠","모토무라"],"세소코섬":["세소코섬","세소코"],"오리온 해피파크(맥주공장)":["오리온 해피파크","오리온 맥주공장"],
      "단보라멘":["단보라멘"],"블루씰 아이스크림":["블루씰"],"선셋 비치(차탄)":["오키나와 선셋비치"],"에메랄드 비치":["오키나와 에메랄드비치"],
      "만자 비치":["만자비치"],"아라하 비치":["아라하비치"]}
today = dt.date.today()

def item(it, kind):
    return {"title": clean(it["title"]), "desc": clean(it["description"])[:160], "link": it["link"],
            "date": it.get("postdate", ""), "src": clean(it.get("bloggername") or it.get("cafename") or ""), "kind": kind}

ONLY = set(sys.argv[sys.argv.index("--only") + 1].split("|")) if "--only" in sys.argv else None
out = []
for name, cat, reg, al in PLACES:
    if ONLY and name not in ONLY: continue
    q = "오키나와 " + Q.get(name, al[0])
    als = [a.lower() for a in al]
    def match(it):
        t = (clean(it["title"]) + clean(it["description"])).replace(" ", "").lower()
        return any(a in t for a in als) and ("오키나와" in t or "나하" in t)
    bd = None; matched = []; scanned = 0; oldest = today; est = False
    for start in range(1, 1001, 100):
        r = search("blog", q, display=100, start=start, sort="date")
        bd = bd or r
        its = [i for i in r["items"] if i.get("postdate")]
        scanned += len(its)
        matched += [i for i in its if match(i)]
        if its: oldest = dt.datetime.strptime(its[-1]["postdate"], "%Y%m%d").date()
        if (today - oldest).days > 30 or len(r["items"]) < 100: break
    in30 = [i for i in matched if (today - dt.datetime.strptime(i["postdate"], "%Y%m%d").date()).days <= 30]
    last30 = len(in30)
    if (today - oldest).days <= 30:  # 1000건을 다 봐도 30일이 안 채워짐 → 일평균으로 환산
        est = True; last30 = round(last30 * 30 / max(1, (today - oldest).days))
    bs = search("blog", q, display=10, sort="sim")
    cs = search("cafearticle", q, display=10, sort="sim")
    bd = {"total": bd["total"], "items": [i for i in matched][:5]}
    bs["items"] = [i for i in bs["items"] if match(i)]
    cs["items"] = [i for i in cs["items"] if match(i)][:3]
    seen=set(); posts=[]
    for it in bs["items"][:3] + [i for i in bd["items"][:2]]:
        if it["link"] in seen: continue
        seen.add(it["link"]); posts.append(item(it, "blog"))
    out.append({"name": name, "cat": cat, "region": reg, "query": q, "blogTotal": bd["total"], "cafeTotal": cs["total"],
                "blog30": last30, "blog30est": est, "matchRate": round(len(matched)/max(1,scanned),2), "posts": posts, "cafe": [item(i, "cafe") for i in cs["items"]],
                "trendKw": TK.get(name, al[:2])})
    print(f"{name}: blog {bd['total']:,} / cafe {cs['total']:,} / 30일 {last30}")

months = []

if ONLY:  # 기존 결과에 합치기
    old = json.loads((ROOT / "data/places.json").read_text(encoding="utf-8"))
    keep = [p for p in old["places"] if p["name"] not in ONLY]
    order = [n for n, *_ in PLACES]
    out = sorted(keep + out, key=lambda p: order.index(p["name"]) if p["name"] in order else 999)
(ROOT / "data/places.json").write_text(json.dumps({"months": months, "generated": str(today), "places": out}, ensure_ascii=False, indent=1), encoding="utf-8")
print("done")
