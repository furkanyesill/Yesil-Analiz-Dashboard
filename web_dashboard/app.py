import sys
import os
import json
import subprocess
from datetime import datetime
from flask import Flask, render_template, jsonify, request

# PYTHONPATH ayarlaması - hissetakip'in bulunduğu ana dizine erişim
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from hissetakip import UltimateOptimizedSimulator, ultimate_strateji_optimizasyonu, CATEGORY_LABELS, portfolio, signal_categories

app = Flask(__name__)

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json")

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def deep_analyze_trade(islem, history):
    import pandas as pd
    alis_tarihi = pd.Timestamp(islem['alis_tarihi'])
    cikis_tarihi = pd.Timestamp(islem['cikis_tarihi'])
    alis_fiyati = islem['alis_fiyati']
    
    if history.index.tz is not None:
        if alis_tarihi.tzinfo is None:
            alis_tarihi = alis_tarihi.tz_localize(history.index.tz)
        if cikis_tarihi.tzinfo is None:
            cikis_tarihi = cikis_tarihi.tz_localize(history.index.tz)
    
    if cikis_tarihi:
        # Önceden belirli bir çıkış tarihine kadardı, şimdi BUGÜNE KADAR istendi!
        pass
        
    mask = history.index >= alis_tarihi
    donem_verisi = history.loc[mask]
    
    max_fiyat = alis_fiyati
    max_tarih = None
    max_gun = 0
    min_fiyat = alis_fiyati
    min_tarih = None
    min_gun = 0
    
    suanki_fiyat = alis_fiyati  # varsayılan
    suanki_tarih = alis_tarihi # varsayılan
    
    if not donem_verisi.empty:
        max_idx = donem_verisi['High'].idxmax()
        max_fiyat = float(donem_verisi.loc[max_idx, 'High'])
        max_tarih = max_idx
        max_gun = (max_tarih.date() - alis_tarihi.date()).days
        
        min_idx = donem_verisi['Low'].idxmin()
        min_fiyat = float(donem_verisi.loc[min_idx, 'Low'])
        min_tarih = min_idx
        min_gun = (min_tarih.date() - alis_tarihi.date()).days
        
        # O HİSSENİN BAZ ALINAN EN SON/BUGÜNKÜ FİYATI
        son_satir = donem_verisi.iloc[-1]
        suanki_fiyat = float(son_satir['Close'])
        suanki_tarih = donem_verisi.index[-1]
        
    return {
        "max_fiyat": max_fiyat,
        "max_tarih": max_tarih.strftime("%d-%m-%Y") if max_tarih else "",
        "max_gun_sonra": max_gun,
        "max_kar_orani": ((max_fiyat - alis_fiyati) / alis_fiyati) * 100,
        "min_fiyat": min_fiyat,
        "min_tarih": min_tarih.strftime("%d-%m-%Y") if min_tarih else "",
        "min_gun_sonra": min_gun,
        "min_zarar_orani": ((min_fiyat - alis_fiyati) / alis_fiyati) * 100,
        "suanki_fiyat": suanki_fiyat,
        "suanki_tarih": suanki_tarih.strftime("%d-%m-%Y") if suanki_tarih else "",
        "suanki_kar_orani": ((suanki_fiyat - alis_fiyati) / alis_fiyati) * 100
    }

