# 현지 트렌드 여행 서비스 — Django 백엔드

## 시작하기 전에

1. `context.md` 를 먼저 읽고 서비스 전체 기획을 파악할 것
2. Gemini API 키 발급 필요 → https://aistudio.google.com/

---

## 개발 목표 (데모)

아이디어톤 데모용 백엔드 구현.
실현 가능성 검증이 목적이므로 핵심 기능 3개만 구현한다.

### 구현할 기능
1. **도시별 트렌드 Top 10** — `GET /api/trends/?city=tokyo`
2. **카테고리별 트렌드** — `GET /api/trends/category/?city=tokyo&category=food`
3. **월별 카드뉴스** — `GET /api/monthly/?city=tokyo&month=5`

### 구현하지 않는 것 (데모 범위 외)
- 회원가입/로그인
- 저장함 기능
- Trend to Route
- 지역 가이드

---

## 세팅 순서

```bash
# 1. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. .env 파일 생성
cp .env.example .env
# .env에 GEMINI_API_KEY 입력

# 4. Django 세팅
python manage.py migrate
python manage.py runserver
```

---

## API 테스트

```bash
# 트렌드 Top 10
curl http://localhost:8000/api/trends/?city=tokyo

# 카테고리별 트렌드
curl http://localhost:8000/api/trends/category/?city=tokyo&category=food

# 월별 카드뉴스
curl http://localhost:8000/api/monthly/?city=tokyo&month=5
```

---

## Claude Code에게 요청할 작업 순서

1. Django 프로젝트 초기 세팅
2. trends 앱 생성 및 구조 잡기
3. pytrends로 Google Trends 데이터 추출 로직 구현
4. Gemini API 연동 및 분석 로직 구현
5. Django REST Framework API 엔드포인트 구현
6. 테스트 및 디버깅

---

## 참고

- `context.md` — 전체 서비스 기획 및 API 스펙
- `requirements.txt` — 필요 패키지 목록
- Gemini API 문서: https://ai.google.dev/docs
- pytrends 문서: https://github.com/GeneralMills/pytrends
