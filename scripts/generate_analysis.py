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

def call_claude(prompt, use_web_search=False):
    """Claude API 호출 (웹 검색 옵션)"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("    API 키 없음")
        return None
    
    try:
        headers = {
            "x-api-key": api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        body = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 4000,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        # 웹 검색 활성화
        if use_web_search:
            headers["anthropic-beta"] = "web-search-2025-03-05"
            body["tools"] = [{
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 5
            }]
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=body,
            timeout=180
        )
        
        data = response.json()
        
        # 에러 체크
        if "error" in data:
            print(f"    API 에러: {data['error']}")
            return None
        
        # 응답에서 텍스트 추출
        result_text = ""
        content = data.get("content", [])
        
        for block in content:
            block_type = block.get("type", "")
            if block_type == "text":
                result_text += block.get("text", "")
        
        if not result_text:
            print(f"    응답 텍스트 없음. 전체 응답: {json.dumps(data, ensure_ascii=False)[:500]}")
            return None
            
        print(f"    분석 생성 완료 ({len(result_text)}자)")
        return result_text
        
    except Exception as e:
        print(f"    Claude API 에러: {e}")
        return None

def generate_one_liner(market_data):
    """한줄 코멘트 생성 (웹 검색으로 최신 이슈 반영)"""
    crypto = market_data.get("crypto", [])
    indices = market_data.get("us_indices", [])
    fear_greed = market_data.get("fear_greed", {})
    
    # 현재 날짜
    kst = timezone(timedelta(hours=9))
    today = datetime.now(kst).strftime("%m월 %d일")
    
    btc = next((c for c in crypto if c["symbol"] == "BTC"), {})
    dxy = next((i for i in indices if i.get("key") == "dxy"), {})
    
    prompt = f"""당신은 월가의 수석 전략가입니다. 오늘({today}) 시장을 한 문장으로 요약해주세요.

현재 시장 상황:
- 비트코인: ${btc.get('price', 0):,} ({btc.get('change', 0):+.2f}%)
- 공포탐욕지수: {fear_greed.get('value', 50)}
- 달러인덱스: {dxy.get('price', 0)} ({dxy.get('change', 0):+.2f}%)
- 주요 지수: {', '.join([f"{i['name']} {i['change']:+.2f}%" for i in indices[:3]])}

최신 금융 뉴스를 검색해서 오늘의 핵심 이슈를 반영해주세요.

규칙:
- 반드시 "{today} |" 로 시작
- 한 문장 (50자 이내)
- 핵심 메시지만
- 이모지 하나 포함
- 전문가 톤

예시: "01월 31일 | 🔥 연준 피벗 기대감에 위험자산 전반 강세"

한 문장만 출력하세요."""

    return call_claude(prompt, use_web_search=True)

def generate_us_market_analysis(market_data):
    """미국 증시 분석 (웹 검색으로 최신 뉴스 반영)"""
    indices = market_data.get("us_indices", [])
    
    # 주요 지수 추출
    sp500 = next((i for i in indices if i.get("key") == "sp500"), {})
    nasdaq = next((i for i in indices if i.get("key") == "nasdaq"), {})
    nasdaq100 = next((i for i in indices if i.get("key") == "nasdaq100"), {})
    dow = next((i for i in indices if i.get("key") == "dow"), {})
    vix = next((i for i in indices if i.get("key") == "vix"), {})
    us10y = next((i for i in indices if i.get("key") == "us10y"), {})
    dxy = next((i for i in indices if i.get("key") == "dxy"), {})
    
    prompt = f"""당신은 월가 10년차 주식 애널리스트입니다. 미국 증시를 전문적으로 분석해주세요.

[실시간 시장 데이터 - 09:30 KST 기준]
- S&P 500: {sp500.get('price', 'N/A')} ({sp500.get('change', 0):+.2f}%)
- 나스닥: {nasdaq.get('price', 'N/A')} ({nasdaq.get('change', 0):+.2f}%)
- 나스닥100: {nasdaq100.get('price', 'N/A')} ({nasdaq100.get('change', 0):+.2f}%)
- 다우존스: {dow.get('price', 'N/A')} ({dow.get('change', 0):+.2f}%)
- VIX: {vix.get('price', 'N/A')} ({vix.get('change', 0):+.2f}%)
- 미국 10년물 금리: {us10y.get('price', 'N/A')}% ({us10y.get('change', 0):+.2f}%)
- 달러인덱스: {dxy.get('price', 'N/A')} ({dxy.get('change', 0):+.2f}%)

