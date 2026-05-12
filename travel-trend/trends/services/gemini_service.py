import json
import re
from google import genai
from google.genai import types
from django.conf import settings

_client = genai.Client(api_key=settings.GEMINI_API_KEY)
_MODEL = 'gemini-2.5-flash'
_JSON_CONFIG = types.GenerateContentConfig(response_mime_type='application/json')


def generate_trends_fallback(city: str, top_n: int = 10) -> list[dict]:
    """pytrends 실패 시 Gemini가 직접 트렌드 데이터를 생성."""
    prompt = f"""
당신은 여행 트렌드 분석 전문가입니다.
{city}에서 지금 현지인들 사이에 실제로 유행 중인 트렌드 키워드 {top_n}개를 만들어주세요.
음식·음료, 장소, 쇼핑, 액티비티, 문화 카테고리를 고르게 포함하세요.

아래 형식의 JSON 배열만 반환하세요:
[
  {{
    "rank": 1,
    "keyword": "키워드",
    "category": "음식·음료" | "장소" | "쇼핑" | "액티비티" | "문화",
    "life_cycle": "Rookie" | "Trending" | "Tourist-heavy",
    "context": "{city}에서 이 키워드가 왜 지금 트렌드인지 한국어로 1~2문장",
    "rising_percentage": 50~500 사이 정수
  }}
]
""".strip()

    response = _client.models.generate_content(
        model=_MODEL,
        contents=prompt,
        config=_JSON_CONFIG,
    )
    return _parse_json(response.text)


def analyze_trends(city: str, raw_trends: list[dict]) -> list[dict]:
    prompt = f"""
당신은 여행 트렌드 분석 전문가입니다.
아래는 {city}의 Google Trends 급상승 키워드 목록입니다.

키워드 데이터:
{json.dumps(raw_trends, ensure_ascii=False)}

각 키워드에 대해 아래 필드를 포함한 JSON 배열을 반환하세요.

필드 설명:
- rank: 순위 (원본 유지)
- keyword: 키워드 (원본 유지)
- category: 다음 5가지 중 정확히 하나 → "음식·음료" | "장소" | "쇼핑" | "액티비티" | "문화"
- life_cycle: 다음 3가지 중 정확히 하나 → "Rookie" | "Trending" | "Tourist-heavy"
  (life_cycle 참고하되, 키워드 성격에 맞게 최종 판단)
- context: {city}에서 이 키워드가 왜 트렌드인지 한국어로 1~2문장
- rising_percentage: 원본 유지 (정수)

JSON 배열만 반환하세요.
""".strip()

    response = _client.models.generate_content(
        model=_MODEL,
        contents=prompt,
        config=_JSON_CONFIG,
    )
    return _parse_json(response.text)


def generate_route(city: str, saved_trends: list[str]) -> list[dict]:
    prompt = f"""
당신은 현지 트렌드를 잘 아는 여행 플래너입니다.

도시: {city}
트렌드 키워드: {', '.join(saved_trends)}

위 키워드를 활용해 {city}에서의 하루 여행 루트를 JSON 배열로 생성하세요.
아침·점심·저녁(필요시 밤 추가) 시간대별로 구성하고, 키워드마다 최소 1개 일정을 포함하세요.

각 항목 형식:
{{
  "time": "아침" 또는 "점심" 또는 "저녁" 또는 "밤",
  "keyword": "사용된 트렌드 키워드",
  "place": "구체적인 장소명 (지역·상호명 포함)",
  "description": "한국어로 1~2문장, 왜 지금 여기가 핫한지 설명"
}}

JSON 배열만 반환하세요.
""".strip()

    response = _client.models.generate_content(
        model=_MODEL,
        contents=prompt,
        config=_JSON_CONFIG,
    )
    return _parse_json(response.text)


def _parse_json(text: str):
    text = text.strip()
    match = re.search(r'```(?:json)?\s*([\s\S]+?)\s*```', text)
    if match:
        text = match.group(1).strip()
    return json.loads(text)
