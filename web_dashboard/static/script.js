document.addEventListener('DOMContentLoaded', () => {
    fetchData();
});

function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    
    event.currentTarget.classList.add('active');
    document.getElementById('tab-' + tabId).classList.add('active');
}

async function fetchData() {
    try {
        const response = await fetch('/api/data');
        const res = await response.json();
        
        if (res.need_analysis) {
            document.getElementById('loading-screen').style.display = 'none';
            document.getElementById('welcome-screen').style.display = 'flex';
        } else {
            document.getElementById('loading-screen').style.display = 'none';
            document.getElementById('welcome-screen').style.display = 'none';
            document.getElementById('dashboard').style.display = 'block';
            renderDashboard(res.data);
        }
    } catch (error) {
        console.error("Veri çekilemedi:", error);
    }
}

async function runAnalysis() {
    document.getElementById('welcome-screen').style.display = 'none';
    document.getElementById('dashboard').style.display = 'none';
    document.getElementById('loading-screen').style.display = 'flex';
    
    try {
        const response = await fetch('/api/run_analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        const data = await response.json();
        
        document.getElementById('loading-screen').style.display = 'none';
        document.getElementById('dashboard').style.display = 'block';
        
        if (data.error) {
            alert("Hata: " + data.error);
        } else {
            renderDashboard(data);
        }
    } catch (e) {
        alert("Bağlantı koptu veya zaman aşımı: " + e);
        window.location.reload();
    }
}

async function runAnalysisWithCustom() {
    const sDate = document.getElementById('sim-start').value;
    const eDate = document.getElementById('sim-end').value;
    const targets = document.getElementById('sim-targets').value;
    const days = document.getElementById('sim-days').value;
    
    const payload = {};
    if (sDate) payload.start_date = sDate;
    if (eDate) payload.end_date = eDate;
    
    // Basit parametre desteği
    if (targets) payload.custom_targets = targets;
    if (days) payload.custom_days = days;
    payload.custom_slots = "6,7"; 
    payload.custom_stops = "6,8,10,15";
    payload.custom_trails = "5,6,8,10,12";
    
    document.getElementById('dashboard').style.display = 'none';
    document.getElementById('loading-screen').style.display = 'flex';
    
    try {
        const response = await fetch('/api/run_analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        
        document.getElementById('loading-screen').style.display = 'none';
        document.getElementById('dashboard').style.display = 'block';
        
        if (data.error) {
            alert("Hata: " + data.error);
        } else {
            renderDashboard(data);
        }
    } catch (e) {
        alert("Bağlantı koptu: " + e);
    }
}

async function syncTelegram() {
    const fromDate = document.getElementById('tg-date').value;
    const btn = event.currentTarget;
    const statusText = document.getElementById('tg-status');
    
    btn.innerText = "⏳ BAĞLANILIYOR VE ÇEKİLİYOR...";
    btn.disabled = true;
    statusText.innerText = "Telegram API'ye bağlanılıyor. Bu işlem birkaç saniye sürebilir...\n(Eğer ilk kez çalıştırıyorsanız terminali [komut ekranını] kontrol edin, telefon onayı isteyebilir!)";
    
    try {
        const response = await fetch('/api/sync_telegram', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ from_date: fromDate })
        });
        const data = await response.json();
        
        if (data.success) {
            statusText.innerHTML = `<span style="color:var(--success-color)">✅ Başarılı!</span> Sinyaller hissetakip eklendi.<br><br><b>Konsol Çıktısı:</b><br>${data.output.replace(/\\n/g, '<br>')}`;
            btn.innerText = "✅ ÇEKİM TAMAMLANDI";
            setTimeout(() => { btn.innerText = "📥 TEKRAR VERİ ÇEK"; btn.disabled = false; }, 3000);
        } else {
            statusText.innerHTML = `<span style="color:var(--danger-color)">❌ Başarısız:</span><br>${data.error}<br>${data.output}`;
            btn.innerText = "❌ HATA OLUŞTU";
            btn.disabled = false;
        }
    } catch (e) {
        statusText.innerText = "Kritik Bağlantı Hatası: " + e;
        btn.disabled = false;
        btn.innerText = "📥 TEKRAR VERİ ÇEK";
    }
}

