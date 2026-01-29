import json

def main():
    print("build start")
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    updated_at = data.get("updated_at", "")
    crypto = data.get("crypto", [])
    fear_greed = data.get("fear_greed", {"value": 50})
    us_indices = data.get("us_indices", [])
    kr_indices = data.get("kr_indices", [])
    analysis = data.get("analysis", {})
    
    fg_value = fear_greed.get("value", 50)
    fg_label = "극도의 공포" if fg_value <= 25 else "공포" if fg_value <= 45 else "중립" if fg_value <= 55 else "탐욕" if fg_value <= 75 else "극도의 탐욕"
    fg_class = "fear" if fg_value <= 45 else "neutral" if fg_value <= 55 else "greed"
    
    us_rows = ""
    for idx in us_indices:
        change_class = "positive" if idx["change"] >= 0 else "negative"
        sign = "+" if idx["change"] >= 0 else ""
        us_rows += f'<tr><td>{idx["name"]}</td><td>{idx["price"]:,}</td><td class="{change_class}">{sign}{idx["change"]:.2f}%</td></tr>'
    
    crypto_cards = ""
    for coin in crypto:
        card_class = "up" if coin["change"] >= 0 else "down"
        change_class = "positive" if coin["change"] >= 0 else "negative"
        sign = "+" if coin["change"] >= 0 else ""
        crypto_cards += f'<div class="crypto-card {card_class}"><div class="crypto-symbol">{coin["symbol"]}</div><div class="crypto-price">${coin["price"]:,}</div><div class="crypto-change {change_class}">{sign}{coin["change"]:.2f}%</div></div>'
    
    kr_rows = ""
    for idx in kr_indices:
        change_class = "positive" if idx["change"] >= 0 else "negative"
        sign = "+" if idx["change"] >= 0 else ""
        kr_rows += f'<tr><td>{idx["name"]}</td><td>{idx["price"]:,}</td><td class="{change_class}">{sign}{idx["change"]:.2f}%</td></tr>'
    
    global_analysis = analysis.get("global_analysis", "")
    prediction_analysis = analysis.get("prediction_analysis", "")
    
    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Market Dashboard</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:sans-serif;background:#0a0a0f;color:#fff;line-height:1.6}}
.header{{background:#12121a;padding:1rem 2rem;border-bottom:1px solid #2a2a3a}}
.header-content{{max-width:1200px;margin:0 auto;display:flex;justify-content:space-between;align-items:center}}
.logo{{font-size:1.5rem;font-weight:bold;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.update-time{{color:#8a8a9a;font-size:0.85rem}}
.container{{max-width:1200px;margin:0 auto;padding:2rem}}
.section{{background:#1a1a25;border:1px solid #2a2a3a;border-radius:12px;margin-bottom:1.5rem;padding:1.5rem}}
.section-title{{font-size:1.1rem;font-weight:bold;margin-bottom:1rem;padding-left:10px;border-left:3px solid #ff4757}}
.table{{width:100%;border-collapse:collapse}}
.table th,.table td{{padding:0.75rem;text-align:left;border-bottom:1px solid #2a2a3a}}
.table th{{color:#8a8a9a;font-weight:500}}
.positive{{color:#2ed573}}
.negative{{color:#ff4757}}
.crypto-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1rem}}
.crypto-card{{background:#12121a;border-radius:10px;padding:1rem;text-align:center}}
.crypto-card.up{{border:1px solid rgba(46,213,115,0.3)}}
.crypto-card.down{{border:1px solid rgba(255,71,87,0.3)}}
.crypto-symbol{{font-weight:bold;font-size:1.1rem}}
.crypto-price{{color:#8a8a9a;font-size:0.85rem;margin:0.25rem 0}}
.crypto-change{{font-weight:bold}}
.fear-greed{{display:flex;align-items:center;gap:2rem;background:#12121a;padding:1.5rem;border-radius:10px;margin-top:1rem}}
.fg-value{{font-size:2.5rem;font-weight:bold}}
.fg-label{{display:inline-block;padding:0.25rem 0.75rem;border-radius:20px;font-size:0.85rem;margin-top:0.5rem}}
.fg-label.fear{{background:rgba(255,71,87,0.2);color:#ff4757}}
.fg-label.neutral{{background:rgba(138,138,154,0.2);color:#8a8a9a}}
.fg-label.greed{{background:rgba(255,165,2,0.2);color:#ffa502}}
.analysis h3{{margin:1rem 0 0.5rem;color:#fff}}
.analysis p{{color:#8a8a9a;margin-bottom:0.75rem}}
.footer{{text-align:center;padding:2rem;color:#8a8a9a;font-size:0.8rem}}
</style>
</head>
<body>
<header class="header"><div class="header-content"><div class="logo">AI Market Dashboard</div><div class="update-time">{updated_at}</div></div></header>
<main class="container">
<section class="section"><h2 class="section-title">US Market</h2>
<table class="table"><thead><tr><th>Index</th><th>Price</th><th>Change</th></tr></thead><tbody>{us_rows}</tbody></table></section>
<section class="section"><h2 class="section-title">Market Analysis</h2><div class="analysis">{global_analysis}</div></section>
<section class="section"><h2 class="section-title">Prediction</h2><div class="analysis">{prediction_analysis}</div></section>
<section class="section"><h2 class="section-title">Crypto</h2><div class="crypto-grid">{crypto_cards}</div>
<div class="fear-greed"><div><div class="fg-value">{fg_value}</div><div class="fg-label {fg_class}">{fg_label}</div></div><div><h4>Fear & Greed</h4><p style="color:#8a8a9a">Market Sentiment</p></div></div></section>
<section class="section"><h2 class="section-title">Korea Market</h2>
<table class="table"><thead><tr><th>Index</th><th>Price</th><th>Change</th></tr></thead><tbody>{kr_rows}</tbody></table></section>
</main>
<footer class="footer"><p>Powered by Claude AI</p></footer>
</body>
</html>'''
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("done")

if __name__ == "__main__":
    main()
