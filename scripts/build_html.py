import json
import base64

def obfuscate_js(js_code):
    """JavaScript 코드 난독화 (UTF-8 안전한 Base64)"""
    # UTF-8 바이트로 변환 후 Base64
    encoded = base64.b64encode(js_code.encode('utf-8')).decode('ascii')
    # decodeURIComponent + atob 조합으로 UTF-8 복원
    return f'eval(decodeURIComponent(escape(atob("{encoded}"))))'

def main():
    print("build start")
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 암호화된 데이터 가져오기
    encrypted_data = data.get("encrypted", "")
    updated_at = data.get("updated_at", "")
    
    # 메인 앱 JavaScript (난독화할 코드)
    app_js = '''
const ENCRYPTED_DATA = "''' + encrypted_data + '''";

let decryptedData = null;
let currentChart = null;

function decrypt(encrypted, password) {
    try {
        const binaryStr = atob(encrypted);
        const bytes = new Uint8Array(binaryStr.length);
        for (let i = 0; i < binaryStr.length; i++) {
            bytes[i] = binaryStr.charCodeAt(i);
        }
        const keyBytes = [];
        for (let i = 0; i < bytes.length; i++) {
            keyBytes.push(password.charCodeAt(i % password.length));
        }
        const decryptedBytes = new Uint8Array(bytes.length);
        for (let i = 0; i < bytes.length; i++) {
            decryptedBytes[i] = bytes[i] ^ keyBytes[i];
        }
        const decoder = new TextDecoder('utf-8');
        const jsonStr = decoder.decode(decryptedBytes);
        return JSON.parse(jsonStr);
    } catch (e) {
        return null;
    }
}

function attemptLogin() {
    const password = document.getElementById('passwordInput').value.toUpperCase();
    const errorEl = document.getElementById('loginError');
    
    if (!password) {
        errorEl.textContent = '암호를 입력해주세요';
        errorEl.style.display = 'block';
        return;
    }
    
    const data = decrypt(ENCRYPTED_DATA, password);
    
    if (data && data.crypto) {
        decryptedData = data;
        sessionStorage.setItem('dashboardAuth', password);
        showDashboard();
    } else {
        errorEl.textContent = '암호가 올바르지 않습니다';
        errorEl.style.display = 'block';
        document.getElementById('passwordInput').value = '';
        document.getElementById('passwordInput').focus();
    }
}

function checkSavedAuth() {
    const saved = sessionStorage.getItem('dashboardAuth');
    if (saved) {
        const data = decrypt(ENCRYPTED_DATA, saved);
        if (data && data.crypto) {
            decryptedData = data;
            showDashboard();
            return true;
        }
    }
    return false;
}

function logout() {
    sessionStorage.removeItem('dashboardAuth');
    decryptedData = null;
    document.getElementById('loginScreen').style.display = 'flex';
    document.getElementById('dashboard').style.display = 'none';
}

function showDashboard() {
    document.getElementById('loginScreen').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';
    renderAll();
}

function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    if (currentTheme === 'light') {
        body.removeAttribute('data-theme');
        localStorage.setItem('theme', 'dark');
    } else {
        body.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
    }
    if (currentChart) updateChartColors();
}

function loadTheme() {
    const saved = localStorage.getItem('theme') || 'dark';
    if (saved === 'light') document.body.setAttribute('data-theme', 'light');
}

function updateChartColors() {
    const isLight = document.body.getAttribute('data-theme') === 'light';
    const textColor = isLight ? '#1a1a2e' : '#fff';
    const gridColor = isLight ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.1)';
    if (currentChart) {
        currentChart.options.scales.x.ticks.color = textColor;
        currentChart.options.scales.y.ticks.color = textColor;
        currentChart.options.scales.x.grid.color = gridColor;
        currentChart.options.scales.y.grid.color = gridColor;
        currentChart.update();
    }
}

function toggleSection(id) {
    document.getElementById(id).classList.toggle('collapsed');
}

function renderAll() {
    if (!decryptedData) return;
    renderCalendar();
    renderFutures();
    renderChartTabs();
    renderCrypto();
    renderIndices();
    renderFearGreed();
    renderAnalysis();
}

const indicatorInfo = {
    'PPI': {
        desc: '생산자물가지수(PPI)는 생산자가 판매하는 상품과 서비스의 가격 변동을 측정합니다.',
        why: '연준(Fed)의 금리 결정에 직접적 영향을 미치며, 기업 수익성과 향후 소비자물가 방향을 예측하는 핵심 지표입니다.',
        bullish: '달러 강세, 금리 인상 기대감 상승, 주식시장 단기 하락 가능, 크립토 약세',
        bearish: '달러 약세, 금리 인하 기대감 상승, 주식시장 호재, 크립토 강세'
    },
    'PMI': {
        desc: '구매관리자지수(PMI)는 제조업/서비스업의 경기 상황을 나타내는 선행지표입니다. 50 이상이면 경기 확장, 50 미만이면 경기 수축을 의미합니다.',
        why: '경기 흐름을 가장 빠르게 반영하는 지표로, GDP 성장률을 예측하는 데 핵심적인 역할을 합니다.',
        bullish: '경제 성장 기대, 위험자산 선호, 주식/크립토 강세',
        bearish: '경기 침체 우려, 안전자산 선호, 달러/금/채권 강세'
    },
    'CPI': {
        desc: '소비자물가지수(CPI)는 가계가 구매하는 상품과 서비스의 가격 변동을 측정합니다.',
        why: '연준의 통화정책 결정에 가장 중요한 지표이며, 금리와 모든 자산 가격에 직접적 영향을 미칩니다.',
        bullish: '금리 인상 → 달러 강세, 주식/크립토 약세',
        bearish: '금리 인하 기대 → 달러 약세, 주식/크립토 강세'
    },
    '고용': {
        desc: '비농업 고용지표(NFP)는 미국 노동시장의 건강 상태를 나타냅니다.',
        why: '연준의 두 가지 목표 중 하나인 완전고용을 직접 측정하는 지표입니다.',
        bullish: '경제 강세 신호, 금리 인상 가능성, 달러 강세',
        bearish: '경기 둔화 우려, 금리 인하 기대, 위험자산 약세'
    },
    'FOMC': {
        desc: 'FOMC는 미국의 기준금리와 통화정책을 결정하는 연준의 핵심 의사결정 기구입니다.',
        why: '전 세계 금융시장의 방향을 결정짓는 가장 중요한 이벤트입니다.',
        bullish: '금리 인상/매파적 발언 → 달러 강세, 주식/크립토 약세',
        bearish: '금리 인하/비둘기파적 발언 → 달러 약세, 주식/크립토 강세'
    }
};

function getIndicatorInfo(name) {
    for (const kw of Object.keys(indicatorInfo)) {
        if (name.includes(kw)) return indicatorInfo[kw];
    }
    return {
        desc: '이 지표는 미국 경제의 특정 부문을 측정하는 중요한 경제 데이터입니다.',
        why: '시장 참여자들이 주목하는 핵심 지표로, 연준의 통화정책과 자산 가격에 영향을 미칩니다.',
        bullish: '예상보다 강한 수치 → 경제 낙관론',
        bearish: '예상보다 약한 수치 → 경제 비관론'
    };
}

function openCalendarModal(idx) {
    const item = decryptedData.economic_calendar[idx];
    if (!item) return;
    const info = getIndicatorInfo(item.event);
    document.getElementById('modalTitle').textContent = '⭐⭐⭐ ' + item.event;
    document.getElementById('modalTime').textContent = item.date + ' ' + item.time;
    document.getElementById('modalForecast').textContent = item.forecast || '-';
    document.getElementById('modalPrevious').textContent = item.previous || '-';
    document.getElementById('modalDesc').textContent = item.description || info.desc;
    let interpret = '';
    if (item.forecast && item.forecast !== '-' && item.previous && item.previous !== '-') {
        const f = parseFloat(item.forecast.replace(/[^0-9.-]/g, ''));
        const p = parseFloat(item.previous.replace(/[^0-9.-]/g, ''));
        if (!isNaN(f) && !isNaN(p)) {
            interpret = f > p ? '예측치가 이전치보다 높습니다.' : f < p ? '예측치가 이전치보다 낮습니다.' : '예측치가 이전치와 동일합니다.';
        }
    }
    document.getElementById('modalInterpret').textContent = interpret || '데이터 확인 중';
    document.getElementById('modalBullish').textContent = info.bullish;
    document.getElementById('modalBearish').textContent = info.bearish;
    document.getElementById('modalWhy').textContent = info.why;
    document.getElementById('calendarModal').classList.add('active');
}

function closeModal() {
    document.getElementById('calendarModal').classList.remove('active');
}

function renderCalendar() {
    const cal = decryptedData.economic_calendar || [];
    const tbody = document.getElementById('calendarBody');
    if (!cal.length) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:2rem;">예정된 경제지표가 없습니다</td></tr>';
        return;
    }
    const now = new Date();
    const kst = new Date(now.getTime() + 9*60*60000);
    const todayStr = (kst.getMonth()+1) + '/' + kst.getDate();
    tbody.innerHTML = cal.map((item, idx) => {
        const imp = item.importance === 'high' ? '⭐⭐⭐' : '⭐⭐';
        const isNext = item.date !== todayStr;
        const bg = isNext ? 'background:rgba(255,255,255,0.03);' : '';
        return '<tr style="'+bg+'" onclick="openCalendarModal('+idx+')"><td>'+item.date+'</td><td class="event-time">'+item.time+'</td><td>'+item.event+'</td><td>'+(item.forecast||'-')+'</td><td>'+(item.previous||'-')+'</td><td style="color:var(--yellow)">'+imp+'</td></tr>';
    }).join('');
}

function renderFutures() {
    const f = decryptedData.futures_data || {};
    if (f.long_short_ratio) {
        const ls = f.long_short_ratio;
        document.getElementById('lsRatio').textContent = ls.ratio.toFixed(2);
        document.getElementById('lsDetail').textContent = '롱 '+ls.long.toFixed(1)+'% / 숏 '+ls.short.toFixed(1)+'%';
        document.getElementById('longBar').style.width = ls.long+'%';
        document.getElementById('longBar').textContent = '롱 '+ls.long.toFixed(1)+'%';
        document.getElementById('shortBar').style.width = ls.short+'%';
        document.getElementById('shortBar').textContent = '숏 '+ls.short.toFixed(1)+'%';
    }
    if (f.funding_rate !== null && f.funding_rate !== undefined) {
        const fr = f.funding_rate;
        document.getElementById('fundingRate').textContent = (fr>=0?'+':'')+fr.toFixed(4)+'%';
        document.getElementById('fundingRate').style.color = fr>=0?'var(--green)':'var(--red)';
        document.getElementById('fundingDesc').textContent = fr>=0?'롱이 숏에게 지불':'숏이 롱에게 지불';
    }
    if (f.open_interest) {
        document.getElementById('openInterest').textContent = f.open_interest.toLocaleString()+' BTC';
    }
    if (f.funding_rates && f.funding_rates.length) {
        document.getElementById('fundingTable').innerHTML = '<tr>'+f.funding_rates.map(x => {
            const c = x.rate>=0?'var(--green)':'var(--red)';
            return '<td><div class="symbol">'+x.symbol+'</div><div style="color:'+c+'">'+(x.rate>=0?'+':'')+x.rate.toFixed(4)+'%</div></td>';
        }).join('')+'</tr>';
    }
}

function renderChartTabs() {
    const crypto = decryptedData.crypto || [];
    const tabs = document.getElementById('chartTabs');
    const btc = crypto.find(c => c.symbol === 'BTC') || {change: 0};
    tabs.innerHTML = crypto.slice(0,5).map((c,i) => {
        const cls = i===0?'chart-tab active':'chart-tab';
        const chg = c.change>=0?'positive':'negative';
        return '<button class="'+cls+'" onclick="selectChart(\\''+c.symbol+'\\')">'+c.symbol+'<span class="change '+chg+'">'+(c.change>=0?'+':'')+c.change.toFixed(2)+'%</span></button>';
    }).join('');
    drawChart('BTC');
}

function selectChart(symbol) {
    document.querySelectorAll('.chart-tab').forEach(t => t.classList.remove('active'));
    event.target.closest('.chart-tab').classList.add('active');
    drawChart(symbol);
}

function drawChart(symbol) {
    const history = decryptedData.btc_history || {labels:[],prices:[]};
    const ctx = document.getElementById('mainChart').getContext('2d');
    const isLight = document.body.getAttribute('data-theme') === 'light';
    const textColor = isLight ? '#1a1a2e' : '#fff';
    const gridColor = isLight ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.1)';
    if (currentChart) currentChart.destroy();
    const crypto = decryptedData.crypto.find(c => c.symbol === symbol);
    const color = crypto && crypto.change >= 0 ? '#2ed573' : '#ff4757';
    currentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: history.labels,
            datasets: [{
                label: symbol + ' 가격',
                data: history.prices,
                borderColor: color,
                backgroundColor: color + '20',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {legend:{display:false}},
            scales: {
                x: {ticks:{color:textColor,maxTicksLimit:6},grid:{color:gridColor}},
                y: {ticks:{color:textColor},grid:{color:gridColor}}
            }
        }
    });
}

function renderCrypto() {
    const crypto = decryptedData.crypto || [];
    const grid = document.getElementById('cryptoGrid');
    grid.innerHTML = crypto.map(c => {
        const cls = c.change >= 0 ? 'up' : 'down';
        return '<div class="crypto-card '+cls+'"><div class="crypto-symbol">'+c.symbol+'</div><div class="crypto-name">'+c.name+'</div><div class="crypto-price">$'+c.price.toLocaleString()+'</div><div class="crypto-change">'+(c.change>=0?'+':'')+c.change.toFixed(2)+'%</div></div>';
    }).join('');
}

function renderIndices() {
    const us = decryptedData.us_indices || [];
    const kr = decryptedData.kr_indices || [];
    document.getElementById('indicesTable').innerHTML = us.map(i => {
        const cls = i.change >= 0 ? 'positive' : 'negative';
        return '<tr><td>'+i.name+'</td><td>'+i.price.toLocaleString()+'</td><td class="'+cls+'">'+(i.change>=0?'+':'')+i.change.toFixed(2)+'%</td></tr>';
    }).join('');
    document.getElementById('krTable').innerHTML = kr.map(i => {
        const cls = i.change >= 0 ? 'positive' : 'negative';
        return '<tr><td>'+i.name+'</td><td>'+i.price.toLocaleString()+'</td><td class="'+cls+'">'+(i.change>=0?'+':'')+i.change.toFixed(2)+'%</td></tr>';
    }).join('');
}

function renderFearGreed() {
    const fg = decryptedData.fear_greed || {value: 50};
    const val = fg.value;
    document.getElementById('fgValue').textContent = val;
    const label = val <= 25 ? '극도의 공포' : val <= 45 ? '공포' : val <= 55 ? '중립' : val <= 75 ? '탐욕' : '극도의 탐욕';
    const cls = val <= 45 ? 'fear' : val <= 55 ? 'neutral' : 'greed';
    document.getElementById('fgLabel').textContent = label;
    document.getElementById('fgLabel').className = 'fg-label ' + cls;
    
    const canvas = document.getElementById('fgGauge');
    const ctx = canvas.getContext('2d');
    const size = 140;
    canvas.width = size;
    canvas.height = size;
    const center = size / 2;
    const radius = 55;
    ctx.clearRect(0, 0, size, size);
    ctx.beginPath();
    ctx.arc(center, center, radius, 0.75 * Math.PI, 0.25 * Math.PI);
    ctx.strokeStyle = '#2a2a3a';
    ctx.lineWidth = 12;
    ctx.lineCap = 'round';
    ctx.stroke();
    const gradient = ctx.createLinearGradient(0, 0, size, 0);
    gradient.addColorStop(0, '#ff4757');
    gradient.addColorStop(0.5, '#ffa502');
    gradient.addColorStop(1, '#2ed573');
    ctx.beginPath();
    const endAngle = 0.75 * Math.PI + (val / 100) * 1.5 * Math.PI;
    ctx.arc(center, center, radius, 0.75 * Math.PI, endAngle);
    ctx.strokeStyle = gradient;
    ctx.lineWidth = 12;
    ctx.lineCap = 'round';
    ctx.stroke();
}

function renderAnalysis() {
    const analysis = decryptedData.analysis || {};
    document.getElementById('globalAnalysis').innerHTML = analysis.global_analysis || '<p>분석 데이터 없음</p>';
    document.getElementById('predictionAnalysis').innerHTML = analysis.prediction_analysis || '<p>분석 데이터 없음</p>';
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeModal();
    if (e.key === 'Enter' && document.getElementById('loginScreen').style.display !== 'none') attemptLogin();
    
    // 개발자 도구 차단
    if (e.key === 'F12') { e.preventDefault(); return false; }
    if (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'i')) { e.preventDefault(); return false; }
    if (e.ctrlKey && e.shiftKey && (e.key === 'J' || e.key === 'j')) { e.preventDefault(); return false; }
    if (e.ctrlKey && e.shiftKey && (e.key === 'C' || e.key === 'c')) { e.preventDefault(); return false; }
    if (e.ctrlKey && (e.key === 'U' || e.key === 'u')) { e.preventDefault(); return false; }
});

// 오른쪽 클릭 차단
document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
    return false;
});

// 텍스트 선택 차단
document.addEventListener('selectstart', function(e) {
    if (e.target.tagName !== 'INPUT') {
        e.preventDefault();
        return false;
    }
});

// 드래그 차단
document.addEventListener('dragstart', function(e) {
    e.preventDefault();
    return false;
});

document.getElementById('calendarModal').addEventListener('click', function(e) {
    if (e.target === this) closeModal();
});

loadTheme();
if (!checkSavedAuth()) {
    document.getElementById('loginScreen').style.display = 'flex';
}
'''

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
[data-theme="light"]{{--bg-primary:#f5f5f7;--bg-secondary:#ffffff;--bg-card:#ffffff;--border:#e0e0e0;--text:#1a1a2e;--text-secondary:#6b6b80}}
[data-theme="light"] .section{{box-shadow:0 2px 12px rgba(0,0,0,0.08)}}
[data-theme="light"] .crypto-card{{box-shadow:0 2px 8px rgba(0,0,0,0.06)}}
[data-theme="light"] .modal{{box-shadow:0 4px 24px rgba(0,0,0,0.15)}}
body{{font-family:'Noto Sans KR',sans-serif;background:var(--bg-primary);color:var(--text);line-height:1.6;transition:background 0.3s,color 0.3s}}

/* 로그인 화면 */
.login-screen{{position:fixed;top:0;left:0;right:0;bottom:0;background:var(--bg-primary);display:none;justify-content:center;align-items:center;z-index:9999}}
.login-box{{background:var(--bg-card);border:1px solid var(--border);border-radius:20px;padding:3rem;max-width:400px;width:90%;text-align:center}}
.login-logo{{font-size:3rem;margin-bottom:1rem}}
.login-title{{font-size:1.5rem;font-weight:700;margin-bottom:0.5rem}}
.login-subtitle{{color:var(--text-secondary);margin-bottom:2rem;font-size:0.9rem}}
.login-input{{width:100%;padding:1rem;font-size:1.1rem;background:var(--bg-secondary);border:2px solid var(--border);border-radius:12px;color:var(--text);text-align:center;letter-spacing:0.3rem;font-weight:700;margin-bottom:1rem}}
.login-input:focus{{outline:none;border-color:var(--blue)}}
.login-input::placeholder{{letter-spacing:normal;font-weight:400}}
.login-btn{{width:100%;padding:1rem;font-size:1rem;font-weight:700;background:linear-gradient(135deg,#667eea,#764ba2);border:none;border-radius:12px;color:#fff;cursor:pointer;transition:transform 0.2s,box-shadow 0.2s}}
.login-btn:hover{{transform:translateY(-2px);box-shadow:0 4px 15px rgba(102,126,234,0.4)}}
.login-error{{color:var(--red);margin-top:1rem;font-size:0.9rem;display:none}}

/* 헤더 */
.header{{background:var(--bg-secondary);padding:1rem 2rem;border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100}}
.header-content{{max-width:1400px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem}}
.header-left{{display:flex;align-items:center;gap:1.5rem}}
.logo{{font-size:1.5rem;font-weight:900;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.update-time{{color:var(--text-secondary);font-size:0.85rem;display:flex;align-items:center;gap:0.5rem}}
.live-dot{{width:8px;height:8px;background:var(--green);border-radius:50%;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.5}}}}
.header-right{{display:flex;align-items:center;gap:1rem}}
.theme-toggle{{background:var(--bg-card);border:1px solid var(--border);border-radius:50px;padding:0.4rem;display:flex;align-items:center;gap:0.25rem;cursor:pointer}}
.theme-toggle span{{width:32px;height:32px;display:flex;align-items:center;justify-content:center;border-radius:50%;font-size:1.1rem;transition:all 0.3s}}
.theme-toggle .sun{{background:transparent}}
.theme-toggle .moon{{background:var(--blue);box-shadow:0 2px 8px rgba(55,66,250,0.4)}}
[data-theme="light"] .theme-toggle .sun{{background:var(--orange);box-shadow:0 2px 8px rgba(255,165,2,0.4)}}
[data-theme="light"] .theme-toggle .moon{{background:transparent;box-shadow:none}}
.logout-btn{{background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:0.5rem 1rem;color:var(--text-secondary);font-size:0.85rem;cursor:pointer;transition:all 0.2s}}
.logout-btn:hover{{border-color:var(--red);color:var(--red)}}

/* 메인 콘텐츠 */
.container{{max-width:1400px;margin:0 auto;padding:2rem}}
.section{{background:var(--bg-card);border:1px solid var(--border);border-radius:16px;margin-bottom:1.5rem;overflow:hidden}}
.section-header{{display:flex;justify-content:space-between;align-items:center;padding:1.25rem 1.5rem;cursor:pointer;border-bottom:1px solid var(--border)}}
.section-header:hover{{background:rgba(255,255,255,0.02)}}
.section-title{{font-size:1.1rem;font-weight:700;display:flex;align-items:center;gap:0.75rem}}
.section-title::before{{content:'';width:4px;height:20px;background:var(--red);border-radius:2px}}
.section-title.blue::before{{background:var(--blue)}}
.section-title.green::before{{background:var(--green)}}
.section-title.yellow::before{{background:var(--yellow)}}
.section-title.orange::before{{background:var(--orange)}}
.toggle-btn{{color:var(--text-secondary);font-size:0.85rem}}
.section.collapsed .toggle-btn{{transform:rotate(180deg)}}
.section-content{{padding:1.5rem}}
.section.collapsed .section-content{{display:none}}

/* 테이블 */
.table,.calendar-table{{width:100%;border-collapse:collapse}}
.table th,.table td,.calendar-table th,.calendar-table td{{padding:0.75rem 1rem;text-align:left;border-bottom:1px solid var(--border)}}
.table th,.calendar-table th{{background:var(--bg-secondary);font-weight:600;font-size:0.85rem;color:var(--text-secondary)}}
.calendar-table tbody tr{{cursor:pointer;transition:all 0.2s}}
.calendar-table tbody tr:hover{{background:rgba(55,66,250,0.15);transform:scale(1.01)}}
.event-time{{color:var(--blue);font-weight:600}}
.positive{{color:var(--green)}}
.negative{{color:var(--red)}}

/* 암호화폐 카드 */
.crypto-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1rem}}
.crypto-card{{padding:1.25rem;border-radius:12px;text-align:center}}
.crypto-card.up{{background:linear-gradient(135deg,rgba(46,213,115,0.15),rgba(46,213,115,0.05));border:1px solid rgba(46,213,115,0.3)}}
.crypto-card.down{{background:linear-gradient(135deg,rgba(255,71,87,0.15),rgba(255,71,87,0.05));border:1px solid rgba(255,71,87,0.3)}}
.crypto-symbol{{font-size:1.25rem;font-weight:900}}
.crypto-name{{font-size:0.75rem;color:var(--text-secondary)}}
.crypto-price{{font-size:0.9rem;color:var(--text-secondary)}}
.crypto-change{{font-weight:700;font-size:1.1rem}}
.crypto-card.up .crypto-change{{color:var(--green)}}
.crypto-card.down .crypto-change{{color:var(--red)}}

/* 공포탐욕 */
.fear-greed-container{{display:flex;align-items:center;gap:2rem;background:var(--bg-secondary);padding:1.5rem;border-radius:12px;margin-top:1.5rem}}
.fg-gauge{{position:relative;width:140px;height:140px}}
.fg-value{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:2.5rem;font-weight:900}}
.fg-info h4{{font-size:1.25rem;margin-bottom:0.5rem}}
.fg-label{{display:inline-block;padding:0.35rem 1rem;border-radius:20px;font-size:0.85rem;font-weight:600;margin-top:0.75rem}}
.fg-label.fear{{background:rgba(255,71,87,0.2);color:var(--red)}}
.fg-label.neutral{{background:rgba(138,138,154,0.2);color:var(--text-secondary)}}
.fg-label.greed{{background:rgba(255,165,2,0.2);color:var(--yellow)}}

/* 차트 */
.chart-tabs{{display:flex;gap:0.5rem;margin-bottom:1rem;flex-wrap:wrap}}
.chart-tab{{padding:0.6rem 1.2rem;background:var(--bg-secondary);border:1px solid var(--border);border-radius:8px;color:var(--text-secondary);font-size:0.9rem;font-weight:500;cursor:pointer}}
.chart-tab:hover{{border-color:var(--blue);color:var(--text)}}
.chart-tab.active{{background:var(--blue);border-color:var(--blue);color:#fff}}
.chart-tab .change{{font-size:0.75rem;margin-left:0.5rem}}
.chart-tab .change.positive{{color:var(--green)}}
.chart-tab .change.negative{{color:var(--red)}}
.chart-tab.active .change{{color:rgba(255,255,255,0.9)}}
.chart-container{{position:relative;height:350px;margin-bottom:1rem}}

/* 선물 */
.futures-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem}}
.futures-card{{background:var(--bg-secondary);border-radius:12px;padding:1.25rem;text-align:center}}
.futures-card h5{{color:var(--text-secondary);font-size:0.8rem;margin-bottom:0.5rem}}
.futures-card .value{{font-size:1.5rem;font-weight:700}}
.futures-card .sub{{font-size:0.8rem;color:var(--text-secondary);margin-top:0.25rem}}
.long-short-bar{{display:flex;height:30px;border-radius:6px;overflow:hidden;margin:1rem 0}}
.long-bar{{background:linear-gradient(90deg,#2ed573,#7bed9f);display:flex;align-items:center;justify-content:center;color:#000;font-weight:600;font-size:0.8rem}}
.short-bar{{background:linear-gradient(90deg,#ff6b81,#ff4757);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:600;font-size:0.8rem}}
.funding-table{{width:100%;margin-top:1rem}}
.funding-table td{{padding:0.5rem;text-align:center;border-bottom:1px solid var(--border)}}
.funding-table .symbol{{font-weight:700}}

/* 분석 */
.grid-2{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1.5rem}}
.analysis-content{{color:var(--text-secondary);font-size:0.95rem}}
.analysis-content h3{{color:var(--text);font-size:1rem;font-weight:700;margin:1.5rem 0 0.75rem;display:flex;align-items:center;gap:0.5rem}}
.analysis-content h3:first-child{{margin-top:0}}
.analysis-content h3::before{{content:'▸';color:var(--blue)}}
.analysis-content p{{margin-bottom:1rem;line-height:1.8}}

/* 모달 */
.modal-overlay{{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.8);display:none;justify-content:center;align-items:center;z-index:1000;padding:1rem}}
.modal-overlay.active{{display:flex}}
.modal{{background:var(--bg-card);border:1px solid var(--border);border-radius:16px;max-width:500px;width:100%;max-height:80vh;overflow-y:auto}}
.modal-header{{padding:1.25rem 1.5rem;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}}
.modal-header h3{{font-size:1.1rem;font-weight:700;color:var(--yellow)}}
.modal-close{{background:none;border:none;color:var(--text-secondary);font-size:1.5rem;cursor:pointer}}
.modal-body{{padding:1.5rem}}
.modal-section{{margin-bottom:1.25rem}}
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

.footer{{text-align:center;padding:2rem;color:var(--text-secondary);font-size:0.85rem;border-top:1px solid var(--border);margin-top:2rem}}

@media(max-width:768px){{
.container{{padding:1rem}}
.header-content{{justify-content:center;text-align:center}}
.fear-greed-container{{flex-direction:column;text-align:center}}
.crypto-grid{{grid-template-columns:repeat(2,1fr)}}
.futures-grid{{grid-template-columns:1fr}}
.grid-2{{grid-template-columns:1fr}}
.login-box{{padding:2rem}}
}}
</style>
</head>
<body>

<!-- 로그인 화면 -->
<div class="login-screen" id="loginScreen">
<div class="login-box">
<div class="login-logo">🔐</div>
<h1 class="login-title">AI 마켓 대시보드</h1>
<p class="login-subtitle">유료 회원 전용 서비스입니다</p>
<input type="text" id="passwordInput" class="login-input" placeholder="오늘의 암호 입력" maxlength="6" autocomplete="off">
<button class="login-btn" onclick="attemptLogin()">접속하기</button>
<p class="login-error" id="loginError"></p>
</div>
</div>

<!-- 대시보드 -->
<div id="dashboard" style="display:none;">
<header class="header">
<div class="header-content">
<div class="header-left">
<div class="logo">🚀 AI 마켓 대시보드</div>
<div class="update-time"><span class="live-dot"></span>{updated_at}</div>
</div>
<div class="header-right">
<div class="theme-toggle" onclick="toggleTheme()" title="테마 변경">
<span class="sun">☀️</span>
<span class="moon">🌙</span>
</div>
<button class="logout-btn" onclick="logout()">로그아웃</button>
</div>
</div>
</header>

<main class="container">

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

<section class="section" id="futuresSection">
<div class="section-header" onclick="toggleSection('futuresSection')">
<h2 class="section-title blue">⚡ BTC 선물 데이터</h2>
<span class="toggle-btn">▲</span>
</div>
<div class="section-content">
<div class="futures-grid">
<div class="futures-card"><h5>롱/숏 비율</h5><div class="value" id="lsRatio">-</div><div class="sub" id="lsDetail">-</div></div>
<div class="futures-card"><h5>펀딩비 (8H)</h5><div class="value" id="fundingRate">-</div><div class="sub" id="fundingDesc">-</div></div>
<div class="futures-card"><h5>미결제약정</h5><div class="value" id="openInterest">-</div><div class="sub">Open Interest</div></div>
</div>
<div class="long-short-bar"><div class="long-bar" id="longBar" style="width:50%">롱 50%</div><div class="short-bar" id="shortBar" style="width:50%">숏 50%</div></div>
<table class="funding-table" id="fundingTable"></table>
</div>
</section>

<section class="section" id="analysisSection">
<div class="section-header" onclick="toggleSection('analysisSection')">
<h2 class="section-title yellow">🤖 AI 시장 분석</h2>
<span class="toggle-btn">▲</span>
</div>
<div class="section-content">
<div class="grid-2">
<div class="analysis-content" id="globalAnalysis"></div>
<div class="analysis-content" id="predictionAnalysis"></div>
</div>
</div>
</section>

<section class="section" id="cryptoSection">
<div class="section-header" onclick="toggleSection('cryptoSection')">
<h2 class="section-title green">💰 암호화폐</h2>
<span class="toggle-btn">▲</span>
</div>
<div class="section-content">
<div class="crypto-grid" id="cryptoGrid"></div>
<div class="fear-greed-container">
<div class="fg-gauge"><canvas id="fgGauge"></canvas><div class="fg-value" id="fgValue">50</div></div>
<div class="fg-info">
<h4>공포 & 탐욕 지수</h4>
<p>시장 심리를 나타내는 종합 지표</p>
<span class="fg-label" id="fgLabel">중립</span>
</div>
</div>
</div>
</section>

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
</div>

<!-- 모달 -->
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
<div class="modal-section"><h4>📊 지표 설명</h4><p id="modalDesc">-</p></div>
<div class="modal-section"><h4>🎯 예측치 해석</h4><p id="modalInterpret">-</p></div>
<div class="modal-section">
<h4>📈 시나리오 분석</h4>
<div class="scenario-box bullish"><div class="scenario-label">🟢 예측치 상회 시</div><div id="modalBullish">-</div></div>
<div class="scenario-box bearish"><div class="scenario-label">🔴 예측치 하회 시</div><div id="modalBearish">-</div></div>
</div>
<div class="modal-section"><h4>⭐ 중요도가 높은 이유</h4><p id="modalWhy">-</p></div>
</div>
</div>
</div>

<script>{obfuscate_js(app_js)}</script>
</body>
</html>'''

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("done - encrypted build complete")

if __name__ == "__main__":
    main()
