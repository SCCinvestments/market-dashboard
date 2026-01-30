"""
시장 데이터 수집 스크립트
"""

import requests
import json
from datetime import datetime, timezone, timedelta

def get_crypto_data():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,ripple,solana,binancecoin,dogecoin",
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        crypto_list = []
        symbol_map = {
            "bitcoin": ("BTC", "비트코인"),
            "ethereum": ("ETH", "이더리움"),
            "ripple": ("XRP", "리플"),
            "solana": ("SOL", "솔라나"),
            "binancecoin": ("BNB", "BNB"),
            "dogecoin": ("DOGE", "도지코인")
        }
        
        for coin_id, (symbol, name) in symbol_map.items():
            if coin_id in data:
                crypto_list.append({
                    "symbol": symbol,
                    "name": name,
                    "price": round(data[coin_id]["usd"], 2),
                    "change": round(data[coin_id].get("usd_24h_change", 0), 2)
                })
        
        return crypto_list
    except Exception as e:
        print(f"암호화폐 데이터 수집 실패: {e}")
        return []

def get_fear_greed_index():
    try:
        url = "https://api.alternative.me/fng/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("data"):
            return {
                "value": int(data["data"][0]["value"]),
                "label": data["data"][0]["value_classification"]
            }
        return {"value": 50, "label": "Neutral"}
    except Exception as e:
        print(f"공포탐욕지수 수집 실패: {e}")
        return {"value": 50, "label": "Neutral"}

def get_stock_indices():
    indices = []
    
    try:
        symbols = {
            "^GSPC": ("S&P 500", "sp500"),
            "^DJI": ("다우존스", "dow"),
            "^IXIC": ("나스닥", "nasdaq"),
            "^VIX": ("VIX", "vix"),
            "^NDX": ("나스닥100", "nasdaq100"),
            "GC=F": ("골드", "gold"),
            "KRW=X": ("원/달러", "usdkrw")
        }
        
        for symbol, (name, key) in symbols.items():
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(url, headers=headers, timeout=10)
                data = response.json()
                
                if "chart" in data and data["chart"]["result"]:
                    result = data["chart"]["result"][0]
                    meta = result["meta"]
                    price = meta.get("regularMarketPrice", 0)
                    prev_close = meta.get("previousClose", price)
                    change = ((price - prev_close) / prev_close * 100) if prev_close else 0
                    
                    indices.append({
                        "key": key,
                        "name": name,
                        "price": round(price, 2),
                        "change": round(change, 2)
                    })
            except Exception as e:
                print(f"{name} 데이터 수집 실패: {e}")
                
    except Exception as e:
        print(f"주식 지수 데이터 수집 실패: {e}")
    
    return indices

def get_korean_indices():
    indices = []
    
    try:
        symbols = {
            "^KS11": ("코스피", "kospi"),
            "^KQ11": ("코스닥", "kosdaq")
        }
        
        for symbol, (name, key) in symbols.items():
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(url, headers=headers, timeout=10)
                data = response.json()
                
                if "chart" in data and data["chart"]["result"]:
                    result = data["chart"]["result"][0]
                    meta = result["meta"]
                    price = meta.get("regularMarketPrice", 0)
                    prev_close = meta.get("previousClose", price)
                    change = ((price - prev_close) / prev_close * 100) if prev_close else 0
                    
                    indices.append({
                        "key": key,
                        "name": name,
                        "price": round(price, 2),
                        "change": round(change, 2)
                    })
            except Exception as e:
                print(f"{name} 데이터 수집 실패: {e}")
                
    except Exception as e:
        print(f"한국 지수 데이터 수집 실패: {e}")
    
    return indices

def get_btc_history():
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        params = {
            "vs_currency": "usd",
            "days": "30",
            "interval": "daily"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        prices = []
        labels = []
        
        for item in data.get("prices", [])[-11:]:
            timestamp = item[0] / 1000
            date = datetime.fromtimestamp(timestamp)
            labels.append(date.strftime("%m/%d"))
            prices.append(round(item[1], 0))
        
        return {"labels": labels, "prices": prices}
    except Exception as e:
        print(f"BTC 히스토리 수집 실패: {e}")
        return {"labels": [], "prices": []}

def main():
    print("시장 데이터 수집 시작...")
    
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    
    crypto_data = get_crypto_data()
    print(f"  암호화폐: {len(crypto_data)}개")
    
    fear_greed = get_fear_greed_index()
    print(f"  공포탐욕지수: {fear_greed['value']}")
    
    stock_indices = get_stock_indices()
    print(f"  미국 지수: {len(stock_indices)}개")
    
    korean_indices = get_korean_indices()
    print(f"  한국 지수: {len(korean_indices)}개")
    
    btc_history = get_btc_history()
    print(f"  BTC 히스토리: {len(btc_history['prices'])}일")
    
    market_data = {
        "updated_at": now.strftime("%Y년 %m월 %d일 %H:%M KST"),
        "updated_timestamp": now.isoformat(),
        "crypto": crypto_data,
        "fear_greed": fear_greed,
        "us_indices": stock_indices,
        "kr_indices": korean_indices,
        "btc_history": btc_history
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(market_data, f, ensure_ascii=False, indent=2)
    
    print("데이터 저장 완료: data.json")
    return market_data

if __name__ == "__main__":
    main()
