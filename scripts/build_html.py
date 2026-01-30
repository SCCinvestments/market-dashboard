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
.modal-overlay{{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.8);display:none;justify-content:center;align-items:center;z-index:1000;padding:1rem}}
.modal-overlay.active{{display:flex}}
.modal{{background:var(--bg-card);border:1px solid var(--border);border-radius:16px;max-width:500px;width:100%;max-height:80vh;overflow-y:auto}}
.modal-header{{padding:1.25rem 1.5rem;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}}
.modal-header h3{{font-size:1.1rem;font-weight:700;color:var(--yellow)}}
.modal-close{{background:none;border:none;color:var(--text-secondary);font-size:1.5rem;cursor:pointer;padding:0.5rem}}
.modal-close:hover{{color:var(--text)}}
.modal-body{{padding:1.5rem}}
.modal-section{{margin-bottom:1.25rem}}
.modal-section:last-child{{margin-bottom:0}}
.modal-section h4{{font-size:0.9rem;color:var(--blue);margin-bottom:0.5rem;font-weight:600}}
.modal-section p{{color:var(--text-secondary);font-size:0.9rem;line-height:1.7}}
.modal-meta{{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1rem;padding:1rem;background:var(--bg-secondary);border-radius:8px}}
.modal-meta-item{{flex:1;min-width:80px}}
.modal-meta-item span{{display:block;font-size:0.75rem;color:var(--text-secondary)}}
.modal-meta-item strong{{font-size:1rem}}
.scenario-box{{padding:0.75rem;border-radius:8px;margin-bottom:0.5rem;font-size:0.85rem}}
.scenario-box.bullish{{background:rgba(46,213,115,0.1);border-left:3px solid var(--green)}}
.scenario-box.bearish{{background:rgba(255,71,87,0.1);border-left:3px solid var(--red)}}
.scenario-label{{font-weight:600;margin-bottom:0.25rem}}
.calendar-table tr{{cursor:pointer;transition:background 0.2s}}
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

<!-- 경제지표 일정 -->
<section class="section" id="calendarSection">
<div class="section-header" onclick="toggleSection('calendarSection')">
<h2 class="section-title orange">📅 미국 경제지표 일정</h2>
<span class="toggle-btn">▲</span>
</div>
<div class="section-content">
<table class="calendar-table">
<thead><tr><th>날짜</th><th>시간(KST)</th><th>이벤트</th><th>예측</th><th>이전</th><th>중요도</th></tr></thead>
<tbody id="calendarBody"></tbody>
</table>
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

<!-- 경제지표 모달 -->
<div class="modal-overlay" id="calendarModal">
<div class="modal">
<div class="modal-header">
<h3 id="modalTitle">⭐⭐⭐ 경제지표 상세</h3>
<button class="modal-close" onclick="closeModal()">&times;</button>
</div>
<div class="modal-body">
<div class="modal-meta">
<div class="modal-meta-item"><span>시간(KST)</span><strong id="modalTime">-</strong></div>
<div class="modal-meta-item"><span>예측</span><strong id="modalForecast">-</strong></div>
<div class="modal-meta-item"><span>이전</span><strong id="modalPrevious">-</strong></div>
</div>
<div class="modal-section">
<h4>📊 지표 설명</h4>
<p id="modalDesc">-</p>
</div>
<div class="modal-section">
<h4>🎯 예측치 해석</h4>
<p id="modalInterpret">-</p>
</div>
<div class="modal-section">
<h4>📈 시나리오 분석</h4>
<div class="scenario-box bullish">
<div class="scenario-label">🟢 예측치 상회 시</div>
<div id="modalBullish">-</div>
</div>
<div class="scenario-box bearish">
<div class="scenario-label">🔴 예측치 하회 시</div>
<div id="modalBearish">-</div>
</div>
</div>
<div class="modal-section">
<h4>⭐ 중요도가 높은 이유</h4>
<p id="modalWhy">-</p>
</div>
</div>
</div>
</div>

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
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--text-secondary);padding:2rem;">예정된 주요 경제지표가 없습니다</td></tr>';
        return;
    }}
    
    // 오늘 날짜 구하기 (KST)
    const now = new Date();
    const kstOffset = 9 * 60;
    const kstTime = new Date(now.getTime() + (kstOffset + now.getTimezoneOffset()) * 60000);
    const todayStr = (kstTime.getMonth() + 1) + '/' + kstTime.getDate();
    
    tbody.innerHTML = economicCalendar.map((item, idx) => {{
        const importance = item.importance === 'high' ? '⭐⭐⭐' : item.importance === 'medium' ? '⭐⭐' : '⭐';
        const impClass = item.importance === 'high' ? 'color:var(--yellow)' : 'color:var(--text-secondary)';
        const isNextDay = item.date !== todayStr;
        const rowStyle = isNextDay ? 'background:rgba(255,255,255,0.03);' : '';
        return `<tr style="${{rowStyle}}" onclick="openCalendarModal(${{idx}})" title="클릭하여 상세 정보 보기">
            <td>${{item.date || '-'}}</td>
            <td class="event-time">${{item.time || '-'}}</td>
            <td>${{item.event || '-'}}</td>
            <td>${{item.forecast || '-'}}</td>
            <td>${{item.previous || '-'}}</td>
            <td style="${{impClass}}">${{importance}}</td>
        </tr>`;
    }}).join('');
}}