def run_ai_analysis(custom_params=None, start_date=None, end_date=None):
    print("🚀 [Web Backend] Arka planda devasa AI analizi başlatılıyor...")
    
    en_iyi_kategoriler = ultimate_strateji_optimizasyonu(
        custom_param_grid=custom_params,
        start_date=start_date,
        end_date=end_date
    )
    
    if not en_iyi_kategoriler:
        return {"error": "Strateji optimize edilemedi. Hisseler çekilememiş olabilir."}
        
    # Minimax Mantığı: En yüksek "EN KÖTÜ İHTİMAL" sonucunu veren kategoriyi seç
    def en_kotu_senaryo_getirisi(kategori_sonuc):
        stres_list = kategori_sonuc.get("stres_sonuclari", [])
        if not stres_list: return kategori_sonuc['final_sermaye']
        return min(s['final_sermaye'] for s in stres_list)
        
    en_karlisi = max(en_iyi_kategoriler.items(), key=lambda x: en_kotu_senaryo_getirisi(x[1]))
    sampiyon_kategori = en_karlisi[0]
    sampiyon_sonuc = en_karlisi[1]
    
    simulator = UltimateOptimizedSimulator()
    simulator.load_all_stock_data_once()
    if start_date: simulator.baslangic_filtresi = start_date
    if end_date: simulator.bitis_filtresi = end_date
    
    nihai_sonuc = simulator.simulasyon_calistir(
        sampiyon_sonuc['slot_sayisi'],
        sampiyon_sonuc['strateji'],
        hedef_kategori=sampiyon_kategori
    )
    
    zengin_islemler = []
    for islem in nihai_sonuc['islemler']:
        hisse = islem['hisse']
        history = simulator.all_stock_data[hisse]['history']
        detaylar = deep_analyze_trade(islem, history)
        
        zengin_islem = {
            "id": islem['hisse'] + "_" + islem['alis_tarihi'].strftime("%Y%m%d"),
            "hisse": hisse,
            "alis_tarihi": islem['alis_tarihi'].strftime("%d-%m-%Y"),
            "cikis_tarihi": islem['cikis_tarihi'].strftime("%d-%m-%Y"),
            "gun_sayisi": islem['gun_sayisi'],
            "alis_fiyati": round(islem['alis_fiyati'], 2),
            "cikis_fiyati": round(islem['cikis_fiyati'], 2),
            "kar_orani": round(islem['kar_orani'], 2),
            "kar_tl": round(islem['kar_tl'], 0),
            "cikis_sebebi": islem['cikis_sebebi'],
            "max_fiyat": round(detaylar["max_fiyat"], 2),
            "max_tarih": detaylar["max_tarih"],
            "max_gun_sonra": detaylar["max_gun_sonra"],
            "max_kar_orani": round(detaylar["max_kar_orani"], 2),
            "min_fiyat": round(detaylar["min_fiyat"], 2),
            "min_tarih": detaylar["min_tarih"],
            "min_gun_sonra": detaylar["min_gun_sonra"],
            "min_zarar_orani": round(detaylar["min_zarar_orani"], 2),
            "suanki_fiyat": round(detaylar["suanki_fiyat"], 2),
            "suanki_tarih": detaylar["suanki_tarih"],
            "suanki_kar_orani": round(detaylar["suanki_kar_orani"], 2),
        }
        zengin_islemler.append(zengin_islem)
        
    # ------- TÜM SİNYALLERİN BUGÜNE KADARKİ "HİÇ SATMASAYDIK" DURUMU -------
    tum_sinyaller_listesi = []
    import pandas as pd
    for hisse, veriler in portfolio.items():
        a_tarihi_str = veriler[0]
        a_fiyati = veriler[1]
        kat = signal_categories.get(hisse, "BİLİNMEYEN")
        
        # Simülatör tüm hisseleri çekmişti
        if hisse in simulator.all_stock_data:
            h_data = simulator.all_stock_data[hisse]['history']
            
            fake_islem = {
                'alis_tarihi': a_tarihi_str,  # %d-%m-%Y str
                'cikis_tarihi': None,
                'alis_fiyati': a_fiyati,
            }
            # Tarihi Datetime formatına çevir (tıpkı islemlerdeki gibi)
            try:
                fake_islem['alis_tarihi'] = pd.to_datetime(fake_islem['alis_tarihi'], format="%d-%m-%Y")
            except:
                fake_islem['alis_tarihi'] = pd.Timestamp.now()
                
            detaylar = deep_analyze_trade(fake_islem, h_data)
            
            tum_sinyaller_listesi.append({
                "hisse": hisse,
                "kategori": CATEGORY_LABELS.get(kat, kat),
                "alis_tarihi": a_tarihi_str,
                "alis_fiyati": round(a_fiyati, 2),
                
                "max_fiyat": round(detaylar["max_fiyat"], 2),
                "max_tarih": detaylar["max_tarih"],
                "max_kar_orani": round(detaylar["max_kar_orani"], 2),
                "max_gun_sonra": detaylar["max_gun_sonra"],
                
                "min_fiyat": round(detaylar["min_fiyat"], 2),
                "min_tarih": detaylar["min_tarih"],
                "min_zarar_orani": round(detaylar["min_zarar_orani"], 2),
                "min_gun_sonra": detaylar["min_gun_sonra"],
                
                "suanki_fiyat": round(detaylar["suanki_fiyat"], 2),
                "suanki_tarih": detaylar["suanki_tarih"],
                "suanki_kar_orani": round(detaylar["suanki_kar_orani"], 2)
            })
            
    # Listeyi alış tarihine göre sırala (en yeni sinyaller en üstte olsun)
    tum_sinyaller_listesi.sort(key=lambda x: pd.to_datetime(x['alis_tarihi'], format="%d-%m-%Y"), reverse=True)
            
    results = {
        "meta": {
            "tavsiye_baslik": CATEGORY_LABELS.get(sampiyon_kategori, sampiyon_kategori),
            "kategori_kodu": sampiyon_kategori,
            "strateji": sampiyon_sonuc['strateji'],
            "slot_sayisi": sampiyon_sonuc['slot_sayisi'],
            "final_sermaye": sampiyon_sonuc['final_sermaye'],
            "toplam_getiri": sampiyon_sonuc['toplam_getiri'],
            "basari_orani": round(sampiyon_sonuc['basari_orani'], 1),
            "basarili_islem": sampiyon_sonuc['basarili_islem'],
            "toplam_islem": sampiyon_sonuc['toplam_islem'],
            "yakalanan_hisse": sampiyon_sonuc['alinan_hisse'],
            "toplam_hisse": sampiyon_sonuc['toplam_hisse'],
            "is_custom": custom_params is not None or start_date is not None,
            "analiz_tarihi": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "islemler": zengin_islemler,
        "tum_sinyaller": tum_sinyaller_listesi
    }
    
    if "stres_sonuclari" in sampiyon_sonuc and sampiyon_sonuc["stres_sonuclari"]:
         stres = sampiyon_sonuc['stres_sonuclari']
         # MİNİMAX SEÇİMİ NEDENİYLE BU STRES_MİN DEĞERİ, DİĞER STRATEJİLERİN EN KÖTÜSÜNDEN DAHA İYİDİR!
         results["meta"]["stres_min"] = min([s['final_sermaye'] for s in stres])
         results["meta"]["stres_avg"] = sum([s['final_sermaye'] for s in stres]) / len(stres)
    else:
         results["meta"]["stres_min"] = 0
         results["meta"]["stres_avg"] = 0
         
    save_db(results)
    return results

@app.route('/')
def index():
    return render_template("index.html")
    
@app.route('/api/data')
def get_data():
    """Mevcut (DB'deki) veriyi döner, yoksa analiz ihtiyacını bildirir."""
    data = load_db()
    if not data:
        return jsonify({"need_analysis": True})
    return jsonify({"need_analysis": False, "data": data})

@app.route('/api/run_analysis', methods=['POST'])
def api_run_analysis():
    req = request.json or {}
    
    start_date = req.get('start_date') # Beklenen format: YYYY-MM-DD
    end_date = req.get('end_date')     # Beklenen format: YYYY-MM-DD
    
    # Custom params gelirse ayrıştır
    custom_params = None
    if req.get('custom_slots'):
        try:
            custom_params = {
                'slots': [int(x.strip()) for x in req.get('custom_slots').split(',')],
                'targets': [int(x.strip()) for x in req.get('custom_targets').split(',')],
                'stops': [int(x.strip()) for x in req.get('custom_stops').split(',')],
                'trails': [int(x.strip()) for x in req.get('custom_trails').split(',')],
                'days': [int(x.strip()) for x in req.get('custom_days').split(',')]
            }
        except:
            pass # Hata olursa parametreler yoksayılır

    result = run_ai_analysis(custom_params, start_date, end_date)
    return jsonify(result)

@app.route('/api/sync_telegram', methods=['POST'])
def sync_telegram():
    req = request.json or {}
    from_date = req.get('from_date', '2025-08-01')
    
    script_path = os.path.join(BASE_DIR, "telegram_to_portfolio.py")
    print(f"🔄 Telegram Sinyalleri Çekiliyor... (Tarih: {from_date})")
    
    # Processi çalıştır
    try:
        process = subprocess.run([sys.executable, script_path, "--from-date", from_date], 
                                 capture_output=True, text=True, check=True)
        return jsonify({"success": True, "output": process.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "error": str(e), "output": e.stdout + e.stderr})

if __name__ == '__main__':
    print("🌐 Yeşil Analiz - Premium AI Dashboard Başlıyor...")
    print("👉 Tarayıcında aç: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