function renderDashboard(data) {
    const meta = data.meta;
    const islemler = data.islemler;
    
    document.getElementById('ai-text').innerHTML = `
        <h3>AI MİNİMAX KARARI: <span class="gradient-text">${meta.tavsiye_baslik}</span></h3>
        <p>Bütün ihtimaller on binlerce kez tarandı. Tüm şanssızlıkları (sinyal kaçma vb.) yaşadığın <b>En Kötü Senaryo Stres Testinde BİLE</b> en çok kâr bırakan strateji budur:
        <strong>Senin için ${meta.yakalanan_hisse} hisseyi dipten yakalayan</strong> 
        bu strateji ile ilerlemelisin. <strong>%${meta.strateji.kar_hedefi} Kar, %${meta.strateji.stop_loss} Stop, %${meta.strateji.trailing_stop} Takip Eden Limit</strong> ile ${meta.strateji.max_gun} gün bekletmelisin.</p>
        <small style="color:#666">Son Analiz: ${meta.analiz_tarihi} ${meta.is_custom ? '(Özel Ayarlar)' : ''}</small>
    `;

    const kpiContainer = document.getElementById('kpi-container');
    kpiContainer.innerHTML = `
        <div class="kpi-card glass-panel border-bottom-glow">
            <span class="kpi-label">📈 İdeal Sermaye (Tüm Sinyaller)</span>
            <span class="kpi-value">${formatMoney(meta.final_sermaye)} <small style="color:var(--success-color);font-size:1rem;">(%+${meta.toplam_getiri})</small></span>
        </div>
        <div class="kpi-card glass-panel">
            <span class="kpi-label">🎯 İdeal İşlem Başarısı</span>
            <span class="kpi-value">${meta.basarili_islem} / ${meta.toplam_islem} <small style="color:var(--accent-secondary);font-size:1rem;">(%${meta.basari_orani})</small></span>
        </div>
        <div class="kpi-card glass-panel border-red-glow" style="border-left: 4px solid var(--warning-color)">
            <span class="kpi-label">⚠️ DİP STRES TESTİ (Karantina)</span>
            <span class="kpi-value text-red" style="font-size:1.5rem">${formatMoney(meta.stres_min)} <small style="font-size:0.8rem;color:#888"> (Zemindeki En Kötü Senaryo)</small></span>
        </div>
    `;

    const tbody = document.querySelector('#history-table tbody');
    tbody.innerHTML = '';
    
    islemler.forEach(islem => {
        const isGreen = islem.kar_orani > 0;
        const colorClass = isGreen ? 'text-green' : 'text-red';
        const sign = isGreen ? '+' : '';
        
        tbody.innerHTML += `
            <tr>
                <td><strong>${islem.hisse}</strong></td>
                <td>${islem.alis_tarihi}</td>
                <td>${(islem.alis_fiyati || 0).toFixed(2)} TL</td>
                <td>${islem.cikis_tarihi}</td>
                <td>${(islem.cikis_fiyati || 0).toFixed(2)} TL</td>
                <td>${islem.gun_sayisi} Gün</td>
                <td class="${colorClass}"><strong>${sign}%${islem.kar_orani}</strong> (${sign}${islem.kar_tl} TL)</td>
                <td><span class="badge" style="background: rgba(255,255,255,0.1); color:#fff; font-weight:normal;">${islem.cikis_sebebi}</span></td>
            </tr>
        `;
    });

    const analyticsGrid = document.getElementById('analytics-grid');
    analyticsGrid.innerHTML = '';
    
    islemler.forEach(islem => {
        const maxCls = 'text-green';
        const minCls = 'text-red';

        analyticsGrid.innerHTML += `
            <div class="analytic-card glass-panel">
                <div class="stock-tag">${islem.hisse}</div>
                <div class="entry-line">
                    <div>
                        <small style="color:var(--text-secondary)">Giriş (Alış)</small>
                        <div style="font-size:1.1rem;font-weight:600">${(islem.alis_fiyati || 0).toFixed(2)} TL</div>
                        <small style="color:#666">${islem.alis_tarihi}</small>
                    </div>
                    <div style="text-align:right">
                        <small style="color:var(--text-secondary)">Sistemin Satışı</small>
                        <div style="font-size:1.1rem;font-weight:600;color:${islem.kar_orani>0?'var(--success-color)':'var(--danger-color)'}">${(islem.cikis_fiyati || 0).toFixed(2)} TL</div>
                        <span class="badge" style="background:rgba(255,255,255,0.1);color:#fff">${islem.cikis_sebebi}</span>
                    </div>
                </div>
                
                <div class="min-max-row bg-green-soft">
                    <div class="mm-label">
                        Alındıktan Sonra Gördüğü Maksimum Tepe
                        <strong class="${maxCls}">${(islem.max_fiyat || 0).toFixed(2)} TL (+%${islem.max_kar_orani})</strong>
                    </div>
                    <div class="mm-meta">
                        ${islem.max_tarih}<br>
                        <em>Alıştan ${islem.max_gun_sonra} gün sonra</em>
                    </div>
                </div>

                <div class="min-max-row bg-red-soft" style="margin-bottom:0.5rem">
                    <div class="mm-label">
                        Alındığı Dönemde Gördüğü Maksimum Dip
                        <strong class="${minCls}">${(islem.min_fiyat || 0).toFixed(2)} TL (%${islem.min_zarar_orani})</strong>
                    </div>
                    <div class="mm-meta">
                        ${islem.min_tarih}<br>
                        <em>Alıştan ${islem.min_gun_sonra} gün sonra</em>
                    </div>
                </div>
                
                <div class="entry-line" style="border-top: 1px solid rgba(255,255,255,0.05); padding-top: 0.5rem;">
                    <div>
                        <small style="color:var(--text-secondary)">Bugünkü Anlık Fiyat</small>
                    </div>
                    <div style="text-align:right">
                        <strong style="color:${islem.suanki_kar_orani>0?'var(--success-color)':'var(--danger-color)'}">${(islem.suanki_fiyat || 0).toFixed(2)} TL (%${islem.suanki_kar_orani > 0 ? '+':''}${islem.suanki_kar_orani})</strong>
                    </div>
                </div>
            </div>
        `;
    });
    
    // TAB 3: TÜM SİNYALLER RENDER
    const allSignalsGrid = document.getElementById('all-signals-grid');
    if (allSignalsGrid && data.tum_sinyaller) {
        allSignalsGrid.innerHTML = '';
        data.tum_sinyaller.forEach(islem => {
            const currentBadgeColor = islem.suanki_kar_orani > 0 ? 'var(--success-color)' : 'var(--danger-color)';
            allSignalsGrid.innerHTML += `
                <div class="analytic-card glass-panel" style="border-left: 3px solid ${currentBadgeColor}">
                    <div class="stock-tag">${islem.hisse} <span style="font-size:0.7rem; color:#888; font-weight:normal; margin-left:5px">${islem.kategori}</span></div>
                    <div class="entry-line">
                        <div>
                            <small style="color:var(--text-secondary)">Alış Fiyatı</small>
                            <div style="font-size:1.1rem;font-weight:600">${(islem.alis_fiyati || 0).toFixed(2)} TL</div>
                            <small style="color:#666">${islem.alis_tarihi}</small>
                        </div>
                        <div style="text-align:right">
                            <small style="color:var(--text-secondary)">BUGÜNKÜ FİYAT (Hiç Satılmasa)</small>
                            <div style="font-size:1.4rem;font-weight:bold;color:${currentBadgeColor}">${(islem.suanki_fiyat || 0).toFixed(2)} TL</div>
                            <strong style="color:${currentBadgeColor}">${islem.suanki_kar_orani > 0 ? '+':''}%${islem.suanki_kar_orani}</strong>
                        </div>
                    </div>
                    
                    <div class="min-max-row bg-green-soft">
                        <div class="mm-label">
                            Bugüne Kadar Gördüğü En Yüksek Tepe
                            <strong class="text-green">${(islem.max_fiyat || 0).toFixed(2)} TL (+%${islem.max_kar_orani})</strong>
                        </div>
                        <div class="mm-meta">
                            ${islem.max_tarih}<br>
                            <em>Alıştan ${islem.max_gun_sonra} gün sonra</em>
                        </div>
                    </div>

                    <div class="min-max-row bg-red-soft">
                        <div class="mm-label">
                            Bugüne Kadar Gördüğü En Kötü Dip
                            <strong class="text-red">${(islem.min_fiyat || 0).toFixed(2)} TL (%${islem.min_zarar_orani})</strong>
                        </div>
                        <div class="mm-meta">
                            ${islem.min_tarih}<br>
                            <em>Alıştan ${islem.min_gun_sonra} gün sonra</em>
                        </div>
                    </div>
                </div>
            `;
        });
    }
}

function formatMoney(amount) {
    return new Intl.NumberFormat('tr-TR', { maximumFractionDigits: 0 }).format(amount) + ' ₺';
}
