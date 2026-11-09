"""보조: 수집 글에서 자주 나오지만 장소 목록에 없는 이름 후보를 reports/<city>_new_candidates.md 로 뽑는다.
사람이 확인한 뒤 cities/<city>.py 의 PLACES 에 추가하는 용도예요. 사용법: python3 find_candidates.py --city okinawa"""
import json, re, datetime as dt
from collections import Counter
from naver import clean, ROOT, city_dir
from cities import load

C = load()

raw = json.loads((city_dir(C) / "raw.json").read_text(encoding="utf-8"))
known = [a.lower() for n, c, r, al in C.PLACES for a in al]
PART = r"(에서|으로|에는|에도|에|의|은|는|이|가|를|을|와|과|도|까지|부터|이랑|랑|로|만|처럼|보다)$"
SUF = ("공원", "비치", "해변", "섬", "지마", "곶", "미사키", "성터", "시장", "식당", "카페", "커피", "거리", "몰", "타워", "동굴", "폭포",
       "대교", "마을", "신사", "궁", "수족관", "전망대", "아울렛", "스테이크", "소바", "라멘", "파크", "랜드", "가든", "농원", "우타키", "숲",
       "정원", "박물관", "미술관", "휴게소", "온천", "타운", "언덕", "계곡", "마켓", "놀이터")
SUF_GENERIC = set(SUF)
STOP = set(C.STOP_WORDS) | set("일본 여행 추천 가볼만한곳 맛집 카페 후기 일정 코스 아이랑 가족 북부 남부 중부 렌트카 호텔 숙소 리조트 해외 근처 현지 "
           "공원 비치 해변 섬 시장 식당 커피 거리 마을 파크 공항 이온몰 쇼핑몰 오션뷰 감성 아름다운 예쁜".split())
IGN = {l.strip() for l in (ROOT / "pipeline/ignore_candidates.txt").read_text(encoding="utf-8").splitlines()
       if l.strip() and not l.startswith("#")} if (ROOT / "pipeline/ignore_candidates.txt").exists() else set()
IGN |= set(C.IGNORE)
cnt = Counter()
for i in raw:
    ws = [w if w.endswith(tuple(C.CONTEXT)) else re.sub(PART, "", w) for w in re.findall(r"[가-힣A-Za-z0-9&]+", clean(i["title"]) + " " + clean(i["description"]))]
    seen = set()
    for k, w in enumerate(ws):
        if len(w) >= 2 and w.endswith(SUF): seen.add(w)
        if k + 1 < len(ws) and len(w) >= 2 and ws[k + 1].endswith(SUF): seen.add(w + " " + ws[k + 1])
    cnt.update(seen)
generic = lambda w: w.replace(" ", "") in SUF or w.startswith(tuple(C.CONTEXT)) or w in ("먹거리", "볼거리", "놀거리")
isknown = lambda w: any(a in w.replace(" ", "").lower() for a in known)
rows = [(w, n) for w, n in cnt.most_common() if n >= 15 and w.split(" ")[0] not in STOP and w not in STOP and not isknown(w) and not generic(w) and w not in IGN and w.replace(" ", "") not in IGN]
# 브랜드형 이름: "블루보틀"처럼 끝말이 없는 가게 이름은 위 방식에 안 걸려서, 맛집·카페 글 제목에 자주 나온 낱말을 따로 센다
WORDS = set("""여행 추천 맛집 카페 후기 일정 코스 가족 아이랑 혼자 커플 현지인 현지 디저트 커피 라멘 스시 초밥 브런치 분위기 메뉴 가격 웨이팅
예약 위치 영업시간 솔직 솔직후기 내돈내산 리뷰 방문 정보 정리 총정리 베스트 best top 일본여행 감성 맛있는 유명한 인기 가성비 필수 진짜 정말 너무
이번 그리고 하는 있는 함께 다녀온 다녀왔어요 근처 점심 저녁 아침 야식 이자카야 우동 야키토리 함바그 함박스테이크 규카츠 돈카츠 돈까스 텐동 소바
장어덮밥 오마카세 회전초밥 빵집 베이커리 파르페 팬케이크 말차 푸딩 크로와상 젤라또 케이크 타르트 도넛 맥주 하이볼 사케 와규 야키니쿠 야끼니꾸
모츠나베 명란 돈코츠 교자 철판 꼬치 해산물 시장 쇼핑 기념품 면세 드럭스토어 편의점 호텔 숙소 리스트 추천해주세요 부탁드려요 부탁드립니다 추천부탁드려요
추천부탁드립니다 공항 방법 비교 자유여행 조식 로컬 식당 라멘집 주문 츠케멘 오픈런 무한리필 인생 가족여행 꿀팁 혼밥 가볼만한곳 전문 카이센동 당일치기
정식 직접 주문방법 어디 맛있 패키지 시간 투어 음식 가이드 원조 추천템 있을까요 킷사텐 오므라이스 할인 찐맛집 아이 가능 가능한 여기 평균 가정식 먹거리
스테이크 여행기 거리 산책 모닝세트 주말 coffee cafe 스페셜티 라떼 프렌치토스트 카레 노포 미슐랭 로스터리 몬자야끼 몬자야키 스키야키 아부라소바
놀거리 핫플 모음 완벽 교통 날씨 명소 feat 2박 3박 4박 3일 4일 5일 vs 3곳 5곳 3대 레스토 대욕장 온천 버스투어 부모님 아기 기온""".split())
title_cnt = Counter()
for i in raw:
    if not any(k in i.get("_query", "") for k in ("맛집", "카페", "라멘")):
        continue
    ws = {re.sub(PART + "|(점|본점)$", "", w) for w in re.findall(r"[가-힣A-Za-z0-9&]+", clean(i["title"]))}
    title_cnt.update(w for w in ws if len(w) >= 2 and not w.isdigit() and not re.search(r"\d", w))
brand = [(w, n) for w, n in title_cnt.most_common() if n >= 20 and w.lower() not in WORDS and w not in STOP and w not in IGN
         and not isknown(w) and not w.startswith(tuple(C.CONTEXT)) and not any(c.startswith(w) for c in C.CONTEXT) and not w.endswith(("맛집", "카페", "여행", "추천"))]
(ROOT / "reports").mkdir(exist_ok=True)
lines = [f"# {C.NAME} 새 장소 후보 ({dt.date.today()})", "", f"수집 글에서 15번 이상 나왔지만 장소 목록에 없는 이름이에요. 장소가 맞으면 pipeline/cities/{C.SLUG}.py 의 PLACES 에 추가하세요.", "",
         "| 이름 | 언급 글 수 |", "|---|---|"] + [f"| {w} | {n} |" for w, n in rows[:80]] + [
    "", "## 브랜드형 이름 후보", "", "맛집·카페 글 제목에 20번 이상 나온 낱말이에요. 가게 이름이 섞여 있으니 확인해 보세요.", "",
    "| 낱말 | 제목 수 |", "|---|---|"] + [f"| {w} | {n} |" for w, n in brand[:60]]
(ROOT / "reports" / f"{C.SLUG}_new_candidates.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"[{C.NAME}] reports/{C.SLUG}_new_candidates.md  후보 {len(rows)}개 · 브랜드형 {len(brand)}개")
