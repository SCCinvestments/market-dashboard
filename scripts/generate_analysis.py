import os
import json
import requests
from datetime import datetime, timezone, timedelta

def load_market_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def call_claude(prompt):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=60
        )
        data = response.json()
        return data["content"][0]["text"]
    except Exception as e:
        print(f"Claude API 에러: {e}")
        return None

def generate_analysis(market_data):
    crypto_summary = "\n".join([f"- {c['name']}: ${c['price']:,} ({c['change']:+.2f}%)" for c in market_data.get("crypto", [])])
    indices_summary = "\n".join([f"- {i['name']}: {i['price']:,} ({i['change']:+.2f}%)" for i in market_data.get("us_indices", [])])
    fear_greed = market_data.get("fear_greed", {})
    
    prompt = f"""전문 금융 애널리스트로서 시장 분석을 작성해주세요.

암호화폐:
{crypto_summary}
공포탐욕지수: {fear_greed.get('value', 'N/A')}

미국 지수:
{indices_summary}

HTML 형식으로 h3과 p 태그만 사용해서 작성:
1. 최근 글로벌 이슈
2. 전반적인 추세 분석  
3. 종합 견해

응답은 HTML 코드만 출력하세요."""

    return call_claude(prompt)

def generate_prediction(market_data):
    btc = next((c for c in market_data.get("crypto", []) if c["symbol"] == "BTC"), None)
    if not btc:
        return None
    fear_greed = market_data.get("fear_greed", {})
    
    prompt = f"""암호화폐 전문가로서 비트코인 분석을 작성해주세요.

비트코인: ${btc['price']:,} ({btc['change']:+.2f}%)
공포탐욕지수: {fear_greed.get('value', 'N/A')}

HTML 형식으로 h3과 p 태그만 사용:
1. 비트코인 단기 전망
2. 기술적 분석 근거
3. 투자자 대응방안

응답은 HTML 코드만 출력하세요."""

    return call_claude(prompt)

def get_economic_calendar_from_finnhub():
    """Finnhub에서 경제지표 일정 가져오기"""
    api_key = os.environ.get("FINNHUB_API_KEY")
    if not api_key:
        print("FINNHUB_API_KEY 없음")
        return []
    
    try:
        # 오늘부터 3일간 데이터
        kst = timezone(timedelta(hours=9))
        today = datetime.now(kst)
        from_date = today.strftime("%Y-%m-%d")
        to_date = (today + timedelta(days=3)).strftime("%Y-%m-%d")
        
        url = "https://finnhub.io/api/v1/calendar/economic"
        params = {
            "from": from_date,
            "to": to_date,
            "token": api_key
        }
        
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        events = data.get("economicCalendar", [])
        
        # 미국 + 중요도 높음(high, medium) 필터링
        us_events = []
        for event in events:
            if event.get("country") == "US" and event.get("impact") in ["high", "medium"]:
                us_events.append(event)
        
        return us_events
    except Exception as e:
        print(f"Finnhub API 에러: {e}")
        return []

def translate_economic_events(events):
    """Claude로 경제지표 한국어 번역"""
    if not events:
        return []
    
    # 이벤트 정보 정리
    events_text = ""
    for e in events[:15]:  # 최대 15개
        events_text += f"- {e.get('time', '')} | {e.get('event', '')} | forecast: {e.get('estimate', '-')} | previous: {e.get('prev', '-')} | impact: {e.get('impact', '')}\n"
    
    prompt = f"""다음 미국 경제지표 일정을 한국어로 번역해주세요.
시간은 UTC 기준이니 한국시간(KST, +9시간)으로 변환해주세요.

{events_text}

다음 JSON 형식으로만 응답하세요:
[
  {{"date": "2/5", "time": "00:00", "event": "ISM 제조업 PMI", "forecast": "48.3", "previous": "47.9", "importance": "high"}}
]

- event는 한국어로 번역
- time은 한국시간(KST)으로 변환
- importance가 "high"면 ⭐⭐⭐, "medium"이면 ⭐⭐

JSON만 출력하세요."""

    result = call_claude(prompt)
    
    if result:
        try:
            clean_result = result.strip()
            if clean_result.startswith("```"):
                clean_result = clean_result.split("\n", 1)[1]
            if clean_result.endswith("```"):
                clean_result = clean_result.rsplit("```", 1)[0]
            clean_result = clean_result.strip()
            
            return json.loads(clean_result)
        except:
            pass
    return []

def generate_economic_calendar():
    """경제지표 캘린더 생성 (Finnhub + Claude 번역)"""
    print("  Finnhub에서 경제지표 수집 중...")
    events = get_economic_calendar_from_finnhub()
    
    if events:
        print(f"  {len(events)}개 이벤트 발견, 번역 중...")
        translated = translate_economic_events(events)
        if translated:
            return translated
    
    # 실패 시 빈 배열 반환
    print("  경제지표 수집 실패")
    return []

def get_binance_futures_data():
    """Binance 선물 데이터 수집 (롱숏비율, 펀딩비, 미결제약정)"""
    futures_data = {
        "long_short_ratio": None,
        "funding_rate": None,
        "open_interest": None,
        "funding_rates": []
    }
    
    try:
        # 1. 글로벌 롱/숏 비율
        url = "https://fapi.binance.com/futures/data/globalLongShortAccountRatio"
        params = {"symbol": "BTCUSDT", "period": "1h", "limit": 1}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data:
                futures_data["long_short_ratio"] = {
                    "long": float(data[0]['longAccount']) * 100,
                    "short": float(data[0]['shortAccount']) * 100,
                    "ratio": float(data[0]['longShortRatio'])
                }
    except:
        pass
    
    try:
        # 2. 펀딩비
        url = "https://fapi.binance.com/fapi/v1/fundingRate"
        params = {"symbol": "BTCUSDT", "limit": 1}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data:
                futures_data["funding_rate"] = float(data[0]['fundingRate']) * 100
    except:
        pass
    
    try:
        # 3. 미결제약정
        url = "https://fapi.binance.com/fapi/v1/openInterest"
        params = {"symbol": "BTCUSDT"}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            futures_data["open_interest"] = float(data['openInterest'])
    except:
        pass
    
    try:
        # 4. 주요 코인 펀딩비
        coins = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT"]
        for coin in coins:
            url = "https://fapi.binance.com/fapi/v1/fundingRate"
            params = {"symbol": coin, "limit": 1}
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data:
                    futures_data["funding_rates"].append({
                        "symbol": coin.replace("USDT", ""),
                        "rate": float(data[0]['fundingRate']) * 100
                    })
    except:
        pass
    
    return futures_data

def main():
    print("start analysis")
    market_data = load_market_data()
    if not market_data:
        return
    
    print("  글로벌 분석 생성 중...")
    global_analysis = generate_analysis(market_data)
    
    print("  예측 분석 생성 중...")
    prediction_analysis = generate_prediction(market_data)
    
    print("  경제지표 일정 생성 중...")
    economic_calendar = generate_economic_calendar()
    
    print("  선물 데이터 수집 중...")
    futures_data = get_binance_futures_data()
    
    market_data["analysis"] = {
        "global_analysis": global_analysis or "<p>분석 생성 실패</p>",
        "prediction_analysis": prediction_analysis or "<p>분석 생성 실패</p>"
    }
    market_data["economic_calendar"] = economic_calendar
    market_data["futures_data"] = futures_data
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(market_data, f, ensure_ascii=False, indent=2)
    print("done")

if __name__ == "__main__":
    main()
