# 프로젝트 컨텍스트 — 현지 트렌드 여행 서비스

## 서비스 개요

**한 줄 설명**: AI가 현지 검색 트래픽을 실시간 분석해 여행자에게 현지인의 지금 트렌드를 알려주는 서비스

**핵심 문제**
> 여행자는 구글 검색·블로그·유튜브에 의존하지만 이 정보들은 오래된 리뷰나 외국인 시각의 콘텐츠다.
> 현지인들 사이에서 지금 막 유행하는 음식, 장소, 행사는 현지 검색 트래픽 안에 있지만
> 언어 장벽과 플랫폼 장벽으로 인해 여행자는 접근할 수 없다.

**솔루션**
> AI가 현지 검색 트래픽(Google Trends)을 실시간 분석해
> 1~2주 내 급상승 트렌드를 탐지하고 카테고리별로 큐레이션해서 제공한다.
> 저장한 트렌드를 바탕으로 하루 여행 루트까지 자동 생성해준다.

---

## 트렌드 카테고리 (5개)

| 카테고리 | 설명 | 예시 |
|---|---|---|
| 음식·음료 | 유행 음식, 음료, 식당 | 마라탕, 버터떡, 흑임자라떼 |
| 장소 | 관광지, 카페, 공원, 뷰포인트 | 낙산공원, 한강공원 |
| 쇼핑 | 트렌드 아이템, 편집숍 | 빈티지 나이키, 로컬 브랜드 |
| 액티비티 | 체험, 야외활동 | 러닝크루, 서핑, 피크닉 |
| 문화 | 전시, 공연, 페스티벌 | 팝업스토어, 인디공연 |

---

## Trend Life Cycle (3단계)

| 단계 | 설명 |
|---|---|
| Rookie | 막 떠오르는 중 (1~2주 내 급상승) |
| Trending | 빠르게 확산 중 |
| Tourist-heavy | 관광객에게 많이 알려짐 |

---

## 구현할 핵심 기능 (데모 범위 - 3가지)

### 1. 실시간 트렌드 확인
- Google Trends에서 도시별 급상승 키워드 추출
- Gemini API로 카테고리 분류 + Trend Life Cycle 판별 + 맥락 설명 생성
- JSON 형태로 반환

### 2. Trend Life Cycle
- 키워드 시계열 데이터 기반으로 단계 판별
- Rookie / Trending / Tourist-heavy 3단계
- 트렌드 확인 API 응답에 포함

### 3. Trend to Route
- 사용자가 저장한 트렌드 키워드를 입력받아
- Gemini API가 하루 여행 루트 자동 생성
- 아침·점심·저녁·밤 시간대별 구성

---

## 구현하지 않는 것 (데모 범위 외)

- 회원가입 / 로그인
- 저장함 DB 저장
- 월별 카드뉴스
- 지역 가이드
- 카테고리별 필터링
- Local Proof

---

## API 엔드포인트 정의

### 1. 실시간 트렌드 Top 10 (Trend Life Cycle 포함)
```
GET /api/trends/?city=tokyo

Response:
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

### 2. Trend to Route
```
POST /api/route/
Request:
{
  "city": "tokyo",
  "saved_trends": ["마라탕", "우라하라주쿠", "빈티지 나이키"]
}

Response:
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

## 기술 스택

```
Backend   : Django 4.2 + Django REST Framework
Trend     : pytrends (Google Trends 비공식 라이브러리)
AI        : google-generativeai (Gemini API)
DB        : SQLite (데모용)
가상환경   : Poetry
```

---

## 프로젝트 구조

```
travel-trend/
├── manage.py
├── pyproject.toml
├── .env
├── context.md
├── README.md
├── config/
│   ├── settings.py
│   └── urls.py
└── trends/
    ├── views.py
    ├── services/
    │   ├── __init__.py
    │   ├── trends_service.py   ← Google Trends 데이터 추출
    │   └── gemini_service.py   ← Gemini API 분석·가공
    ├── serializers.py
    ├── urls.py
    └── models.py
```

---

## 환경변수 (.env)

```
GEMINI_API_KEY=your_gemini_api_key_here
DEBUG=True
SECRET_KEY=your_django_secret_key_here
```

---

## 데이터 흐름

### 트렌드 확인
```
GET /api/trends/?city=tokyo
      ↓
trends_service.py
→ pytrends로 도시 급상승 키워드 추출
      ↓
gemini_service.py
→ 카테고리 분류 + Life Cycle 판별 + 맥락 설명 생성
      ↓
JSON 응답 반환
```

### Trend to Route
```
POST /api/route/
→ saved_trends 키워드 목록 수신
      ↓
gemini_service.py
→ 도시 + 키워드 기반 하루 루트 생성
      ↓
시간대별 루트 JSON 반환
```

---

## 주의사항

- pytrends는 Google Trends 비공식 라이브러리로 rate limit 있음 → 캐싱 권장
- Gemini API 응답은 항상 JSON 파싱 예외처리 필요
- 데모용이므로 인증(JWT 등) 생략
- CORS 설정 필요 (프론트 연동 시)
- Gemini API 응답을 JSON으로 받으려면 프롬프트에 "JSON으로만 응답해줘" 명시 필요
