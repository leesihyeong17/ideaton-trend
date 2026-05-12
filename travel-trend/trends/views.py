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