최신 미국 증시 뉴스를 웹에서 검색해서 분석에 반영하세요.
특히 Fed 정책, 실적 발표, 경제지표 관련 뉴스를 찾아주세요.

다음 형식으로 HTML 작성 (h4, p 태그만 사용):

<h4>📊 나스닥 분석</h4>
<p>위 실제 데이터 기반으로 나스닥 지수의 기술적 분석, 주요 지지/저항선, 모멘텀 분석 작성. 반드시 위 수치를 인용하세요.</p>

<h4>📈 섹터별 동향</h4>
<p>최신 뉴스 검색 결과 기반으로 기술주, 반도체, 헬스케어, 에너지 등 주요 섹터의 동향을 구체적인 종목과 수치로 분석</p>

<h4>⚡ 주요 이슈</h4>
<p>웹 검색으로 찾은 오늘의 핵심 이슈 3가지를 심층 분석</p>

규칙:
- 위에 제공된 실제 데이터를 반드시 사용
- 웹 검색으로 찾은 최신 뉴스 반영
- 구체적인 수치 필수
- HTML 코드만 출력"""

    return call_claude(prompt, use_web_search=True)

def generate_crypto_analysis(market_data):
    """암호화폐 분석 (웹 검색으로 최신 뉴스 반영)"""
    crypto = market_data.get("crypto", [])
    fear_greed = market_data.get("fear_greed", {})
    futures = market_data.get("futures_data", {})
    
    # 주요 코인 추출
    btc = next((c for c in crypto if c["symbol"] == "BTC"), {})
    eth = next((c for c in crypto if c["symbol"] == "ETH"), {})
    sol = next((c for c in crypto if c["symbol"] == "SOL"), {})
    xrp = next((c for c in crypto if c["symbol"] == "XRP"), {})
    
    ls_ratio = futures.get("long_short_ratio") or {}
    funding = futures.get("funding_rate") or 0
    oi = futures.get("open_interest") or 0
    
    prompt = f"""당신은 크립토 전문 애널리스트입니다. 암호화폐 시장을 심층 분석해주세요.

[실시간 시장 데이터 - 09:30 KST 기준]
- 비트코인(BTC): ${btc.get('price', 0):,} ({btc.get('change', 0):+.2f}%)
- 이더리움(ETH): ${eth.get('price', 0):,} ({eth.get('change', 0):+.2f}%)
- 솔라나(SOL): ${sol.get('price', 0):,} ({sol.get('change', 0):+.2f}%)
- 리플(XRP): ${xrp.get('price', 0):,} ({xrp.get('change', 0):+.2f}%)

[시장 지표]
- 공포탐욕지수: {fear_greed.get('value', 50)}
- BTC 롱/숏 비율: {ls_ratio.get('ratio', 'N/A') if ls_ratio else 'N/A'}
- BTC 펀딩비: {funding:.4f}%
- BTC 미결제약정: {oi:,.0f} BTC

최신 암호화폐 뉴스를 웹에서 검색해서 분석에 반영하세요.
ETF 자금 흐름, 기관 투자, 규제 뉴스 등을 찾아주세요.

다음 형식으로 HTML 작성 (h4, p 태그만 사용):

<h4>🔶 비트코인 심층 분석</h4>
<p>위 실제 데이터 기반으로 BTC 기술적 분석, 주요 지지/저항선, ETF 자금 흐름, 기관 동향 분석</p>

<h4>🌈 알트코인 동향</h4>
<p>위 실제 데이터 기반으로 ETH, SOL, XRP 등 주요 알트코인 분석, BTC 대비 상대 강도</p>

<h4>📉 선물 시장 분석</h4>
<p>위 롱숏비율, 펀딩비, 미결제약정 데이터를 해석하고 향후 가격 방향성 예측</p>

규칙:
- 위에 제공된 실제 데이터를 반드시 사용
- 웹 검색으로 찾은 최신 뉴스 반영
- 구체적인 수치 필수
- HTML 코드만 출력"""

    return call_claude(prompt, use_web_search=True)

def generate_commodities_analysis(market_data):
    """원자재 분석 (웹 검색으로 최신 뉴스 반영)"""
    indices = market_data.get("us_indices", [])
    
    gold = next((i for i in indices if i.get("key") == "gold"), {})
    silver = next((i for i in indices if i.get("key") == "silver"), {})
    wti = next((i for i in indices if i.get("key") == "wti"), {})
    dxy = next((i for i in indices if i.get("key") == "dxy"), {})
    us10y = next((i for i in indices if i.get("key") == "us10y"), {})
    
    prompt = f"""당신은 원자재 전문 애널리스트입니다. 원자재 시장을 분석해주세요.

