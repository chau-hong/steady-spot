"""1단계: 도시 여행 관련 최신 블로그·카페 글을 넓게 수집해 data/<city>/raw.json 에 저장.
사용법: python3 collect.py --city okinawa"""
import json
from naver import search, clean, city_dir, has_context
from cities import load

C = load()
items = {}
for q in C.QUERIES + C.QUERIES_EXTRA:
    for kind in ("blog", "cafearticle"):
        for sort in (("date", "sim") if kind == "blog" else ("sim",)):
            for start in range(1, 1001, 100):
                try:
                    res = search(kind, q, start=start, sort=sort)
                except Exception as e:
                    print("skip", q, kind, sort, start, e); break
                for it in res.get("items", []):
                    if not has_context(clean(it["title"]) + clean(it["description"]), C):
                        continue
                    it["_kind"], it["_query"] = kind, q
                    items.setdefault(it["link"], it)
                if start + 100 > res.get("total", 0):
                    break
    print(f"[{C.NAME}] {q}: 누적 {len(items)}건", flush=True)
(city_dir(C) / "raw.json").write_text(json.dumps(list(items.values()), ensure_ascii=False), encoding="utf-8")
print(f"[{C.NAME}] 저장 완료: {len(items)}건")
