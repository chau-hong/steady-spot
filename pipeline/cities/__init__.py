"""도시 설정 모음. 새 도시는 cities/<slug>.py 를 만들고 CITIES 에 추가해요."""
import importlib, sys

CITIES = ["okinawa", "fukuoka", "tokyo"]   # 허브 페이지에 보이는 순서


def load(slug=None):
    """--city <slug> 인자(없으면 okinawa)의 설정 모듈을 돌려준다."""
    if slug is None:
        slug = sys.argv[sys.argv.index("--city") + 1] if "--city" in sys.argv else "okinawa"
    m = importlib.import_module(f"cities.{slug}")
    for k, v in (("Q", {}), ("CHAIN", {}), ("EXTRA", {}), ("MAPQ", {}), ("PLACES", []), ("QUERIES_EXTRA", []), ("IGNORE", [])):
        if not hasattr(m, k):
            setattr(m, k, v)
    return m
