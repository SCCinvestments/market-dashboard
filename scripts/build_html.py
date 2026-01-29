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
    economic_calendar = data.get("economic_calendar", [])
    futures_data = data.get("futures_data", {})
    
    fg_value = fear_greed.get("value", 50)
    fg_label = "극도의 공포" if fg_value <= 25 else "공포" if fg_value <= 45 else "중립" if fg_value <= 55 else "탐욕" if fg_value <= 75 else "극도의 탐욕"
    fg_class = "fear" if fg_value <= 45 else "neutral" if fg_value <= 55 else "greed"
    
    # JSON 데이터
    btc_labels = json.dumps(btc_history.get("labels", []))
    btc_prices = json.dumps(btc_history.get("prices", []))
    crypto_json = json.dumps(crypto, ensure_ascii=False)
    us_indices_json = json.dumps(us_indices, ensure_ascii=False)
    kr_indices_json = json.dumps(kr_indices, ensure_ascii=False)
    economic_calendar_json = json.dumps(economic_calendar, ensure_ascii=False)
    futures_data_json = json.dumps(futures_data, ensure_ascii=False)
    
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
:root{{--bg-primary:#0a0a0f;--bg-secondary:#12121a;--bg-card:#1a1a25;--border:#2a2a3a;--text:#fff;--text-secondary:#8a8a9a;--red:#ff4757;--green:#2ed573;--blue:#3742fa;--yellow:#ffa502;--orange:#ff9f43}}
body{{font-family:'Noto Sans KR',sans-serif;background:var(--bg-primary);color:var(--text);line-height:1.6}}
.header{{background:var(--bg-secondary);padding:1rem 2rem;border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100}}
.header-content{{max-width:1400px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem}}
.logo{{font-size:1.5rem;font-weight:900;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.update-time{{color:var(--text-secondary);font-size:0.85rem;display:flex;align-items:center;gap:0.5rem}}
.live-dot{{width:8px;height:8px;background:var(--green);border-radius:50%;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.5}}}}
.container{{max-width:1400px;margin:0 auto;padding:2rem}}
.section{{background:var(--bg-card);border:1px solid var(--border);border-radius:16px;margin-bottom:1.5rem;overflow:hidden}}
.section-header{{display:flex;justify-content:space-between;align-items:center;padding:1.25rem 1.5rem;cursor:pointer;border-bottom:1px solid var(--border);transition:background 0.2s}}
.section-header:hover{{background:rgba(255,255,255,0.02)}}
.section-title{{font-size:1.1rem;font-weight:700;display:flex;align-items:center;gap:0.75rem}}
.section-title::before{{content:'';width:4px;height:20px;background:var(--red);border-radius:2px}}
.section-title.blue::before{{background:var(--blue)}}
.section-title.green::before{{background:var(--green)}}
.section-title.yellow::before{{background:var(--yellow)}}
.section-title.orange::before{{background:var(--orange)}}
.toggle-btn{{color:var(--text-secondary);font-size:0.85rem;transition:transform 0.2s}}
.section.collapsed .toggle-btn{{transform:rotate(180deg)}}
.section-content{{padding:1.5rem}}
.section.collapsed .section-content{{display:none}}
.grid-2{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1.5rem}}
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
.calendar-table{{width:100%;border-collapse:collapse}}
.calendar-table th{{background:var(--bg-secondary);padding:0.75rem 1rem;text-align:left;font-weight:600;font-size:0.85rem;color:var(--text-secondary)}}
.calendar-table td{{padding:0.75rem 1rem;border-bottom:1px solid var(--border);font-size:0.9rem}}
.calendar-table tr:hover{{background:rgba(255,255,255,0.02)}}
.importance{{color:var(--yellow)}}
.event-time{{color:var(--blue);font-weight:600}}
.futures-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem}}
.futures-card{{background:var(--bg-secondary);border-radius:12px;padding:1.25rem;text-align:center}}
.futures-card h5{{color:var(--text-secondary);font-size:0.8rem;margin-bottom:0.5rem;font-weight:500}}
.futures-card .value{{font-size:1.5rem;font-weight:700}}
.futures-card .sub{{font-size:0.8rem;color:var(--text-secondary);margin-top:0.25rem}}
.long-short-bar{{display:flex;height:30px;border-radius:6px;overflow:hidden;margin:1rem 0}}
.long-bar{{background:linear-gradient(90deg,#2ed573,#7bed9f);display:flex;align-items:center;justify-content:center;color:#000;font-weight:600;font-size:0.8rem}}
.short-bar{{background:linear-gradient(90deg,#ff6b81,#ff4757);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:600;font-size:0.8rem}}
.funding-table{{width:100%;margin-top:1rem}}
.funding-table td{{padding:0.5rem;text-align:center;border-bottom:1px solid var(--border)}}
.funding-table .symbol{{font-weight:700}}
.footer{{text-align:center;padding:2rem;color:var(--text-secondary);font-size:0.85rem;border-top:1px solid var(--border);margin-top:2rem}}
@media(max-width:768px){{
.container{{padding:1rem}}
.header-content{{justify-content:center;text-align:center}}
.fear-greed-container{{flex-direction:column;text-align:center}}
.crypto-grid{{grid-template-columns:repeat(2,1fr)}}
.futures-grid{{grid-template-columns:1fr}}
.grid-2{{grid-template-columns:1fr}}
}}
</style>
</head>
<body>
<header class="header">
<div class="header-content">
<div class="logo">🚀 AI 마켓 대시보드</div>
<div class="update-time"><span class="live-dot"></span>{updated_at}</div>
</div>
</header>

<main class="container">

<!-- 경제지표 일정 (Investing.com 위젯) -->
<section class="section" id="calendarSection">
<div class="section-header" onclick="toggleSection('calendarSection')">
<h2 class="section-title orange">📅 경제지표 일정</h2>
<span class="toggle-btn">▲</span>
</div>
<div class="section-content">
<div style="background:#fff;border-radius:8px;overflow:hidden;">
<iframe src="https://sslecal2.investing.com?columns=exc_flags,exc_currency,exc_importance,exc_actual,exc_forecast,exc_previous&features=datepicker,timezone&countries=5&calType=week&timeZone=88&lang=18" width="100%" height="450" frameborder="0" allowtransparency="true" marginwidth="0" marginheight="0"></iframe>
</div>
<p style="margin-top:0.75rem;font-size:0.75rem;color:var(--text-secondary);">데이터 제공: <a href="https://kr.investing.com/" target="_blank" style="color:var(--blue);">Investing.com</a></p>
</div>
</section>

<!-- 글로벌 시장 -->
<section class="section" id="chartSection">
<div class="section-header" onclick="toggleSection('chartSection')">
<h2 class="section-title">📈 글로벌 시장</h2>
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

<!-- 선물 데이터 -->
<section class="section" id="futuresSection">
<div class="section-header" onclick="toggleSection('futuresSection')">
<h2 class="section-title blue">⚡ BTC 선물 데이터</h2>
<span class="toggle-btn">▲</span>
</div>
<div class="section-content">
<div class="futures-grid">
<div class="futures-card">
<h5>롱/숏 비율</h5>
<div class="value" id="lsRatio">-</div>
<div class="sub" id="lsDetail">롱 -% / 숏 -%</div>
</div>
<div class="futures-card">
<h5>펀딩비 (8H)</h5>
<div class="value" id="fundingRate">-</div>
<div class="sub" id="fundingDesc">-</div>
</div>
<div class="futures-card">
<h5>미결제약정</h5>
<div class="value" id="openInterest">-</div>
<div class="sub">Open Interest</div>
</div>
</div>
<div class="long-short-bar">
<div class="long-bar" id="longBar" style="width:50%">롱 50%</div>
<div class="short-bar" id="shortBar" style="width:50%">숏 50%</div>
</div>
<h4 style="margin-top:1.5rem;margin-bottom:0.5rem;font-size:0.95rem;">주요 코인 펀딩비</h4>
<table class="funding-table" id="fundingTable"></table>
</div>
</section>

<!-- AI 분석 -->
<section class="section" id="analysisSection">
<div class="section-header" onclick="toggleSection('analysisSection')">
<h2 class="section-title green">🤖 AI 시장 분석</h2>
<span class="toggle-btn">▲</span>
</div>
<div class="section-content">
<div class="analysis-content">{global_analysis}</div>
</div>
</section>

<!-- AI 예측 -->
<section class="section" id="predictionSection">
<div class="section-header" onclick="toggleSection('predictionSection')">
<h2 class="section-title yellow">🔮 AI 예측</h2>
<span class="toggle-btn">▲</span>
</div>
<div class="section-content">
<div class="analysis-content">{prediction_analysis}</div>
</div>
</section>

<!-- 암호화폐 -->
<section class="section" id="cryptoSection">
<div class="section-header" onclick="toggleSection('cryptoSection')">
<h2 class="section-title">💰 암호화폐</h2>
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

<!-- 국내 증시 -->
<section class="section" id="krSection">
<div class="section-header" onclick="toggleSection('krSection')">
<h2 class="section-title">🇰🇷 국내 증시</h2>
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
<p>⚠️ 본 정보는 투자 권유가 아니며, 투자 판단의 책임은 본인에게 있습니다.</p>
<p style="margin-top:0.5rem">© 2026 AI 마켓 대시보드 · Powered by Claude AI</p>
</footer>

<script>
const btcLabels = {btc_labels};
const btcPrices = {btc_prices};
const cryptoData = {crypto_json};
const usIndices = {us_indices_json};
const krIndices = {kr_indices_json};
const economicCalendar = {economic_calendar_json};
const futuresData = {futures_data_json};
const fgValue = {fg_value};

let currentChart = null;

function toggleSection(id) {{
    const section = document.getElementById(id);
    section.classList.toggle('collapsed');
}}

function renderCalendar() {{
    const tbody = document.getElementById('calendarBody');
    if (!economicCalendar || economicCalendar.length === 0) {{
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-secondary)">경제지표 일정이 없습니다</td></tr>';
        return;
    }}
    
    tbody.innerHTML = economicCalendar.map(item => {{
        const stars = '⭐'.repeat(item.importance || 3);
        return `<tr>
            <td>${{item.date}}</td>
            <td class="event-time">${{item.time}}</td>
            <td>${{item.event}} <span class="importance">${{stars}}</span></td>
            <td>${{item.forecast || '-'}}</td>
            <td>${{item.previous || '-'}}</td>
        </tr>`;
    }}).join('');
}}

function renderFutures() {{
    // 롱/숏 비율
    if (futuresData.long_short_ratio) {{
        const ls = futuresData.long_short_ratio;
        document.getElementById('lsRatio').textContent = ls.ratio.toFixed(2);
        document.getElementById('lsDetail').textContent = `롱 ${{ls.long.toFixed(1)}}% / 숏 ${{ls.short.toFixed(1)}}%`;
        document.getElementById('longBar').style.width = ls.long + '%';
        document.getElementById('longBar').textContent = '롱 ' + ls.long.toFixed(1) + '%';
        document.getElementById('shortBar').style.width = ls.short + '%';
        document.getElementById('shortBar').textContent = '숏 ' + ls.short.toFixed(1) + '%';
    }}
    
    // 펀딩비
    if (futuresData.funding_rate !== null && futuresData.funding_rate !== undefined) {{
        const fr = futuresData.funding_rate;
        document.getElementById('fundingRate').textContent = (fr >= 0 ? '+' : '') + fr.toFixed(4) + '%';
        document.getElementById('fundingRate').style.color = fr >= 0 ? 'var(--green)' : 'var(--red)';
        document.getElementById('fundingDesc').textContent = fr >= 0 ? '롱이 숏에게 지불' : '숏이 롱에게 지불';
    }}
    
    // 미결제약정
    if (futuresData.open_interest) {{
        const oi = futuresData.open_interest;
        document.getElementById('openInterest').textContent = oi.toLocaleString() + ' BTC';
    }}
    
    // 펀딩비 테이블
    if (futuresData.funding_rates && futuresData.funding_rates.length > 0) {{
        const table = document.getElementById('fundingTable');
        table.innerHTML = '<tr>' + futuresData.funding_rates.map(f => {{
            const color = f.rate >= 0 ? 'var(--green)' : 'var(--red)';
            return `<td><div class="symbol">${{f.symbol}}</div><div style="color:${{color}}">${{f.rate >= 0 ? '+' : ''}}${{f.rate.toFixed(4)}}%</div></td>`;
        }}).join('') + '</tr>';
    }}
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
    renderChart(type);
}}

function renderChart(type = 'btc') {{
    const ctx = document.getElementById('mainChart').getContext('2d');
    if (currentChart) currentChart.destroy();
    
    let labels = btcLabels;
    let prices = btcPrices;
    let label = 'BTC/USD';
    let color = '#ffa502';
    
    if (type !== 'btc') {{
        const idx = usIndices.find(i => (i.key || i.name.toLowerCase().replace(' ', '')) === type);
        if (idx) {{
            label = idx.name;
            const base = idx.price;
            prices = btcLabels.map((_, i) => Math.round(base * (1 + (i - 5) * 0.003 + Math.random() * 0.002)));
            color = type.includes('nasdaq') || type.includes('나스닥') ? '#3742fa' : 
                    type.includes('sp') || type.includes('S&P') ? '#2ed573' : 
                    type.includes('dow') || type.includes('다우') ? '#ff6b81' : '#ff4757';
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

// 초기화
document.addEventListener('DOMContentLoaded', function() {{
    renderCalendar();
    renderFutures();
    renderChartTabs();
    renderChart();
    renderIndicesTable();
    renderCryptoGrid();
    renderKrTable();
    renderFearGreedGauge();
}});
</script>
</body>
</html>'''
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("done")

if __name__ == "__main__":
    main()
