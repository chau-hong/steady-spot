"""한 번에 갱신: 도시마다 글 수집 → 장소별 지표 → 36개월 검색 추세 → 새 장소 후보 리포트, 마지막에 공개 파일·페이지 생성.

사용법
  python3 pipeline/update.py                     # 모든 도시 전체 갱신 (도시당 API 약 2,000회, 15~25분)
  python3 pipeline/update.py --city fukuoka      # 한 도시만
  python3 pipeline/update.py --skip-collect      # 글 수집은 건너뛰고 지표·추세·페이지만
  python3 pipeline/update.py --build-only        # API 호출 없이 페이지만 다시 생성 (픽·템플릿 수정 후)
장소 목록(PLACES)이 아직 비어 있는 도시는 글 수집과 후보 리포트만 해요.
"""
import subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from cities import CITIES, load  # noqa: E402

args = sys.argv[1:]
only = args[args.index("--city") + 1] if "--city" in args else None
cities = [only] if only else CITIES


def run(title, script, *extra):
    t = time.time()
    print(f"\n▶ {title} ({script} {' '.join(extra)})", flush=True)
    r = subprocess.run([sys.executable, script, *extra], cwd=HERE)
    if r.returncode != 0:
        sys.exit(f"실패: {script} {' '.join(extra)} (종료 코드 {r.returncode})")
    print(f"  완료 {time.time() - t:.0f}초", flush=True)


for slug in cities:
    C = load(slug)
    print(f"\n===== {C.NAME} =====", flush=True)
    if "--build-only" in args:
        continue
    if "--skip-collect" not in args:
        run(f"{C.NAME} 글 수집", "collect.py", "--city", slug)
    if C.PLACES:
        run(f"{C.NAME} 장소별 블로그·카페 지표", "enrich.py", "--city", slug)
        run(f"{C.NAME} 36개월 검색 추세·스테디 점수", "trend.py", "--city", slug)
    run(f"{C.NAME} 새 장소 후보 리포트", "find_candidates.py", "--city", slug)

run("공개 데이터·페이지 생성", "build.py", *(["--city", only] if only else []))
print("\n모두 완료. docs/ 를 커밋하면 GitHub Pages 에 반영돼요.")
