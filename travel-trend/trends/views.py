import time
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services.trends_service import get_trending_keywords
from .services.gemini_service import analyze_trends, generate_route, generate_trends_fallback

_trends_cache: dict = {}
_TRENDS_CACHE_TTL = 600  # 10분


def _get_or_fetch_trends(city: str) -> list[dict]:
    now = time.time()
    cached = _trends_cache.get(city)
    if cached and now - cached['ts'] < _TRENDS_CACHE_TTL:
        return cached['trends']

    try:
        raw_trends = get_trending_keywords(city, top_n=20)
        trends = analyze_trends(city, raw_trends)
    except Exception:
        trends = generate_trends_fallback(city, top_n=50)

    _trends_cache[city] = {'trends': trends, 'ts': now}
    return trends


class TrendsView(APIView):
    def get(self, request):
        city = request.query_params.get('city', 'tokyo').strip().lower()

        try:
            trends = _get_or_fetch_trends(city)
        except Exception as e:
            return Response(
                {'error': f'트렌드 데이터 생성에 실패했습니다: {str(e)}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({
            'city': city,
            'updated_at': datetime.now().isoformat(timespec='seconds'),
            'trends': trends[:10],
        })


class CategoryRankingView(APIView):
    def get(self, request):
        city = request.query_params.get('city', 'tokyo').strip().lower()

        try:
            trends = _get_or_fetch_trends(city)
        except Exception as e:
            return Response(
                {'error': f'카테고리 랭킹 생성에 실패했습니다: {str(e)}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        grouped: dict = {}
        for trend in trends:
            cat = trend.get('category', '기타')
            grouped.setdefault(cat, [])
            rank = len(grouped[cat]) + 1
            grouped[cat].append({**trend, 'rank': rank})

        return Response({
            'city': city,
            'updated_at': datetime.now().isoformat(timespec='seconds'),
            'categories': grouped,
        })


class RouteView(APIView):
    def post(self, request):
        city = request.data.get('city', 'tokyo')
        saved_trends = request.data.get('saved_trends', [])

        if not saved_trends or not isinstance(saved_trends, list):
            return Response(
                {'error': 'saved_trends 배열이 필요합니다.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            route = generate_route(city, saved_trends)
        except Exception as e:
            return Response(
                {'error': f'루트 생성에 실패했습니다: {str(e)}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({
            'city': city,
            'route': route,
        })

class TravelTrendStaticView(APIView):
    def get(self, request):
        # 1. 수집해 놓은 데이터 리스트 (예시 데이터)
        # 실제 데이터가 파일이나 특정 함수 결과물이라면 그걸 불러오시면 됩니다.
        saved_data = [
            {
                "rank": 1,
                "keyword": "체험형 컨셉 카페",
                "category": "음료/카페/바",
                "life_cycle": "Rookie",
                "context": "도쿄 Z세대는 이제 \"음료\"보다 경험 콘텐츠",
                "rising_percentage": 250
            },
            {
                "rank": 2,
                "keyword": "Love Type 16",
                "category": "유행어/밈/로컬이슈",
                "life_cycle": "Hot",
                "context": "MBTI의 16가지 유형을 연애스타일로 재해석한 심리테스트",
                "rising_percentage": 180
            },
             {
                "rank": 3,
                "keyword": "달바 트러플 미스트",
                "category": "스타일/뷰티트랜드",
                "life_cycle": "Steady",
                "context": "피부를 5초 만에 생기 있게 하는 \'가방 속 필수 아이템\'",
                "rising_percentage": 180
            },
            {
                "rank": 4,
                "keyword": "호지차 디저트",
                "category": "음식",
                "life_cycle": "Hot",
                "context": "고소한 볶은 차 향을 담은 푸딩∙파르페∙라떼 디저트, 말차보다 부드러운 맛으로 주목받는 중",
                "rising_percentage": 250
            },
            {
                "rank": 5,
                "keyword": "생도넛",
                "category": "음식",
                "life_cycle": "Rising",
                "context": "브리오슈 반죽으로 만든 부드럽고 촉촉한 식감의 도넛, 후쿠오카에서 시작해 도쿄에서 인기 확산 중",
                "rising_percentage": 180
            },
             {
                "rank": 6,
                "keyword": "딸기산도",
                "category": "음식",
                "life_cycle": "Steady",
                "context": "비주얼 중심 카페에서 다시 유행 중인 일본식 과일 샌드",
                "rising_percentage": 180
            },
            {
                "rank": 7,
                "keyword": "멜론 카키고리",
                "category": "음식",
                "life_cycle": "Hot",
                "context": "백화점 디저트층과 호텔 카페 중심으로 급상승 중인 멜론 빙수",
                "rising_percentage": 180
            }
        ]
        
        # 2. Response에 데이터를 그대로 담아서 반환 (DRF가 자동으로 JSON으로 변환해 줌)
        return Response(saved_data, status=status.HTTP_200_OK)