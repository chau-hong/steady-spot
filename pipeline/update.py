"""한 번에 갱신: 글 수집 → 장소별 지표 → 36개월 검색 추세 → 공개 파일·페이지 생성 → 새 장소 후보 리포트.

사용법
  python3 pipeline/update.py              # 전체 갱신 (API 약 1,500~2,000회, 15~25분)
  python3 pipeline/update.py --skip-collect  # 글 수집은 건너뛰고 지표·추세·페이지만 갱신
  python3 pipeline/update.py --build-only    # API 호출 없이 페이지만 다시 생성 (picks.json·템플릿 수정 후)
"""
import subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
args = set(sys.argv[1:])
steps = []
if not args & {"--skip-collect", "--build-only"}:
    steps += [("오키나와 여행 글 수집", "collect.py"), ("지역·분류별 글 추가 수집", "collect2.py")]
if "--build-only" not in args:
    steps += [("장소별 블로그·카페 지표", "enrich.py"), ("36개월 검색 추세·스테디 점수", "trend.py")]
steps += [("공개 데이터·페이지 생성", "build.py"), ("새 장소 후보 리포트", "find_candidates.py")]

for i, (title, script) in enumerate(steps, 1):
    t = time.time()
    print(f"\n[{i}/{len(steps)}] {title} ({script})", flush=True)
    r = subprocess.run([sys.executable, script], cwd=HERE)
    if r.returncode != 0:
        sys.exit(f"실패: {script} (종료 코드 {r.returncode})")
    print(f"  완료 {time.time() - t:.0f}초", flush=True)
print("\n모두 완료. docs/ 를 커밋하면 GitHub Pages 에 반영돼요.")
