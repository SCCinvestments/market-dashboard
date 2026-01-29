import os
import json
import requests

def load_market_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def generate_analysis(market_data):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    
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
3. 종합 견해"""

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
    except:
        return None

def generate_prediction(market_data):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    
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
3. 투자자 대응방안"""

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
                "max_tokens": 1500,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=60
        )
        data = response.json()
        return data["content"][0]["text"]
    except:
        return None

def main():
    print("start analysis")
    market_data = load_market_data()
    if not market_data:
        return
    market_data["analysis"] = {
        "global_analysis": generate_analysis(market_data) or "<p>분석 생성 실패</p>",
        "prediction_analysis": generate_prediction(market_data) or "<p>분석 생성 실패</p>"
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(market_data, f, ensure_ascii=False, indent=2)
    print("done")

if __name__ == "__main__":
    main()
```

4. **"Commit changes"** 클릭

---

그리고 **requirements.txt**도 수정:
```
requests==2.31.0