[실시간 시장 데이터 - 09:30 KST 기준]
- 금(Gold): ${gold.get('price', 0):,} ({gold.get('change', 0):+.2f}%)
- 은(Silver): ${silver.get('price', 0):,} ({silver.get('change', 0):+.2f}%)
- WTI 원유: ${wti.get('price', 0):,} ({wti.get('change', 0):+.2f}%)
- 달러인덱스: {dxy.get('price', 0)} ({dxy.get('change', 0):+.2f}%)
- 미국 10년물 금리: {us10y.get('price', 0)}% ({us10y.get('change', 0):+.2f}%)

최신 원자재 뉴스를 웹에서 검색해서 분석에 반영하세요.
지정학적 리스크, 중앙은행 금 매수, OPEC 동향 등을 찾아주세요.

다음 형식으로 HTML 작성 (h4, p 태그만 사용):

<h4>🥇 금(Gold) 심층 분석</h4>
<p>위 실제 데이터 기반으로 금 가격 기술적 분석, 달러인덱스/실질금리와의 상관관계, 중앙은행 매수 동향</p>

<h4>🥈 은 및 기타 원자재</h4>
<p>위 실제 데이터 기반으로 은, WTI 원유 분석, 경기 사이클 관점 해석</p>

<h4>⚡ 주요 이슈</h4>
<p>웹 검색으로 찾은 지정학적 리스크, 수급 이슈, 정책 변화 분석</p>

규칙:
- 위에 제공된 실제 데이터를 반드시 사용
- 웹 검색으로 찾은 최신 뉴스 반영
- 구체적인 수치 필수
- HTML 코드만 출력"""

    return call_claude(prompt, use_web_search=True)

def generate_korea_market_analysis(market_data):
    """국내 증시 분석 (웹 검색으로 최신 뉴스 반영)"""
    kr_indices = market_data.get("kr_indices", [])
    us_indices = market_data.get("us_indices", [])
    
    kospi = next((i for i in kr_indices if i.get("key") == "kospi"), {})
    kosdaq = next((i for i in kr_indices if i.get("key") == "kosdaq"), {})
    usdkrw = next((i for i in us_indices if i.get("key") == "usdkrw"), {})
    
    prompt = f"""당신은 국내 증시 전문 애널리스트입니다. 한국 주식시장을 분석해주세요.

[실시간 시장 데이터 - 09:30 KST 기준]
- 코스피: {kospi.get('price', 0):,} ({kospi.get('change', 0):+.2f}%)
- 코스닥: {kosdaq.get('price', 0):,} ({kosdaq.get('change', 0):+.2f}%)
- 원/달러 환율: {usdkrw.get('price', 0):,}원 ({usdkrw.get('change', 0):+.2f}%)

최신 한국 증시 뉴스를 웹에서 검색해서 분석에 반영하세요.
외국인 수급, 삼성전자, SK하이닉스 등 주요 종목 뉴스를 찾아주세요.

다음 형식으로 HTML 작성 (h4, p 태그만 사용):

<h4>🇰🇷 코스피/코스닥 분석</h4>
<p>위 실제 데이터 기반으로 코스피, 코스닥 기술적 분석, 주요 지지/저항선, 원/달러 영향</p>

<h4>💰 외국인/기관 수급</h4>
<p>웹 검색으로 찾은 외국인, 기관 매매 동향과 수급 분석</p>

<h4>📊 업종별 분석</h4>
<p>반도체, 2차전지, 바이오, 금융 등 주요 업종의 동향과 주도주 분석</p>

규칙:
- 위에 제공된 실제 데이터를 반드시 사용
- 웹 검색으로 찾은 최신 뉴스 반영
- 구체적인 수치 필수
- HTML 코드만 출력"""

    return call_claude(prompt, use_web_search=True)

def generate_investment_strategy(market_data):
    """투자 전략 (웹 검색으로 최신 뉴스 기반 전략)"""
    crypto = market_data.get("crypto", [])
    indices = market_data.get("us_indices", [])
    kr_indices = market_data.get("kr_indices", [])
    fear_greed = market_data.get("fear_greed", {})
    
    btc = next((c for c in crypto if c["symbol"] == "BTC"), {})
    nasdaq = next((i for i in indices if i.get("key") == "nasdaq100"), {})
    gold = next((i for i in indices if i.get("key") == "gold"), {})
    vix = next((i for i in indices if i.get("key") == "vix"), {})
    dxy = next((i for i in indices if i.get("key") == "dxy"), {})
    kospi = next((i for i in kr_indices if i.get("key") == "kospi"), {})
    
    prompt = f"""당신은 자산운용사의 수석 전략가입니다. 종합 투자 전략을 제시해주세요.

