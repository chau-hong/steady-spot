"""NAVER API HUB(ncloud) 검색 API(블로그/카페) 공통 함수."""
import json, os, re, time, urllib.parse, urllib.request, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # 프로젝트 루트
(ROOT / "data").mkdir(exist_ok=True)  # 수집 캐시(깃에 올리지 않음)

def load_env():
    env_file = ROOT / ".env"  # 로컬 실행용. GitHub Actions 에서는 Secrets 가 환경변수로 들어옴
    for line in (env_file.read_text(encoding="utf-8").splitlines() if env_file.exists() else []):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
    cid, sec = os.environ.get("NAVER_CLIENT_ID"), os.environ.get("NAVER_CLIENT_SECRET")
    if not cid or not sec:
        raise SystemExit("NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 가 없어요. 로컬은 .env 에, GitHub 은 저장소 Secrets 에 넣어 주세요.")
    return cid, sec

CID, SEC = None, None

def search(kind, query, display=100, start=1, sort="date"):
    """kind: blog | cafearticle"""
    global CID, SEC
    if CID is None:
        CID, SEC = load_env()
    url = f"https://naverapihub.apigw.ntruss.com/search/v1/{kind}?" + urllib.parse.urlencode(
        {"query": query, "display": display, "start": start, "sort": sort})
    req = urllib.request.Request(url, headers={"X-NCP-APIGW-API-KEY-ID": CID, "X-NCP-APIGW-API-KEY": SEC})
    last = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                time.sleep(0.12)
                data = json.load(r)
            if "items" in data:
                return data
            if "total" in data:  # 결과가 0건이면 네이버가 items 칸을 빼고 보냄 → 빈 결과
                data["items"] = []
                return data
            last = data  # 성공 코드인데 결과 대신 오류 내용이 온 경우 → 잠시 뒤 다시
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504):
                raise
            last = e.code
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
        time.sleep(2 * (attempt + 1))
    print(f"  ! 검색 실패({query}, {kind}, start={start}): {last} → 빈 결과로 처리", flush=True)
    return {"total": 0, "items": []}

TAG = re.compile(r"<[^>]+>")
def clean(s):
    return html.unescape(TAG.sub("", s or "")).strip()


def city_dir(C):
    """도시별 수집 캐시 폴더 data/<slug>/ (깃에 올리지 않음)."""
    d = ROOT / "data" / C.SLUG
    d.mkdir(parents=True, exist_ok=True)
    return d


def has_context(text, C):
    """글에 이 도시를 가리키는 말(CONTEXT)이 들어 있는지."""
    return any(c in text for c in C.CONTEXT)

