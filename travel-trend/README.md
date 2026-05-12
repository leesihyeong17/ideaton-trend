# 현지 트렌드 여행 서비스 — Django 백엔드

## 서비스 개요

AI가 현지 검색 트래픽을 실시간 분석해 여행자에게 현지인의 지금 트렌드를 알려주는 서비스.
저장한 트렌드를 바탕으로 하루 여행 루트까지 자동 생성해준다.

---

## 구현된 기능

| 기능 | 엔드포인트 | 설명 |
|---|---|---|
| 실시간 트렌드 Top 10 | `GET /api/trends/?city=tokyo` | 도시별 급상승 키워드 + Life Cycle + 맥락 설명 |
| 카테고리별 랭킹 | `GET /api/trends/categories/?city=tokyo` | 5개 카테고리별 트렌드 그룹핑 |
| Trend to Route | `POST /api/route/` | 저장한 트렌드 기반 하루 여행 루트 생성 |

---

## 프로젝트 구조

```
travel-trend/
├── manage.py
├── pyproject.toml
├── poetry.lock
├── .env                        ← 직접 생성 필요 (깃에 없음)
├── .env.example                ← 환경변수 템플릿
├── context.md                  ← 서비스 전체 기획
├── config/
│   ├── settings.py             ← dotenv, DRF, CORS 설정
│   └── urls.py                 ← /api/ → trends.urls 연결
└── trends/
    ├── views.py                ← TrendsView, CategoryRankingView, RouteView
    ├── urls.py                 ← URL 라우팅
    └── services/
        ├── trends_service.py   ← pytrends 급상승 키워드 추출 + Life Cycle 계산
        └── gemini_service.py   ← Gemini API 분석·루트 생성
```

---

## 기술 스택

```
Backend   : Django 4.2 + Django REST Framework
Trend     : pytrends (Google Trends 비공식 라이브러리)
AI        : google-genai (Gemini 2.5-flash)
DB        : SQLite (데모용)
가상환경   : Poetry
```

---

## 시작하기

### 1. 레포 클론
```bash
git clone https://github.com/유저명/travel-trend.git
cd travel-trend/travel-trend
```

### 2. Poetry 설치 확인
```bash
poetry --version
# 없으면
pip install poetry
```

### 3. 패키지 설치
```bash
poetry install
```

### 4. 가상환경 진입
```bash
poetry shell
```

### 5. .env 파일 생성
`.env.example` 참고해서 `.env` 직접 생성
```
GEMINI_API_KEY=발급받은_Gemini_API_키
DEBUG=True
SECRET_KEY=django-insecure-아무문자열
```

> Gemini API 키 발급: https://aistudio.google.com/

### 6. 서버 실행
```bash
poetry run python manage.py runserver
```

---

## API 명세

### 트렌드 Top 10 조회
```
GET /api/trends/?city=tokyo
```

- pytrends로 급상승 키워드 추출 → Gemini로 카테고리/라이프사이클/설명 분석
- pytrends 실패 시 Gemini가 직접 생성 (fallback)
- 결과 10분 캐싱

Response 예시
```json
{
  "city": "tokyo",
  "updated_at": "2026-05-12T10:00:00",
  "trends": [
    {
      "rank": 1,
      "keyword": "마라탕",
      "category": "음식·음료",
      "life_cycle": "Trending",
      "context": "최근 도쿄에서 마라탕 열풍이 불고 있어요.",
      "rising_percentage": 320
    }
  ]
}
```

---

### 카테고리별 랭킹 조회
```
GET /api/trends/categories/?city=tokyo
```

- `/api/trends/`와 동일한 캐시 데이터를 category 기준으로 그룹핑해서 반환
- 별도 Gemini 호출 없음 (캐시 미존재 시 자동 생성)

Response 예시
```json
{
  "city": "tokyo",
  "updated_at": "2026-05-12T10:00:00",
  "categories": {
    "음식·음료": [
      { "rank": 1, "keyword": "마라탕", "life_cycle": "Trending", "context": "...", "rising_percentage": 320 }
    ],
    "장소": [ ... ],
    "쇼핑": [ ... ],
    "액티비티": [ ... ],
    "문화": [ ... ]
  }
}
```

---

### Trend to Route 생성
```
POST /api/route/
Content-Type: application/json
```

- 프론트에서 선택한 키워드 배열을 받아 Gemini가 시간대별 하루 일정 생성
- 키워드마다 최소 1개 일정 포함

Request
```json
{
  "city": "tokyo",
  "saved_trends": ["마라탕", "우라하라주쿠", "빈티지 나이키"]
}
```

Response 예시
```json
{
  "city": "tokyo",
  "route": [
    {
      "time": "아침",
      "keyword": "우라하라주쿠",
      "place": "우라하라주쿠 편집숍 골목",
      "description": "도쿄 스트릿 패션의 성지, 오전에 여유롭게 둘러보기 좋아요."
    },
    {
      "time": "점심",
      "keyword": "마라탕",
      "place": "신주쿠 마라탕 맛집",
      "description": "요즘 도쿄에서 가장 핫한 마라탕 거리."
    },
    {
      "time": "저녁",
      "keyword": "빈티지 나이키",
      "place": "시모키타자와 빈티지숍",
      "description": "현지인들이 즐겨 찾는 빈티지 나이키 셀렉숍."
    }
  ]
}
```

---

## 지원 도시

| 도시 | 파라미터 |
|---|---|
| 도쿄 | `tokyo` |
| 오사카 | `osaka` |
| 서울 | `seoul` |
| 부산 | `busan` |
| 파리 | `paris` |
| 런던 | `london` |
| 뉴욕 | `newyork` |
| 방콕 | `bangkok` |
| 싱가포르 | `singapore` |
| 홍콩 | `hongkong` |
| 타이베이 | `taipei` |
| 발리 | `bali` |

> pytrends가 지원하지 않는 도시도 Gemini fallback으로 처리됩니다.

---

## 주요 구현 포인트

**캐시 구조**
- 트렌드 데이터를 모듈 레벨 dict에 10분간 캐싱
- `/api/trends/`와 `/api/trends/categories/` 가 동일한 캐시 공유
- Gemini API 중복 호출 방지

**데이터 흐름**
```
GET /api/trends/
  → pytrends 급상승 키워드 20개 추출
  → Gemini 카테고리/라이프사이클/설명 분석
  → 실패 시 Gemini가 직접 50개 생성 (fallback)
  → 캐시 저장, Top 10 반환

GET /api/trends/categories/
  → 캐시에서 category 기준 그룹핑 후 반환

POST /api/route/
  → 키워드 배열 + 도시 → Gemini 하루 루트 생성
```

**Trend Life Cycle 판별 기준**

| 단계 | 기준 |
|---|---|
| Rookie | 최근 1~2주 내 급상승, 아직 확산 초기 |
| Trending | 빠르게 확산 중, 검색량 급증 |
| Tourist-heavy | 이미 널리 알려짐, 관광객 유입 많음 |

---

## 참고

- `context.md` — 서비스 전체 기획 및 API 스펙
- Gemini API 문서: https://ai.google.dev/docs
- pytrends 문서: https://github.com/GeneralMills/pytrends