// 경제지표 해설 데이터
const indicatorInfo = {{
    'PPI': {{
        desc: '생산자물가지수(PPI)는 생산자가 판매하는 상품과 서비스의 가격 변동을 측정합니다. 인플레이션의 선행지표로 소비자물가(CPI)보다 먼저 가격 압력을 감지할 수 있습니다.',
        why: '연준(Fed)의 금리 결정에 직접적 영향을 미치며, 기업 수익성과 향후 소비자물가 방향을 예측하는 핵심 지표입니다.',
        bullish: '달러 강세, 금리 인상 기대감 상승, 주식시장 단기 하락 가능, 크립토 약세',
        bearish: '달러 약세, 금리 인하 기대감 상승, 주식시장 호재, 크립토 강세'
    }},
    'PMI': {{
        desc: '구매관리자지수(PMI)는 제조업/서비스업의 경기 상황을 나타내는 선행지표입니다. 50 이상이면 경기 확장, 50 미만이면 경기 수축을 의미합니다.',
        why: '경기 흐름을 가장 빠르게 반영하는 지표로, GDP 성장률을 예측하는 데 핵심적인 역할을 합니다.',
        bullish: '경제 성장 기대, 위험자산 선호, 주식/크립토 강세',
        bearish: '경기 침체 우려, 안전자산 선호, 달러/금/채권 강세'
    }},
    'CPI': {{
        desc: '소비자물가지수(CPI)는 가계가 구매하는 상품과 서비스의 가격 변동을 측정합니다. 인플레이션을 가장 직접적으로 나타내는 핵심 지표입니다.',
        why: '연준의 통화정책 결정에 가장 중요한 지표이며, 금리와 모든 자산 가격에 직접적 영향을 미칩니다.',
        bullish: '금리 인상 → 달러 강세, 주식/크립토 약세',
        bearish: '금리 인하 기대 → 달러 약세, 주식/크립토 강세'
    }},
    '고용': {{
        desc: '비농업 고용지표(NFP)는 미국 노동시장의 건강 상태를 나타내며, 농업을 제외한 신규 일자리 수를 측정합니다.',
        why: '연준의 두 가지 목표 중 하나인 "완전고용"을 직접 측정하는 지표로, 금리 결정에 핵심적입니다.',
        bullish: '경제 강세 신호, 금리 인상 가능성, 달러 강세',
        bearish: '경기 둔화 우려, 금리 인하 기대, 위험자산 약세'
    }},
    'GDP': {{
        desc: '국내총생산(GDP)은 한 나라의 경제 활동을 종합적으로 측정하는 가장 중요한 경제지표입니다.',
        why: '경제 전체의 건강 상태를 보여주며, 모든 자산 가격과 정책 결정의 기반이 됩니다.',
        bullish: '경제 성장 확인, 위험자산 강세, 달러 강세',
        bearish: '경기 침체 우려, 안전자산 선호, 채권 강세'
    }},
    'FOMC': {{
        desc: 'FOMC(연방공개시장위원회)는 미국의 기준금리와 통화정책을 결정하는 연준의 핵심 의사결정 기구입니다.',
        why: '전 세계 금융시장의 방향을 결정짓는 가장 중요한 이벤트입니다. 금리, 양적완화, 경제 전망 등을 발표합니다.',
        bullish: '금리 인상/매파적 발언 → 달러 강세, 주식/크립토 약세',
        bearish: '금리 인하/비둘기파적 발언 → 달러 약세, 주식/크립토 강세'
    }},
    '소매': {{
        desc: '소매판매는 소비자 지출 동향을 측정하며, 미국 GDP의 약 70%를 차지하는 소비를 직접 반영합니다.',
        why: '소비자 신뢰와 경제 활력을 나타내는 핵심 지표로, 경기 방향을 예측하는 데 중요합니다.',
        bullish: '소비 증가 → 경제 성장 기대, 위험자산 강세',
        bearish: '소비 감소 → 경기 둔화 우려, 방어적 포지션'
    }},
    '실업': {{
        desc: '실업률과 실업수당 청구건수는 노동시장의 건강 상태를 실시간으로 보여주는 지표입니다.',
        why: '연준의 고용 목표 달성 여부를 판단하는 핵심 지표이며, 소비력과 직결됩니다.',
        bullish: '실업 감소 → 경제 강세, 금리 인상 가능',
        bearish: '실업 증가 → 경기 둔화, 금리 인하 기대'
    }}
}};

