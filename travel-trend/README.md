# 현지 트렌드 여행 서비스 — Django 백엔드

## 서비스 개요

AI가 현지 검색 트래픽을 실시간 분석해 여행자에게 현지인의 지금 트렌드를 알려주는 서비스.
저장한 트렌드를 바탕으로 하루 여행 루트까지 자동 생성해준다.

---

## 구현된 기능

| 기능 | 엔드포인트 | 설명 |
|---|---|---|
| 실시간 트렌드 Top 10 | `GET /api/trends/?city=tokyo` | 도시별 급상승 키워드 + Life Cycle + 맥락 설명 |
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
    ├── views.py                ← TrendsView (GET), RouteView (POST)
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
AI        : google-genai 2.0 (Gemini API 신규 SDK)
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

## API 테스트

### 트렌드 Top 10 조회
```bash
GET http://localhost:8000/api/trends/?city=tokyo
```

Response 예시
```json
{
  "city": "tokyo",
  "updated_at": "2025-05-12T10:00:00",
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

### Trend to Route 생성
```bash
POST http://localhost:8000/api/route/
Content-Type: application/json

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
| 서울 | `seoul` |
| 파리 | `paris` |
| 뉴욕 | `new_york` |
| 런던 | `london` |
| 방콕 | `bangkok` |
| 바르셀로나 | `barcelona` |
| 로마 | `rome` |
| 시드니 | `sydney` |
| 싱가포르 | `singapore` |

---

## 주요 구현 포인트

**trends_service.py**
- 도시명 → (pn, geo) 매핑으로 Google Trends 지역 필터링
- `interest_over_time()` 배치 호출 (5개씩) → rate limit 대응
- 모듈 레벨 dict로 10분 캐싱 (`_CACHE_TTL = 600`)

**gemini_service.py**
- `google-genai` 2.0 신규 SDK 사용
- `response_mime_type: application/json` 으로 JSON 강제 출력
- 마크다운 코드블록 fallback 파서 포함

---

## Trend Life Cycle 판별 기준

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
