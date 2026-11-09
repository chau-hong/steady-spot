"""1-2단계: 지역·분류별 검색어로 추가 수집해 data/raw.json 에 합침."""
import json
from naver import search, ROOT, clean
QUERIES = ["오키나와 북부 가볼만한곳","오키나와 중부 가볼만한곳","오키나와 남부 가볼만한곳","나하 가볼만한곳","오키나와 관광지",
           "오키나와 관광지 추천","오키나와 해변","오키나와 스노클링","오키나와 아이랑","오키나와 쇼핑","나하 맛집","오키나와 맛집 추천",
           "오키나와 카페 추천","오키나와 드라이브","오키나와 명소","오키나와 필수코스"]
items = {i["link"]: i for i in json.loads((ROOT/"data/raw.json").read_text(encoding="utf-8"))}
before = len(items)
for q in QUERIES:
    for kind in ("blog","cafearticle"):
        for sort in (("date","sim") if kind=="blog" else ("sim",)):
            for start in range(1,1001,100):
                try: res = search(kind,q,start=start,sort=sort)
                except Exception as e: print("skip",q,e); break
                for it in res.get("items",[]):
                    t = clean(it["title"])+clean(it["description"])
                    if "오키나와" not in t and "나하" not in t: continue
                    it["_kind"], it["_query"] = kind, q
                    items.setdefault(it["link"], it)
                if start+100 > res.get("total",0): break
    print(f"{q}: 누적 {len(items)}")
(ROOT/"data/raw.json").write_text(json.dumps(list(items.values()),ensure_ascii=False),encoding="utf-8")
print("추가", len(items)-before, "총", len(items))
