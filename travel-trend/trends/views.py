import time
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services.trends_service import get_trending_keywords
from .services.gemini_service import analyze_trends, generate_route, generate_trends_fallback

_trends_cache: dict = {}
_TRENDS_CACHE_TTL = 600  # 10분


class TrendsView(APIView):
    def get(self, request):
        city = request.query_params.get('city', 'tokyo').strip().lower()

        now = time.time()
        cached = _trends_cache.get(city)
        if cached and now - cached['ts'] < _TRENDS_CACHE_TTL:
            return Response(cached['data'])

        try:
            raw_trends = get_trending_keywords(city, top_n=10)
            trends = analyze_trends(city, raw_trends)
        except Exception:
            # pytrends 또는 분석 실패 → Gemini 단독 생성으로 fallback
            try:
                trends = generate_trends_fallback(city, top_n=10)
            except Exception as e:
                return Response(
                    {'error': f'트렌드 데이터 생성에 실패했습니다: {str(e)}'},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

        payload = {
            'city': city,
            'updated_at': datetime.now().isoformat(timespec='seconds'),
            'trends': trends,
        }
        _trends_cache[city] = {'data': payload, 'ts': now}
        return Response(payload)


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
