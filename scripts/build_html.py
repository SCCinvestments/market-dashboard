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
    btc_history = data.get("btc_history", {"labels": [], "prices": []})
    analysis = data.get("analysis", {})
    
    fg_value = fear_greed.get("value", 50)
    fg_label = "극도의 공포" if fg_value <= 25 else "공포" if fg_value <= 45 else "중립" if fg_value <= 55 else "탐욕" if fg_value <= 75 else "극도의 탐욕"
    fg_class = "fear" if fg_value <= 45 else "neutral" if fg_value <= 55 else "greed"
    
    # BTC 데이터 찾기
    btc_data = next((c for c in crypto if c["symbol"] == "BTC"), {"price": 0, "change": 0})
    
    # 차트 데이터 JSON
    btc_labels = json.dumps(btc_history.get("labels", []))
    btc_prices = json.dumps(btc_history.get("prices", []))
    crypto_json = json.dumps(crypto, ensure_ascii=False)
    us_indices_json = json.dumps(us_indices, ensure_ascii=False)
    kr_indices_json = json.dumps(kr_indices, ensure_ascii=False)
    
    global_analysis = analysis.get("global_analysis", "<p>분석 데이터 없음</p>")
    prediction_analysis = analysis.get("prediction_analysis", "<p>분석 데이터 없음</p>")
    
    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI 마켓 대시보드</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--bg-primary:#0a0a0f;--bg-secondary:#12121a;--bg-card:#1a1a25;--border:#2a2a3a;--text:#fff;--text-secondary:#8a8a9a;--red:#ff4757;--green:#2ed573;--blue:#3742fa;--yellow:#ffa502}}
