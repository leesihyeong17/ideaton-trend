# 프로젝트 컨텍스트 — 현지 트렌드 여행 서비스

## 서비스 개요

**서비스명**: (미정)
**한 줄 설명**: AI가 현지 SNS·검색 트래픽을 실시간 분석해 여행자에게 현지인의 지금 트렌드를 알려주는 서비스

**핵심 문제**
> 여행자는 구글 검색·블로그·유튜브에 의존하지만 이 정보들은 오래된 리뷰나 외국인 시각의 콘텐츠다.
> 현지인들 사이에서 지금 막 유행하는 음식, 장소, 행사는 현지 SNS와 검색 트래픽 안에 있지만
> 언어 장벽과 플랫폼 장벽으로 인해 여행자는 접근할 수 없다.

**솔루션**
> AI가 현지 검색 트래픽(Google Trends 등)을 실시간 분석해
> 1~2주 내 급상승 트렌드를 탐지하고 카테고리별로 큐레이션해서 제공한다.

---

## 트렌드 카테고리 (5개)

| 카테고리 | 설명 | 키워드 예시 |
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

## 핵심 기능 (데모 범위)

### 1. 도시별 트렌드 Top 10
- Google Trends에서 도시별 급상승 키워드 추출
- Gemini API로 카테고리 분류 + Trend Life Cycle 판별 + 맥락 설명 생성
- JSON 형태로 반환

### 2. 카테고리별 트렌드
- 특정 카테고리(음식·장소·쇼핑·액티비티·문화)로 필터링된 트렌드 반환

### 3. 월별 카드뉴스
- 도시 + 월 입력 시
- Gemini API가 해당 도시·월의 날씨·음식·행사·쇼핑·현지인 팁 생성

---

## API 엔드포인트 정의

### 1. 트렌드 Top 10
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
      "context": "최근 도쿄에서 마라탕 열풍이 불고 있어요. 한국식 마라탕이 현지화되어...",
      "rising_percentage": 320
    },
    ...
  ]
}
```

### 2. 카테고리별 트렌드
```
GET /api/trends/category/?city=tokyo&category=food

Response:
{
  "city": "tokyo",
  "category": "음식·음료",
  "trends": [ ... ]
}
```

### 3. 월별 카드뉴스
```
GET /api/monthly/?city=tokyo&month=5

Response:
{
  "city": "tokyo",
  "month": 5,
  "weather": "5월 도쿄는 평균 20도로 따뜻하고 맑은 날씨...",
  "food": ["가츠오부시 냉라멘", "딸기 디저트"],
  "events": ["골든위크", "아사쿠사 삼바 페스티벌"],
  "shopping": ["여름 유카타 시즌 시작", "편집숍 신상 출시"],
  "tips": ["골든위크 기간 인파 주의", "자외선 차단제 필수"]
}
```

---

## 기술 스택

```
Backend:  Django 4.x + Django REST Framework
Trend:    pytrends (Google Trends 비공식 라이브러리)
AI:       google-generativeai (Gemini API)
DB:       SQLite (데모용) → PostgreSQL (실서비스)
```

---

## 프로젝트 구조

```
travel_trend/
├── manage.py
├── requirements.txt
├── .env                    ← API 키 관리
├── config/
│   ├── settings.py
│   └── urls.py
└── trends/
    ├── views.py            ← API 엔드포인트
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
```

---

## 데이터 흐름

```
1. 클라이언트 → GET /api/trends/?city=tokyo

2. trends_service.py
   → pytrends로 도쿄 관련 급상승 키워드 추출
   → 키워드 리스트 반환

3. gemini_service.py
   → 키워드 리스트를 Gemini에게 전달
   → 카테고리 분류 + Life Cycle 판별 + 맥락 설명 생성
   → 구조화된 JSON 반환

4. views.py
   → 최종 JSON 응답 반환
```

---

## 주의사항

- pytrends는 Google Trends 비공식 라이브러리로 rate limit 있음 → 캐싱 필요
- Gemini API 응답은 항상 JSON 파싱 예외처리 필요
- 데모용이므로 인증(JWT 등)은 생략 가능
- CORS 설정 필요 (프론트와 연동 시)