[실시간 시장 데이터 - 09:30 KST 기준]
- 비트코인: ${btc.get('price', 0):,} ({btc.get('change', 0):+.2f}%)
- 나스닥100: {nasdaq.get('price', 0):,} ({nasdaq.get('change', 0):+.2f}%)
- 골드: ${gold.get('price', 0):,} ({gold.get('change', 0):+.2f}%)
- VIX: {vix.get('price', 0)} ({vix.get('change', 0):+.2f}%)
- 달러인덱스: {dxy.get('price', 0)} ({dxy.get('change', 0):+.2f}%)
- 코스피: {kospi.get('price', 0):,} ({kospi.get('change', 0):+.2f}%)
- 공포탐욕지수: {fear_greed.get('value', 50)}

최신 글로벌 경제 뉴스와 지정학적 리스크를 웹에서 검색해서 전략에 반영하세요.
Fed 정책, 중국 경제, 지정학적 리스크, 실적 시즌 등을 검토해주세요.

다음 형식으로 HTML 작성 (h4, p 태그만 사용):

<h4>📅 단기 시나리오 (1-2주)</h4>
<p>위 실제 데이터와 웹 검색 결과 기반으로 향후 1-2주 시장 전망, 주요 변수, 예상 시나리오</p>

<h4>📆 중기 시나리오 (1-3개월)</h4>
<p>중기적 관점에서의 시장 방향성과 주요 이벤트, 포지셔닝 전략</p>

<h4>⚠️ 리스크 요인</h4>
<p>웹 검색으로 찾은 현재 시장의 주요 리스크 요인 3가지와 대응 방안</p>

<h4>💡 추천 포지션</h4>
<p>위 실제 가격 데이터 기반으로 자산별 구체적인 진입가, 목표가, 손절가 제시</p>

규칙:
- 위에 제공된 실제 데이터를 반드시 사용
- 웹 검색으로 찾은 최신 뉴스/리스크 반영
- 구체적인 가격대와 비중 제시
- HTML 코드만 출력"""

    return call_claude(prompt, use_web_search=True)

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
    import time
    
    print("start analysis")
    market_data = load_market_data()
    if not market_data:
        return
    
    print("  경제지표 일정 생성 중...")
    economic_calendar = generate_economic_calendar()
    market_data["economic_calendar"] = economic_calendar
    
    print("  선물 데이터 수집 중...")
    futures_data = get_binance_futures_data()
    market_data["futures_data"] = futures_data
    
    # V2 분석 생성 (Rate Limit 방지를 위해 60초 딜레이)
    print("  한줄 코멘트 생성 중...")
    one_liner = generate_one_liner(market_data)
    time.sleep(60)  # 1분 대기
    
    print("  미국 증시 분석 중...")
    us_market = generate_us_market_analysis(market_data)
    time.sleep(60)  # 1분 대기
    
    print("  암호화폐 분석 중...")
    crypto_analysis = generate_crypto_analysis(market_data)
    time.sleep(60)  # 1분 대기
    
    print("  원자재 분석 중...")
    commodities = generate_commodities_analysis(market_data)
    time.sleep(60)  # 1분 대기
    
    print("  국내 증시 분석 중...")
    korea_market = generate_korea_market_analysis(market_data)
    time.sleep(60)  # 1분 대기
    
    print("  투자 전략 생성 중...")
    strategy = generate_investment_strategy(market_data)
    
    market_data["analysis"] = {
        "one_liner": one_liner or "📊 시장 분석 준비 중입니다.",
        "us_market": us_market or "<p>분석 생성 중...</p>",
        "crypto": crypto_analysis or "<p>분석 생성 중...</p>",
        "commodities": commodities or "<p>분석 생성 중...</p>",
        "korea_market": korea_market or "<p>분석 생성 중...</p>",
        "strategy": strategy or "<p>분석 생성 중...</p>"
    }
    
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
