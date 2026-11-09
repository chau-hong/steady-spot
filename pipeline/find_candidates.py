"""보조: 수집 글에서 자주 나오지만 장소 목록(places.py)에 없는 이름 후보를 reports/new_candidates.md 로 뽑는다.
사람이 확인한 뒤 places.py 에 추가하는 용도예요."""
import json, re, datetime as dt
from collections import Counter
from naver import clean, ROOT
from places import PLACES

raw = json.loads((ROOT / "data/raw.json").read_text(encoding="utf-8"))
known = [a.lower() for n, c, r, al in PLACES for a in al]
PART = r"(에서|으로|에는|에도|에|의|은|는|이|가|를|을|와|과|도|까지|부터|이랑|랑|로|만|처럼|보다)$"
SUF = ("공원", "비치", "해변", "섬", "지마", "곶", "미사키", "성터", "시장", "식당", "카페", "커피", "거리", "몰", "타워", "동굴", "폭포",
       "대교", "마을", "신사", "궁", "수족관", "전망대", "아울렛", "스테이크", "소바", "라멘", "파크", "랜드", "가든", "농원", "우타키", "숲",
       "정원", "박물관", "미술관", "휴게소", "온천", "타운", "언덕", "계곡", "마켓", "놀이터")
SUF_GENERIC = set(SUF)
STOP = set("오키나와 나하 일본 여행 추천 가볼만한곳 맛집 카페 후기 일정 코스 아이랑 가족 북부 남부 중부 렌트카 호텔 숙소 리조트 해외 근처 현지 "
           "공원 비치 해변 섬 시장 식당 커피 거리 마을 파크 공항 나하공항 본섬 이온몰 쇼핑몰 오션뷰 감성 아름다운 예쁜".split())
IGN = {l.strip() for l in (ROOT / "pipeline/ignore_candidates.txt").read_text(encoding="utf-8").splitlines()
       if l.strip() and not l.startswith("#")} if (ROOT / "pipeline/ignore_candidates.txt").exists() else set()
cnt = Counter()
for i in raw:
    ws = [w if w.endswith("오키나와") else re.sub(PART, "", w) for w in re.findall(r"[가-힣A-Za-z0-9&]+", clean(i["title"]) + " " + clean(i["description"]))]
    seen = set()
    for k, w in enumerate(ws):
        if len(w) >= 2 and w.endswith(SUF): seen.add(w)
        if k + 1 < len(ws) and len(w) >= 2 and ws[k + 1].endswith(SUF): seen.add(w + " " + ws[k + 1])
    cnt.update(seen)
generic = lambda w: w.replace(" ", "") in SUF or w.startswith(("오키나와", "오키나 ", "나하")) or w in ("먹거리", "볼거리", "놀거리")
isknown = lambda w: any(a in w.replace(" ", "").lower() for a in known)
rows = [(w, n) for w, n in cnt.most_common() if n >= 15 and w.split(" ")[0] not in STOP and w not in STOP and not isknown(w) and not generic(w) and w not in IGN and w.replace(" ", "") not in IGN]
(ROOT / "reports").mkdir(exist_ok=True)
lines = [f"# 새 장소 후보 ({dt.date.today()})", "", "수집 글에서 15번 이상 나왔지만 places.py 에 없는 이름이에요. 장소가 맞으면 places.py 에 추가하세요.", "",
         "| 이름 | 언급 글 수 |", "|---|---|"] + [f"| {w} | {n} |" for w, n in rows[:80]]
(ROOT / "reports/new_candidates.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"reports/new_candidates.md  후보 {len(rows)}개")
