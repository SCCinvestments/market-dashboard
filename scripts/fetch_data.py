import requests
import json
from datetime import datetime, timezone, timedelta

def get_crypto_data():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "bitcoin,ethereum,ripple,solana,binancecoin,dogecoin", "vs_currencies": "usd", "include_24hr_change": "true"}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        crypto_list = []
        symbol_map = {"bitcoin": ("BTC", "비트코인"), "ethereum": ("ETH", "이더리움"), "ripple": ("XRP", "리플"), "solana": ("SOL", "솔라나"), "binancecoin": ("BNB", "BNB"), "dogecoin": ("DOGE", "도지코인")}
        for coin_id, (symbol, name) in symbol_map.items():
            if coin_id in data:
                crypto_list.append({"symbol": symbol, "name": name, "price": round(data[coin_id]["usd"], 2), "change": round(data[coin_id].get("usd_24h_change", 0), 2)})
        return crypto_list
    except Exception as e:
        print(f"error: {e}")
        return []

def get_fear_greed_index():
    try:
        url = "https://api.alternative.me/fng/"
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("data"):
            return {"value": int(data["data"][0]["value"]), "label": data["data"][0]["value_classification"]}
        return {"value": 50, "label": "Neutral"}
    except:
        return {"value": 50, "label": "Neutral"}

def get_stock_indices():
    indices = []
    symbols = {"^GSPC": ("S&P 500", "sp500"), "^DJI": ("다우존스", "dow"), "^IXIC": ("나스닥", "nasdaq"), "^VIX": ("VIX", "vix")}
    for symbol, (name, key) in symbols.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            if "chart" in data and data["chart"]["result"]:
                meta = data["chart"]["result"][0]["meta"]
                price = meta.get("regularMarketPrice", 0)
                prev_close = meta.get("previousClose", price)
                change = ((price - prev_close) / prev_close * 100) if prev_close else 0
                indices.append({"key": key, "name": name, "price": round(price, 2), "change": round(change, 2)})
        except:
            pass
    return indices

def get_korean_indices():
    indices = []
    symbols = {"^KS11": ("코스피", "kospi"), "^KQ11": ("코스닥", "kosdaq")}
    for symbol, (name, key) in symbols.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            if "chart" in data and data["chart"]["result"]:
                meta = data["chart"]["result"][0]["meta"]
                price = meta.get("regularMarketPrice", 0)
                prev_close = meta.get("previousClose", price)
                change = ((price - prev_close) / prev_close * 100) if prev_close else 0
                indices.append({"key": key, "name": name, "price": round(price, 2), "change": round(change, 2)})
        except:
            pass
    return indices

def get_btc_history():
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        params = {"vs_currency": "usd", "days": "30", "interval": "daily"}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        prices, labels = [], []
        for item in data.get("prices", [])[-11:]:
            timestamp = item[0] / 1000
            date = datetime.fromtimestamp(timestamp)
            labels.append(date.strftime("%m/%d"))
            prices.append(round(item[1], 0))
        return {"labels": labels, "prices": prices}
    except:
        return {"labels": [], "prices": []}

def main():
    print("start")
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    market_data = {
        "updated_at": now.strftime("%Y년 %m월 %d일 %H:%M KST"),
        "crypto": get_crypto_data(),
        "fear_greed": get_fear_greed_index(),
        "us_indices": get_stock_indices(),
        "kr_indices": get_korean_indices(),
        "btc_history": get_btc_history()
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(market_data, f, ensure_ascii=False, indent=2)
    print("done")

if __name__ == "__main__":
    main()
