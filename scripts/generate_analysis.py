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

def search_economic_calendar():
    """Tavily로 오늘의 미국 경제지표 검색"""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        print("  TAVILY_API_KEY 없음")
        return None
    
    kst = timezone(timedelta(hours=9))
    today = datetime.now(kst)
    today_str = today.strftime("%Y년 %m월 %d일")
    
    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": f"US economic calendar today {today.strftime('%B %d %Y')} important events",
                "search_depth": "basic",
                "max_results": 5
            },
            timeout=30
        )
        data = response.json()
        
        results = data.get("results", [])
        if results:
            # 검색 결과 텍스트 합치기
            search_content = ""
            for r in results[:3]:
                search_content += r.get("content", "") + "\n"
            return search_content
        return None
    except Exception as e:
        print(f"  Tavily 검색 에러: {e}")
        return None

def generate_economic_calendar():
    """경제지표 캘린더 생성 (Tavily 검색 + Claude 정리)"""
    print("  Tavily로 경제지표 검색 중...")
    
    kst = timezone(timedelta(hours=9))
    today = datetime.now(kst)
    today_str = today.strftime("%Y년 %m월 %d일")
    weekday = ["월", "화", "수", "목", "금", "토", "일"][today.weekday()]
    
    # Tavily로 검색
    search_result = search_economic_calendar()
    
    search_info = ""
    if search_result:
        search_info = f"""
웹 검색 결과:
{search_result}
"""
        print("  검색 결과 있음, Claude로 정리 중...")
    else:
        print("  검색 결과 없음, Claude 지식으로 생성...")
    
    prompt = f"""오늘은 {today_str} ({weekday}요일)입니다.

{search_info}

오늘과 내일 예정된 **미국(USD) 주요 경제지표**를 정리해주세요.
중요도가 높은 것(⭐⭐⭐, ⭐⭐)만 선별해주세요.

주요 경제지표 예시:
- FOMC 금리결정, 기자회견
- 비농업 고용지수 (NFP) - 매월 첫째 금요일
- 신규 실업수당청구건수 - 매주 목요일 22:30 KST
- CPI (소비자물가지수)
- PPI (생산자물가지수)
- GDP
- PCE 물가지수
- ISM 제조업/서비스업 PMI
- 소매판매

다음 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
[
  {{"date": "1/30", "time": "22:30", "event": "신규 실업수당청구건수", "forecast": "220K", "previous": "223K", "importance": "high"}}
]

규칙:
- 시간은 한국시간(KST)
- importance: "high" 또는 "medium"
- 오늘이 목요일이면 신규 실업수당청구건수 반드시 포함
- 예정된 지표가 없으면 빈 배열 []

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
            
            calendar = json.loads(clean_result)
            print(f"  {len(calendar)}개 경제지표 생성 완료")
            return calendar
        except Exception as e:
            print(f"  JSON 파싱 실패: {e}")
            return []
    
    print("  경제지표 생성 실패")
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
