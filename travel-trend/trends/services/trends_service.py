import time
from pytrends.request import TrendReq

# city → 2-letter ISO geo code (realtime_trending_searches 용)
CITY_MAP = {
    'tokyo':     'JP',
    'osaka':     'JP',
    'seoul':     'KR',
    'busan':     'KR',
    'paris':     'FR',
    'london':    'GB',
    'newyork':   'US',
    'bangkok':   'TH',
    'singapore': 'SG',
    'hongkong':  'HK',
    'taipei':    'TW',
    'bali':      'ID',
}

_cache: dict = {}
_CACHE_TTL = 600  # 10분


def get_trending_keywords(city: str, top_n: int = 10) -> list[dict]:
    city_key = city.lower().replace(' ', '')
    cache_key = f"{city_key}_{top_n}"
    now = time.time()

    if cache_key in _cache and now - _cache[cache_key]['ts'] < _CACHE_TTL:
        return _cache[cache_key]['data']

    geo = CITY_MAP.get(city_key, 'JP')
    pytrends = TrendReq(hl='en-US', tz=540, timeout=(10, 25))

    df = pytrends.realtime_trending_searches(pn=geo)
    keywords = df['title'].tolist()[:top_n]

    # interest_over_time 로 life_cycle 힌트 (실패해도 계속 진행)
    interest_map = _fetch_interest_safe(pytrends, keywords, geo)

    results = []
    for i, keyword in enumerate(keywords):
        values = interest_map.get(keyword, [])
        rising_pct = _calc_rising_pct(values) if values else max(50, 300 - i * 25)
        life_cycle = _determine_life_cycle(values) if values else 'Rising'
        results.append({
            'rank': i + 1,
            'keyword': keyword,
            'rising_percentage': max(0, rising_pct),
            'life_cycle': life_cycle,
        })

    _cache[cache_key] = {'data': results, 'ts': now}
    return results


def _fetch_interest_safe(pytrends: TrendReq, keywords: list[str], geo: str) -> dict[str, list]:
    interest_map: dict[str, list] = {}
    for i in range(0, len(keywords), 5):
        batch = keywords[i:i + 5]
        try:
            pytrends.build_payload(batch, timeframe='today 1-m', geo=geo)
            df = pytrends.interest_over_time()
            for kw in batch:
                if kw in df.columns:
                    interest_map[kw] = df[kw].tolist()
            time.sleep(1)
        except Exception:
            pass  # 실패해도 무시 — Gemini가 life_cycle 최종 판단
    return interest_map


def _calc_rising_pct(values: list) -> int:
    if len(values) < 2:
        return 0
    mid = len(values) // 2
    first_avg = sum(values[:mid]) / mid
    second_avg = sum(values[mid:]) / (len(values) - mid)
    if first_avg == 0:
        return 500 if second_avg > 0 else 0
    return int((second_avg - first_avg) / first_avg * 100)


def _determine_life_cycle(values: list) -> str:
    if len(values) < 4:
        return 'rising'
    week = max(1, len(values) // 4)
    recent = sum(values[-week:]) / week
    earlier = sum(values[:week]) / week
    if earlier == 0:
        return 'Rookie'
    ratio = recent / earlier
    if ratio >= 3.0:
        return 'Rookie'
    if ratio >= 1.5:
        return 'Rising'
    if ratio >= 0.9:
        return 'Hot'
    return 'Steady'
