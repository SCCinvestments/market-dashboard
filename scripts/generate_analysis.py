import os
import json
import requests
import hashlib
import base64
from datetime import datetime, timezone, timedelta

def generate_daily_password():
    """매일 바뀌는 암호 생성"""
    kst = timezone(timedelta(hours=9))
    today = datetime.now(kst)
    
    # 비밀 시드 (GitHub Secrets에 저장 권장)
    secret_seed = os.environ.get("PASSWORD_SEED", "SCC2026SECRET")
    
    # 날짜 + 시드로 해시 생성
    date_str = today.strftime("%Y%m%d")
    raw = f"{secret_seed}_{date_str}"
    hash_obj = hashlib.sha256(raw.encode()).hexdigest()
    
    # 앞 6자리를 암호로 사용 (대문자 + 숫자)
    password = hash_obj[:6].upper()
    
    print(f"  오늘의 암호: {password}")
    return password

def encrypt_data(data, password):
    """XOR 암호화 (바이트 단위)"""
    json_str = json.dumps(data, ensure_ascii=False)
    json_bytes = json_str.encode('utf-8')
    
    # 바이트 단위 XOR
    key_bytes = (password * (len(json_bytes) // len(password) + 1))[:len(json_bytes)].encode('ascii')
    encrypted_bytes = bytes([b ^ k for b, k in zip(json_bytes, key_bytes)])
    
    # Base64 인코딩
    encoded = base64.b64encode(encrypted_bytes).decode('ascii')
    return encoded

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

def get_economic_calendar_from_einfomax():
    """einfomax API에서 경제지표 가져오기 (100% 정확)"""
    kst = timezone(timedelta(hours=9))
    today = datetime.now(kst)
    tomorrow = today + timedelta(days=1)
    
    calendar_data = []
    
    # 오늘 + 내일 데이터 가져오기 (새벽 포함)
    for date in [today.strftime("%Y-%m-%d"), tomorrow.strftime("%Y-%m-%d")]:
        try:
            response = requests.post(
                "https://kyobo.einfomax.co.kr/eco/master",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                json={
                    "date": date,
                    "country": ["1"],  # 미국만
                    "frequencyType": "today",
                    "impact": [1, 2, 3],  # 모든 중요도 가져온 후 필터링
                    "isAdmin": False,
                    "paramCountry": None
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                events = data.get("data", [])
                calendar_data.extend(events)
                print(f"  {date}: {len(events)}개 지표 수신")
        except Exception as e:
            print(f"  einfomax API 에러 ({date}): {e}")
    
    return calendar_data

def generate_economic_calendar():
    """경제지표 캘린더 생성 (einfomax API)"""
    print("  einfomax API에서 경제지표 수집 중...")
    
    kst = timezone(timedelta(hours=9))
    today = datetime.now(kst)
    tomorrow = today + timedelta(days=1)
    
    # einfomax에서 데이터 가져오기
    events = get_economic_calendar_from_einfomax()
    
    if not events:
        print("  경제지표 수집 실패")
        return []
    
    calendar = []
    
    for event in events:
        try:
            # UTC -> KST 변환
            timestamp = event.get("event_timestamp", "")
            if not timestamp:
                continue
            
            # 타임스탬프 파싱
            utc_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            kst_time = utc_time + timedelta(hours=9)
            
            # 오늘 날짜 ~ 내일 06:00 KST 범위
            today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow_6am = tomorrow.replace(hour=6, minute=0, second=0, microsecond=0)
            
            # 오늘 날짜이거나, 내일 06:00 이전이면 포함
            kst_date = kst_time.date()
            today_date = today.date()
            tomorrow_date = tomorrow.date()
            
            # 오늘 날짜 전체 포함
            if kst_date == today_date:
                pass  # 포함
            # 내일 06:00 이전까지 포함
            elif kst_date == tomorrow_date and kst_time.hour < 6:
                pass  # 포함
            else:
                continue  # 제외
            
            # 중요도 3(별 3개)만 포함
            impact = event.get("impact", 1)
            if impact != 3:
                continue
            
            importance = "high"
            
            # 한국어 이벤트명 (없으면 영어)
            event_name = event.get("event_kor") or event.get("event", "")
            
            calendar.append({
                "date": kst_time.strftime("%-m/%d"),
                "time": kst_time.strftime("%H:%M"),
                "event": event_name,
                "event_eng": event.get("event", ""),
                "forecast": event.get("eventForecast_value", "") or "-",
                "previous": event.get("eventPrevious_value", "") or "-",
                "importance": importance,
                "description": event.get("description_kor", "") or event.get("description", "") or ""
            })
        except Exception as e:
            continue
    
    # 시간순 정렬
    calendar.sort(key=lambda x: (x["date"], x["time"]))
    
    print(f"  {len(calendar)}개 경제지표 생성 완료")
    return calendar

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
    
    # 암호 생성
    print("  암호 생성 중...")
    password = generate_daily_password()
    
    # 데이터 암호화
    print("  데이터 암호화 중...")
    encrypted_data = encrypt_data(market_data, password)
    
    # 암호화된 데이터 저장
    output = {
        "encrypted": encrypted_data,
        "updated_at": market_data.get("updated_at", "")
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)
    print("done")

if __name__ == "__main__":
    main()