function getIndicatorInfo(eventName) {{
    const keywords = Object.keys(indicatorInfo);
    for (const kw of keywords) {{
        if (eventName.includes(kw)) {{
            return indicatorInfo[kw];
        }}
    }}
    // 기본 정보
    return {{
        desc: '이 지표는 미국 경제의 특정 부문을 측정하는 중요한 경제 데이터입니다.',
        why: '시장 참여자들이 주목하는 핵심 지표로, 연준의 통화정책과 자산 가격에 영향을 미칩니다.',
        bullish: '예상보다 강한 수치 → 경제 낙관론, 해당 섹터 관련 자산 영향',
        bearish: '예상보다 약한 수치 → 경제 비관론, 시장 변동성 확대 가능'
    }};
}}

function openCalendarModal(idx) {{
    const item = economicCalendar[idx];
    if (!item) return;
    
    const info = getIndicatorInfo(item.event);
    
    document.getElementById('modalTitle').textContent = '⭐⭐⭐ ' + item.event;
    document.getElementById('modalTime').textContent = item.date + ' ' + item.time;
    document.getElementById('modalForecast').textContent = item.forecast || '-';
    document.getElementById('modalPrevious').textContent = item.previous || '-';
    document.getElementById('modalDesc').textContent = item.description || info.desc;
    
    // 예측치 해석
    let interpret = '';
    if (item.forecast && item.forecast !== '-' && item.previous && item.previous !== '-') {{
        const forecastNum = parseFloat(item.forecast.replace(/[^0-9.-]/g, ''));
        const prevNum = parseFloat(item.previous.replace(/[^0-9.-]/g, ''));
        if (!isNaN(forecastNum) && !isNaN(prevNum)) {{
            if (forecastNum > prevNum) {{
                interpret = `예측치(${{item.forecast}})가 이전치(${{item.previous}})보다 높습니다. 시장은 이 지표의 상승을 예상하고 있습니다.`;
            }} else if (forecastNum < prevNum) {{
                interpret = `예측치(${{item.forecast}})가 이전치(${{item.previous}})보다 낮습니다. 시장은 이 지표의 하락을 예상하고 있습니다.`;
            }} else {{
                interpret = `예측치(${{item.forecast}})가 이전치와 동일합니다. 시장은 현 수준 유지를 예상합니다.`;
            }}
        }} else {{
            interpret = `예측: ${{item.forecast}} / 이전: ${{item.previous}}`;
        }}
    }} else {{
        interpret = '예측치 또는 이전치 데이터가 아직 발표되지 않았습니다.';
    }}
    document.getElementById('modalInterpret').textContent = interpret;
    
    document.getElementById('modalBullish').textContent = info.bullish;
    document.getElementById('modalBearish').textContent = info.bearish;
    document.getElementById('modalWhy').textContent = info.why;
    
    document.getElementById('calendarModal').classList.add('active');
}}

function closeModal() {{
    document.getElementById('calendarModal').classList.remove('active');
}}

// ESC 키로 모달 닫기
document.addEventListener('keydown', function(e) {{
    if (e.key === 'Escape') closeModal();
}});

// 모달 바깥 클릭 시 닫기
document.getElementById('calendarModal').addEventListener('click', function(e) {{
    if (e.target === this) closeModal();
}});


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