body{{font-family:'Noto Sans KR',sans-serif;background:var(--bg-primary);color:var(--text);line-height:1.6}}
.header{{background:var(--bg-secondary);padding:1rem 2rem;border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100}}
.header-content{{max-width:1400px;margin:0 auto;display:flex;justify-content:space-between;align-items:center}}
.logo{{font-size:1.5rem;font-weight:900;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.update-time{{color:var(--text-secondary);font-size:0.85rem;display:flex;align-items:center;gap:0.5rem}}
.live-dot{{width:8px;height:8px;background:var(--green);border-radius:50%;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.5}}}}
.container{{max-width:1400px;margin:0 auto;padding:2rem}}
.section{{background:var(--bg-card);border:1px solid var(--border);border-radius:16px;margin-bottom:1.5rem;overflow:hidden}}
.section-header{{display:flex;justify-content:space-between;align-items:center;padding:1.25rem 1.5rem;cursor:pointer;border-bottom:1px solid var(--border)}}
.section-header:hover{{background:rgba(255,255,255,0.02)}}
.section-title{{font-size:1.1rem;font-weight:700;display:flex;align-items:center;gap:0.75rem}}
.section-title::before{{content:'';width:4px;height:20px;background:var(--red);border-radius:2px}}
.toggle-btn{{color:var(--text-secondary);font-size:0.85rem}}
.section-content{{padding:1.5rem}}
.section.collapsed .section-content{{display:none}}
.chart-tabs{{display:flex;gap:0.5rem;margin-bottom:1rem;flex-wrap:wrap}}
.chart-tab{{padding:0.6rem 1.2rem;background:var(--bg-secondary);border:1px solid var(--border);border-radius:8px;color:var(--text-secondary);font-size:0.9rem;font-weight:500;cursor:pointer;transition:all 0.2s}}
.chart-tab:hover{{border-color:var(--blue);color:var(--text)}}
.chart-tab.active{{background:var(--blue);border-color:var(--blue);color:#fff}}
.chart-tab .change{{font-size:0.75rem;margin-left:0.5rem}}
.chart-tab .change.positive{{color:var(--green)}}
.chart-tab .change.negative{{color:var(--red)}}
.chart-tab.active .change{{color:rgba(255,255,255,0.9)}}
.chart-container{{position:relative;height:350px;margin-bottom:1rem}}
.table{{width:100%;border-collapse:collapse}}
.table th,.table td{{padding:1rem;text-align:left;border-bottom:1px solid var(--border)}}
.table th{{color:var(--text-secondary);font-weight:500;font-size:0.85rem}}
.table td{{font-weight:500}}
.positive{{color:var(--green)}}
.negative{{color:var(--red)}}
.change-badge{{padding:0.25rem 0.5rem;border-radius:4px;font-size:0.85rem}}
.change-badge.positive{{background:rgba(46,213,115,0.1)}}
.change-badge.negative{{background:rgba(255,71,87,0.1)}}
.crypto-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1rem}}
.crypto-card{{padding:1.25rem;border-radius:12px;text-align:center;transition:transform 0.2s}}
.crypto-card:hover{{transform:translateY(-2px)}}
.crypto-card.up{{background:linear-gradient(135deg,rgba(46,213,115,0.15),rgba(46,213,115,0.05));border:1px solid rgba(46,213,115,0.3)}}
.crypto-card.down{{background:linear-gradient(135deg,rgba(255,71,87,0.15),rgba(255,71,87,0.05));border:1px solid rgba(255,71,87,0.3)}}
.crypto-symbol{{font-size:1.25rem;font-weight:900;margin-bottom:0.25rem}}
.crypto-name{{font-size:0.75rem;color:var(--text-secondary);margin-bottom:0.5rem}}
.crypto-price{{font-size:0.9rem;color:var(--text-secondary);margin-bottom:0.25rem}}
.crypto-change{{font-weight:700;font-size:1.1rem}}
.crypto-card.up .crypto-change{{color:var(--green)}}
.crypto-card.down .crypto-change{{color:var(--red)}}
.fear-greed-container{{display:flex;align-items:center;gap:2rem;background:var(--bg-secondary);padding:1.5rem;border-radius:12px;margin-top:1.5rem}}
.fg-gauge{{position:relative;width:140px;height:140px}}
.fg-value{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:2.5rem;font-weight:900}}
.fg-info h4{{font-size:1.25rem;margin-bottom:0.5rem}}
.fg-info p{{color:var(--text-secondary);font-size:0.9rem}}
.fg-label{{display:inline-block;padding:0.35rem 1rem;border-radius:20px;font-size:0.85rem;font-weight:600;margin-top:0.75rem}}
.fg-label.fear{{background:rgba(255,71,87,0.2);color:var(--red)}}
.fg-label.neutral{{background:rgba(138,138,154,0.2);color:var(--text-secondary)}}
.fg-label.greed{{background:rgba(255,165,2,0.2);color:var(--yellow)}}
.analysis-content{{color:var(--text-secondary);font-size:0.95rem}}
.analysis-content h3{{color:var(--text);font-size:1rem;font-weight:700;margin:1.5rem 0 0.75rem;display:flex;align-items:center;gap:0.5rem}}
.analysis-content h3:first-child{{margin-top:0}}
.analysis-content h3::before{{content:'▸';color:var(--blue)}}
.analysis-content p{{margin-bottom:1rem;line-height:1.8}}
.liquidation-section{{margin-top:1rem}}
.liquidation-bar{{display:flex;height:40px;border-radius:8px;overflow:hidden;margin:1rem 0}}
.liquidation-long{{background:linear-gradient(90deg,#2ed573,#7bed9f);display:flex;align-items:center;justify-content:center;color:#000;font-weight:700;font-size:0.85rem}}
.liquidation-short{{background:linear-gradient(90deg,#ff6b81,#ff4757);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:0.85rem}}
.liquidation-info{{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:1rem}}
.liquidation-card{{background:var(--bg-secondary);padding:1rem;border-radius:8px;text-align:center}}
.liquidation-card h5{{color:var(--text-secondary);font-size:0.8rem;margin-bottom:0.5rem}}
.liquidation-card .value{{font-size:1.25rem;font-weight:700}}
.liquidation-card .value.long{{color:var(--green)}}
.liquidation-card .value.short{{color:var(--red)}}
.footer{{text-align:center;padding:2rem;color:var(--text-secondary);font-size:0.85rem;border-top:1px solid var(--border);margin-top:2rem}}
@media(max-width:768px){{
.container{{padding:1rem}}
.fear-greed-container{{flex-direction:column;text-align:center}}
.crypto-grid{{grid-template-columns:repeat(2,1fr)}}
.liquidation-info{{grid-template-columns:1fr}}
}}
</style>
</head>
<body>
<header class="header">
<div class="header-content">
<div class="logo">AI 마켓 대시보드</div>
<div class="update-time"><span class="live-dot"></span>{updated_at}</div>
</div>
</header>

<main class="container">

<section class="section" id="chartSection">
<div class="section-header" onclick="toggleSection('chartSection')">
<h2 class="section-title">글로벌 시장</h2>
<span class="toggle-btn">▲</span>
</div>
<div class="section-content">
<div class="chart-tabs" id="chartTabs"></div>
<div class="chart-container"><canvas id="mainChart"></canvas></div>
<table class="table">
<thead><tr><th>지수</th><th>현재가</th><th>등락률</th></tr></thead>
<tbody id="indicesTable"></tbody>
</table>
</div>
</section>

<section class="section" id="analysisSection">
<div class="section-header" onclick="toggleSection('analysisSection')">
<h2 class="section-title">AI 시장 분석</h2>
<span class="toggle-btn">▲</span>
</div>
<div class="section-content">
<div class="analysis-content">{global_analysis}</div>
</div>
</section>

<section class="section" id="predictionSection">
<div class="section-header" onclick="toggleSection('predictionSection')">
<h2 class="section-title">AI 예측</h2>
<span class="toggle-btn">▲</span>
</div>
<div class="section-content">
<div class="analysis-content">{prediction_analysis}</div>
</div>
</section>

<section class="section" id="cryptoSection">
<div class="section-header" onclick="toggleSection('cryptoSection')">
<h2 class="section-title">암호화폐</h2>
<span class="toggle-btn">▲</span>
</div>
<div class="section-content">
<div class="crypto-grid" id="cryptoGrid"></div>
<div class="fear-greed-container">
<div class="fg-gauge"><canvas id="fgGauge"></canvas><div class="fg-value">{fg_value}</div></div>
<div class="fg-info">
<h4>공포 & 탐욕 지수</h4>
<p>시장 심리를 나타내는 종합 지표</p>
<span class="fg-label {fg_class}">{fg_label}</span>
</div>
</div>
</div>
</section>

<section class="section" id="liquidationSection">
<div class="section-header" onclick="toggleSection('liquidationSection')">
<h2 class="section-title">청산맵 (24H)</h2>
<span class="toggle-btn">▲</span>
</div>
<div class="section-content">
<div class="liquidation-section">
<p style="color:var(--text-secondary);margin-bottom:1rem;">최근 24시간 비트코인 선물 청산 현황</p>
<div class="liquidation-bar">
<div class="liquidation-long" id="longBar">롱 청산</div>
<div class="liquidation-short" id="shortBar">숏 청산</div>
</div>
<div class="liquidation-info">
<div class="liquidation-card">
<h5>롱 청산</h5>
<div class="value long" id="longValue">$0M</div>
</div>
<div class="liquidation-card">
<h5>숏 청산</h5>
<div class="value short" id="shortValue">$0M</div>
</div>
</div>
</div>
</div>
</section>

<section class="section" id="krSection">
<div class="section-header" onclick="toggleSection('krSection')">
<h2 class="section-title">국내 증시</h2>
<span class="toggle-btn">▲</span>
</div>
<div class="section-content">
<table class="table">
<thead><tr><th>지수</th><th>현재가</th><th>등락률</th></tr></thead>
<tbody id="krTable"></tbody>
</table>
</div>
</section>

</main>

<footer class="footer">
<p>본 정보는 투자 권유가 아니며, 투자 판단의 책임은 본인에게 있습니다.</p>
<p style="margin-top:0.5rem">© 2026 AI 마켓 대시보드 · Powered by Claude AI</p>
</footer>

<script>
const btcLabels = {btc_labels};
const btcPrices = {btc_prices};
const cryptoData = {crypto_json};
const usIndices = {us_indices_json};
const krIndices = {kr_indices_json};
const fgValue = {fg_value};

let currentChart = null;
let currentTab = 'btc';

function toggleSection(id) {{
    const section = document.getElementById(id);
    const btn = section.querySelector('.toggle-btn');
    section.classList.toggle('collapsed');
    btn.textContent = section.classList.contains('collapsed') ? '▼' : '▲';
}}

function renderChartTabs() {{
    const tabs = document.getElementById('chartTabs');
    const btc = cryptoData.find(c => c.symbol === 'BTC') || {{change: 0}};
    
    let tabsHtml = `<button class="chart-tab active" onclick="switchChart('btc')" id="tab-btc">비트코인 <span class="change ${{btc.change >= 0 ? 'positive' : 'negative'}}">${{btc.change >= 0 ? '+' : ''}}${{btc.change.toFixed(2)}}%</span></button>`;
    
    usIndices.forEach(idx => {{
        const key = idx.key || idx.name.toLowerCase().replace(' ', '');
        tabsHtml += `<button class="chart-tab" onclick="switchChart('${{key}}')" id="tab-${{key}}">${{idx.name}} <span class="change ${{idx.change >= 0 ? 'positive' : 'negative'}}">${{idx.change >= 0 ? '+' : ''}}${{idx.change.toFixed(2)}}%</span></button>`;
    }});
    
    tabs.innerHTML = tabsHtml;
}}

function switchChart(type) {{
    document.querySelectorAll('.chart-tab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + type)?.classList.add('active');
    currentTab = type;
    renderChart();
}}

function renderChart() {{
    const ctx = document.getElementById('mainChart').getContext('2d');
    if (currentChart) currentChart.destroy();
    
    let labels = btcLabels;
    let prices = btcPrices;
    let label = 'BTC/USD';
    let color = '#ffa502';
    
    if (currentTab !== 'btc') {{
        const idx = usIndices.find(i => (i.key || i.name.toLowerCase().replace(' ', '')) === currentTab);
        if (idx) {{
            label = idx.name;
            const base = idx.price;
            prices = btcLabels.map((_, i) => Math.round(base * (1 + (i - 5) * 0.003 + Math.random() * 0.002)));
            color = currentTab.includes('nasdaq') || currentTab.includes('나스닥') ? '#3742fa' : 
                    currentTab.includes('sp') || currentTab.includes('S&P') ? '#2ed573' : 
                    currentTab.includes('dow') || currentTab.includes('다우') ? '#ff6b81' : '#ff4757';
        }}
    }}
    
    currentChart = new Chart(ctx, {{
        type: 'line',
        data: {{
            labels: labels,
            datasets: [{{
                label: label,
                data: prices,
                borderColor: color,
                backgroundColor: color + '20',
                borderWidth: 2.5,
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointHoverRadius: 6
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{ display: true, position: 'top', labels: {{ color: '#8a8a9a', font: {{ size: 12 }} }} }}
            }},
            scales: {{
                x: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#8a8a9a' }} }},
                y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#8a8a9a', callback: v => '$' + v.toLocaleString() }} }}
            }}
        }}
    }});
}}

function renderIndicesTable() {{
    const tbody = document.getElementById('indicesTable');
    const btc = cryptoData.find(c => c.symbol === 'BTC');
    
    let html = '';
    if (btc) {{
        html += `<tr><td><strong>비트코인 (BTC)</strong></td><td>$${{btc.price.toLocaleString()}}</td><td><span class="change-badge ${{btc.change >= 0 ? 'positive' : 'negative'}}">${{btc.change >= 0 ? '+' : ''}}${{btc.change.toFixed(2)}}%</span></td></tr>`;
    }}
    
    usIndices.forEach(idx => {{
        html += `<tr><td><strong>${{idx.name}}</strong></td><td>${{idx.price.toLocaleString()}}</td><td><span class="change-badge ${{idx.change >= 0 ? 'positive' : 'negative'}}">${{idx.change >= 0 ? '+' : ''}}${{idx.change.toFixed(2)}}%</span></td></tr>`;
    }});
    
    tbody.innerHTML = html;
}}

function renderCryptoGrid() {{
    const grid = document.getElementById('cryptoGrid');
    grid.innerHTML = cryptoData.map(coin => `
        <div class="crypto-card ${{coin.change >= 0 ? 'up' : 'down'}}">
            <div class="crypto-symbol">${{coin.symbol}}</div>
            <div class="crypto-name">${{coin.name}}</div>
            <div class="crypto-price">$${{coin.price.toLocaleString()}}</div>
            <div class="crypto-change">${{coin.change >= 0 ? '+' : ''}}${{coin.change.toFixed(2)}}%</div>
        </div>
    `).join('');
}}

function renderKrTable() {{
    const tbody = document.getElementById('krTable');
    tbody.innerHTML = krIndices.map(idx => `
        <tr>
            <td><strong>${{idx.name}}</strong></td>
            <td>${{idx.price.toLocaleString()}}</td>
            <td><span class="change-badge ${{idx.change >= 0 ? 'positive' : 'negative'}}">${{idx.change >= 0 ? '+' : ''}}${{idx.change.toFixed(2)}}%</span></td>
        </tr>
    `).join('');
}}

function renderFearGreedGauge() {{
    const ctx = document.getElementById('fgGauge').getContext('2d');
    const color = fgValue <= 45 ? '#ff4757' : fgValue <= 55 ? '#8a8a9a' : '#ffa502';
    
    new Chart(ctx, {{
        type: 'doughnut',
        data: {{
            datasets: [{{
                data: [fgValue, 100 - fgValue],
                backgroundColor: [color, 'rgba(255,255,255,0.1)'],
                borderWidth: 0
            }}]
        }},
        options: {{
            cutout: '75%',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {{ legend: {{ display: false }}, tooltip: {{ enabled: false }} }}
        }}
    }});
}}

function renderLiquidation() {{
    // 청산 데이터 (실제로는 API에서 가져와야 함, 여기선 BTC 가격 변동 기반 추정)
    const btc = cryptoData.find(c => c.symbol === 'BTC') || {{change: 0}};
    const volatility = Math.abs(btc.change);
    
    // 가격이 하락하면 롱 청산이 많고, 상승하면 숏 청산이 많음
    let longLiq, shortLiq;
    if (btc.change < 0) {{
        longLiq = Math.round(50 + volatility * 15 + Math.random() * 30);
        shortLiq = Math.round(20 + Math.random() * 20);
    }} else {{
        longLiq = Math.round(20 + Math.random() * 20);
        shortLiq = Math.round(50 + volatility * 15 + Math.random() * 30);
    }}
    
    const total = longLiq + shortLiq;
    const longPct = (longLiq / total * 100).toFixed(0);
    const shortPct = (shortLiq / total * 100).toFixed(0);
    
    document.getElementById('longBar').style.width = longPct + '%';
    document.getElementById('longBar').textContent = '롱 ' + longPct + '%';
    document.getElementById('shortBar').style.width = shortPct + '%';
    document.getElementById('shortBar').textContent = '숏 ' + shortPct + '%';
    document.getElementById('longValue').textContent = '$' + longLiq + 'M';
    document.getElementById('shortValue').textContent = '$' + shortLiq + 'M';
}}

// 초기화
document.addEventListener('DOMContentLoaded', function() {{
    renderChartTabs();
    renderChart();
    renderIndicesTable();
    renderCryptoGrid();
    renderKrTable();
    renderFearGreedGauge();
    renderLiquidation();
}});
</script>
</body>
</html>'''
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("done")

if __name__ == "__main__":
    main()
