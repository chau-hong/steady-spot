"""1단계: '오키나와' 여행 관련 최신 블로그/카페 글을 넓게 수집."""
import json
from naver import search, ROOT, clean

QUERIES = ["오키나와 여행", "오키나와 가볼만한곳", "오키나와 여행 코스", "오키나와 일정",
           "오키나와 맛집", "오키나와 카페", "오키나와 북부", "오키나와 남부"]
items = {}
for q in QUERIES:
    for kind in ("blog", "cafearticle"):
        for sort in (("date", "sim") if kind == "blog" else ("sim",)):
            for start in range(1, 1001, 100):
                try:
                    res = search(kind, q, start=start, sort=sort)
                except Exception as e:
                    print("skip", q, kind, sort, start, e); break
                for it in res.get("items", []):
                    if "오키나와" not in clean(it["title"]) + clean(it["description"]):
                        continue
                    it["_kind"], it["_query"] = kind, q
                    items.setdefault(it["link"], it)
                if start + 100 > res.get("total", 0):
                    break
    print(f"{q}: 누적 {len(items)}건")
(ROOT / "data/raw.json").write_text(json.dumps(list(items.values()), ensure_ascii=False), encoding="utf-8")
print("저장 완료:", len(items))
