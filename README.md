# steady-spot

여행지에서 **꾸준히 많이 찾는 스테디 명소**를 네이버 검색 3년 추세와 블로그·카페 글로 고르는 페이지예요. 지금은 오키나와부터 시작했어요.

- 페이지: https://chau-hong.github.io/steady-spot/
- 저장소: https://github.com/chau-hong/steady-spot

## 구성

`docs/` 폴더가 GitHub Pages로 공개되고, GitHub Actions가 매달 모든 도시의 데이터를 새로 받아 갱신해요.

- 도시 목록: https://chau-hong.github.io/steady-spot/
- 오키나와: https://chau-hong.github.io/steady-spot/okinawa/
- 후쿠오카: https://chau-hong.github.io/steady-spot/fukuoka/
- 도쿄: https://chau-hong.github.io/steady-spot/tokyo/

| 경로 | 내용 |
|---|---|
| `docs/index.html` | 도시 목록 페이지 (배치가 자동 생성) |
| `docs/<도시>/` | 도시별 페이지와 데이터 (배치가 자동 생성) |
| `pipeline/cities/<도시>.py` | 도시별 설정: 검색어, 지역 이름, 기준 장소, **장소 목록**, 구글맵 검색어 |
| `web/page.template.html` | 도시 페이지 템플릿. 화면을 고칠 때는 여기를 수정해요 |
| `web/standalone_head.html` | GitHub Pages용 색·글꼴과 데이터 연결 코드 |
| `web/picks/<도시>.json` | **silk pick!** 목록. 직접 고쳐도 돼요 |
| `pipeline/update.py` | 전체 갱신을 한 번에 실행 |
| `reports/<도시>_new_candidates.md` | 장소 목록에 없는 새 장소 후보 (배치가 매번 갱신) |

## 처음 설정 (한 번만)

1. 이 폴더를 GitHub 저장소로 올려요. `.env`(API 키)는 `.gitignore`에 있어서 올라가지 않아요. (완료)
2. 저장소 **Settings → Secrets and variables → Actions → New repository secret**에서 두 개를 추가해요.
   - `NAVER_CLIENT_ID`
   - `NAVER_CLIENT_SECRET`
3. **Settings → Pages**에서 Source를 `Deploy from a branch`, Branch를 `main` / `/docs`로 지정해요.
4. **Actions** 탭에서 "월간 데이터 갱신"을 열고 **Run workflow**로 한 번 실행해 동작을 확인해요.

이후에는 매월 2일 오전 9시(한국 시간)에 자동으로 갱신돼요.

## 직접 실행할 때

프로젝트 폴더에 `.env` 파일을 만들고 두 줄을 넣어요. 이 파일은 `.gitignore`에 있어서 GitHub에 올라가지 않아요.

```
NAVER_CLIENT_ID=발급받은 ID
NAVER_CLIENT_SECRET=발급받은 Secret
```

```bash
python3 pipeline/update.py                    # 모든 도시 전체 갱신 (도시당 15~25분, 검색 API 약 2,000회)
python3 pipeline/update.py --city fukuoka     # 한 도시만
python3 pipeline/update.py --skip-collect     # 글 수집 없이 지표·추세만 갱신
python3 pipeline/update.py --build-only       # API 호출 없이 페이지만 다시 생성
```

`--build-only`는 `web/picks/`나 템플릿만 고쳤을 때 써요. 이전에 수집한 `data/` 폴더가 있어야 해요.

## 자주 하는 작업

- **silk pick! 추가·수정**: `web/picks/<도시>.json`에 `{"name": "장소 이름", "note": "메모"}`를 추가해요. 이름은 도시 설정의 대표 이름과 같아야 해요. 지점이 여러 곳인 곳은 `"mapQuery": "구글맵 검색어"`로 특정 지점을 지정할 수 있어요.
- **장소 추가**: `reports/<도시>_new_candidates.md`를 보고 `pipeline/cities/<도시>.py`의 `PLACES`에 `(이름, 분류, 지역, [별칭])`을, `MAPQ`에 구글맵 검색어(일본어 명칭 권장)를 추가해요. 검색어 트렌드용 검색어가 따로 필요하면 같은 파일의 `EXTRA`에 넣어요.
- **도시 추가**: `pipeline/cities/`에 설정 파일을 하나 만들고 `pipeline/cities/__init__.py`의 `CITIES`에 추가해요. 처음에는 `PLACES = []`로 두고 배치를 돌리면 후보 리포트가 나와요.
- **장소가 아닌 후보 숨기기**: `pipeline/ignore_candidates.txt`에 한 줄씩 추가해요.

## 지표

- **검색지수**: 네이버 검색어 트렌드 월별 검색량. 도시마다 기준 장소(오키나와 만좌모, 후쿠오카 캐널시티, 도쿄 도쿄타워)의 36개월 월평균 = 100
- **꾸준함**: 세 해 중 가장 적게 찾은 해 ÷ 가장 많이 찾은 해
- **스테디 점수**: 3년 평균 검색지수 × 꾸준함
- **등급**: 필수 스테디(점수 30 이상·꾸준함 50% 이상), 꾸준한 곳(점수 5 이상·꾸준함 50% 이상), 변동 큼, 검색 적음

## API 사용량 (1회 전체 갱신 기준)

- 검색 API(블로그·카페): 도시당 약 1,500~2,000회 / 하루 한도 25,000회
- 검색어 트렌드 API: 도시당 약 25~40회 / 하루 한도 1,000회
