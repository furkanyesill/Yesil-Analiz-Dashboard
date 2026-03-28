import asyncio
import os
import json
import re
from datetime import datetime, timezone, timedelta
import yfinance as yf
from telethon import TelegramClient, events

# =========================================================================
# CONFIG VE SABİTLER
# =========================================================================
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tg_config.json")
LIVE_PORTFOLIO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "live_portfolio.json")
SUBSCRIBERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "subscribers.json")

# KESİN STRATEJİ KURALLARI (Şampiyon Kombinasyon)
KAR_HEDEFI = 12.0
STOP_LOSS = 10.0
TRAILING_STOP = 6.0
MAX_GUN = 14

SIGNAL_PATTERNS = [
    ("GÜÇLÜ_HACİMLİ", ["GÜÇLÜ HACİMLİ GİRİŞ"]),
    ("HACİMLİ",       ["HACİMLİ GİRİŞ SİNYALİ"]),
    ("GİRİŞ",         ["GİRİŞ SİNYALİ"]),
]

# =========================================================================
# YARDIMCI FONKSİYONLAR
# =========================================================================
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def load_live_portfolio():
    if os.path.exists(LIVE_PORTFOLIO_FILE):
        with open(LIVE_PORTFOLIO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_live_portfolio(port):
    with open(LIVE_PORTFOLIO_FILE, "w", encoding="utf-8") as f:
        json.dump(port, f, indent=4, ensure_ascii=False)

def load_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_subscribers(subs):
    with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(set(subs)), f, indent=4)

async def broadcast_message(client, text, admin_id=None):
    subs = load_subscribers()
    if admin_id and str(admin_id) != 'me' and admin_id not in subs:
        subs.append(admin_id)
        save_subscribers(subs)
        
    # Userbot modundaysak (admin_id == 'me')
    if admin_id == 'me' and not subs:
        await client.send_message('me', text)
        return
        
    for user_id in set(subs):
        try:
            await client.send_message(int(user_id), text)
        except Exception as e:
            print(f"[{user_id}] Bildirim gönderilemedi: {e}")

def detect_category(text: str):
    text_upper = text.upper()
    for category, keywords in SIGNAL_PATTERNS:
        for kw in keywords:
            if kw.upper() in text_upper:
                return category
    return None

def parse_signal_message(text: str, msg_date: datetime):
    text_clean = re.sub(r'[*_~`]', '', text)
    hisse_match = re.search(r"Hisse[e]?\s*:\s*([A-ZÇĞİÖŞÜa-zçğışöşü0-9.\-]+)", text_clean, re.IGNORECASE)
    fiyat_match = re.search(r"Giri[sş].*?:\s*([\d.,]+)", text_clean, re.IGNORECASE)
    if not (hisse_match and fiyat_match):
        return None
    hisse = hisse_match.group(1).strip().upper()
    fiyat_raw = fiyat_match.group(1).strip().replace(",", ".")
    try:
        fiyat = float(fiyat_raw)
    except ValueError:
        return None
    return hisse, msg_date, fiyat

def get_current_price(hisse):
    try:
        ticker = yf.Ticker(hisse + ".IS")
        pr = ticker.fast_info.get('lastPrice')
        if not pr or str(pr).lower() == 'nan':
            hist = ticker.history(period="1d")
            if not hist.empty:
                pr = hist['Close'].iloc[-1]
        return pr
    except Exception as e:
        print(f"[{hisse}] Fiyat çekilemedi: {e}")
        return None

# =========================================================================
# ÇEKİRDEK İŞLEMLER
# =========================================================================
async def pazar_ozeti_ve_kapanis(client, cfg):
    """Her gün 18:30 civarı günlük kapanış işlemlerini yapar ve özet gönderir"""
    port = load_live_portfolio()
    admin_id = int(cfg.get("admin_user_id", 0)) if cfg.get("admin_user_id") else 'me'
    
    if not port:
         await broadcast_message(client, "ℹ️ Şuan takip edilen aktif bir hisse yok.", admin_id)
         return
         
    ozet_mesaji = "📊 **GÜNLÜK KAPANIŞ VE TRAILING STOP ÖZETİ (18:30)** 📊\n\n"
    silinecek_hisseler = []
    simdi = datetime.now(timezone.utc)
    
    for hisse, veri in port.items():
        pr = get_current_price(hisse)
        if not pr:
            continue
            
        alis_fiyati = veri["alis_fiyati"]
        alis_tarihi = datetime.fromisoformat(veri["alis_tarihi"])
        
        # Süre Hesabı
        gecen_gun = (simdi.date() - alis_tarihi.date()).days
        if gecen_gun < 0: gecen_gun = 0
        kalan_gun = MAX_GUN - gecen_gun
        veri["aktif_gun_sayisi"] = gecen_gun
        
        hedef_fiyat = alis_fiyati * (1 + KAR_HEDEFI / 100)
        sabit_stop_fiyati = alis_fiyati * (1 - STOP_LOSS / 100)
        
        # --- TRAILING STOP (SİMÜLASYON MATEMATİĞİ) ---
        trailing_metni = "Aktif Değil (Kapanış henüz alış fiyatını geçmedi)"
        aktif_trailing_fiyati = None
        
        if not veri.get("trailing_aktif", False):
            # 1. Kural: İlk kez alış fiyatından yüksek kapanış
            if pr > alis_fiyati:
                veri["trailing_aktif"] = True
                veri["en_yuksek_kapanis"] = pr
                veri["trailing_aktif_gun"] = str(simdi.date())
                aktif_trailing_fiyati = pr * (1 - TRAILING_STOP / 100)
                trailing_metni = f"AKTİF 🟢 (Limit: {aktif_trailing_fiyati:.3f} TL)"
        else:
            # 2. Kural: Zaten aktifse ve dünden daha yüksek kapattıysa yukarı taşı
            if pr > veri["en_yuksek_kapanis"]:
                veri["en_yuksek_kapanis"] = pr
                
            aktif_trailing_fiyati = veri["en_yuksek_kapanis"] * (1 - TRAILING_STOP / 100)
            trailing_metni = f"AKTİF 🟢 (Limit: {aktif_trailing_fiyati:.3f} TL) [Tepe: {veri['en_yuksek_kapanis']:.3f}]"
        
        # Süre Limitine Çarpma:
        if gecen_gun >= MAX_GUN:
             kar_orani = ((pr - alis_fiyati) / alis_fiyati) * 100
             emo = "🟢" if kar_orani > 0 else "🔴"
             ozet_mesaji += f"⏳ **{hisse}** SÜRESİ DOLDU! ({MAX_GUN} Gün)\n💰 Satış: {pr:.3f} TL ({emo} %{kar_orani:.1f})\n\n"
             silinecek_hisseler.append(hisse)
             continue
             
        ozet_mesaji += f"📌 **{hisse}** (Giriş: {alis_fiyati:.3f} TL | Güncel: {pr:.3f} TL)\n"
        ozet_mesaji += f"   🎯 Hedef (%12): {hedef_fiyat:.3f} TL\n"
        ozet_mesaji += f"   🛑 Sabit Stop (%10): {sabit_stop_fiyati:.3f} TL\n"
        ozet_mesaji += f"   🛡️ Trailing (%6): {trailing_metni}\n"
        ozet_mesaji += f"   ⏳ Kalan Gün: {kalan_gun} gün\n\n"
        
    for h in silinecek_hisseler:
        del port[h]
        
    save_live_portfolio(port)
    await broadcast_message(client, ozet_mesaji, admin_id)

async def check_market_prices(client, cfg):
    """Gün içi fiyatları kontrol eder ve Tetikleyicileri (Trigger) arar"""
    port = load_live_portfolio()
    admin_id = int(cfg.get("admin_user_id", 0)) if cfg.get("admin_user_id") else 'me'
    
    if not port:
        return
        
    silinecek_hisseler = []
    simdi = datetime.now(timezone.utc)
    
    for hisse, veri in port.items():
        pr = get_current_price(hisse)
        if not pr:
            continue
             
        alis_fiyati = veri["alis_fiyati"]
        hedef_fiyat = alis_fiyati * (1 + KAR_HEDEFI / 100)
        sabit_stop_fiyati = alis_fiyati * (1 - STOP_LOSS / 100)
        
        # 1. Sabit Stop Kontrolü
        if pr <= sabit_stop_fiyati:
             await broadcast_message(client, f"🚨 **ZARAR KES (STOP LOSS) TETİKLENDİ!**\n📉 Hisse: {hisse}\n💰 Satış Fiyatı: {pr:.3f} TL (Zarar: %10)\n🚫 Takipten çıkarıldı.", admin_id)
             silinecek_hisseler.append(hisse)
             continue
             
        # 2. Kar Hedefi Kontrolü
        if pr >= hedef_fiyat:
             await broadcast_message(client, f"🎉 **KAR HEDEFİNE ULAŞILDI!**\n📈 Hisse: {hisse}\n💰 Satış Fiyatı: {pr:.3f} TL (Kar: %12)\n✅ Takipten çıkarıldı.", admin_id)
             silinecek_hisseler.append(hisse)
             continue
             
        # 3. Trailing Stop Kontrolü (Sadece Kapanışta Güncellenmiş Stop Seviyesi İçin)
        if veri.get("trailing_aktif", False):
             # Simülasyonda trailing stop'un ilk aktif olduğu gün içindeysek stop tetiklenmez.
             if veri.get("trailing_aktif_gun") != str(simdi.date()):
                 trailing_limit = veri["en_yuksek_kapanis"] * (1 - TRAILING_STOP / 100)
                 if pr <= trailing_limit:
                      kar_orani = ((pr - alis_fiyati) / alis_fiyati) * 100
                      durum_emoji = "🟢 Kar" if kar_orani > 0 else "🔴 Zarar"
                      await client.send_message(admin_id, f"🛡️ **TRAILING STOP TETİKLENDİ!**\n📉 Hisse: {hisse}\n💰 Satış Fiyatı: {pr:.3f} TL\n📊 Sonuç: {durum_emoji} (%{kar_orani:.1f})\n🚫 Takipten çıkarıldı.")
                      silinecek_hisseler.append(hisse)
                      continue

    for h in silinecek_hisseler:
        if h in port:
             del port[h]
    if silinecek_hisseler:
        save_live_portfolio(port)

async def market_poller(client, cfg):
    """Piyasa saatlerinde fiyat kontrolünü sürekli arka planda yapar."""
    tz_trt = timezone(timedelta(hours=3))
    
    daily_summary_sent_today = False
    
    while True:
        try:
            now_tr = datetime.now(tz_trt)
            
            # Hafta içi mi? (0=Pzt, 4=Cuma)
            if now_tr.weekday() <= 4:
                # 10:00 - 18:15 arası piyasa açık
                if 10 <= now_tr.hour <= 18:
                    await check_market_prices(client, cfg)
                    
                # Saat 18:30'da günlük kapaniş ve trailing hesaplamasi
                if now_tr.hour == 18 and now_tr.minute >= 30 and not daily_summary_sent_today:
                    await pazar_ozeti_ve_kapanis(client, cfg)
                    daily_summary_sent_today = True
                    
            # Ertesi güne geçildiğinde bayrağı temizle
            if now_tr.hour == 0:
                 daily_summary_sent_today = False
                 
        except Exception as e:
            print(f"Poller hatası: {e}")
            
        # Her 2 dakikada bir kontrol et
        await asyncio.sleep(120)

# =========================================================================
# ANA BOT DOSYASI (MAIN)
# =========================================================================
async def main():
    cfg = load_config()
    if not cfg:
        print("❌ Config bulunamadı. Lütfen önce telegram_to_portfolio.py dosyasını çalıştırıp API bilgilerini girin.")
        return
        
    session_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tg_session")
    
    admin_id = int(cfg.get("admin_user_id", 0)) if cfg.get("admin_user_id") else 'me'
    
    client = TelegramClient(session_path, cfg["api_id"], cfg["api_hash"])
    
    if cfg.get("bot_token"):
        await client.start(bot_token=cfg["bot_token"])
        print("✅ Live Bot (Resmi Bot API) Telegram Bağlantısı Kuruldu!")
    else:
        await client.start(phone=cfg["phone"])
        print("✅ Live Bot (Userbot) Telegram Bağlantısı Kuruldu!")
        
    print(f"📡 {cfg['group']} kanalı dinleniyor...")
    
    # ── 1. Telegramdan Canlı Sinyal Yakalama ──
    @client.on(events.NewMessage(chats=cfg["group"]))
    async def handler(event):
        if not event.message.text: return
        cat = detect_category(event.message.text)
        
        # İstenilen 2 hedef kategorisi kontrolü (GÜÇLÜ_HACİMLİ ve GİRİŞ ikilisi)
        if cat in ["GÜÇLÜ_HACİMLİ", "GİRİŞ"]:
            parsed = parse_signal_message(event.message.text, event.message.date)
            if parsed:
                hisse, tarih_dt, fiyat = parsed
                port = load_live_portfolio()
                
                if hisse not in port:
                    port[hisse] = {
                        "alis_fiyati": fiyat,
                        "alis_tarihi": tarih_dt.isoformat(),
                        "trailing_aktif": False,
                        "en_yuksek_kapanis": fiyat,
                        "kategori": cat
                    }
                    save_live_portfolio(port)
                    
                    mesaj_metni = (
                             f"🚨 **YENİ SİNYAL YAKALANDI VE LİSTEYE EKLENDİ!** 🚨\n\n"
                             f"📈 **Hisse:** {hisse}\n"
                             f"🏷️ **Kategori:** {cat}\n"
                             f"💰 **Sinyal/Giriş Fiyatı:** {fiyat} TL\n\n"
                             f"⚙️ **Tetikleyiciler (Senin Adına Bekliyorum):**\n"
                             f"🎯 Hedef Kar: %12\n"
                             f"🛑 Stop Loss: %10\n"
                             f"🛡️ Trailing Limit: %6 (Yeşil kapatırsa aktif olur)\n"
                             f"⏳ Süre Limiti: 14 Gün"
                    )
                    await broadcast_message(client, mesaj_metni, admin_id)
                    print(f"✅ Yeni hisse sisteme entegre edildi: {hisse} ({fiyat} TL)")

    # ── 2. Kullanıcıdan Gelen Manuel İstekler (DM / Kendine atılan gizli komut) ──
    @client.on(events.NewMessage(incoming=True))
    async def manual_handler(event):
        try:
            sender_id = event.sender_id
            subs = load_subscribers()
            
            # Userbot check
            if admin_id == 'me' and not event.out and not event.is_private:
                if sender_id != (await client.get_me()).id:
                    return
                    
            text = event.message.text.lower()
            
            # /start komutu - yeni abone kaydı
            if text == "/start":
                if admin_id != 'me' and sender_id not in subs:
                    subs.append(sender_id)
                    save_subscribers(subs)
                    await event.reply("👋 Borsa Bildirim Ağına Hoşgeldin! Artık yapay zeka sisteminin kar/zarar bildirimlerini VIP olarak alacaksın! `ozet` yazarak mevcut hisselere bakabilirsin.")
                else:
                    await event.reply("Hali hazırda sisteme kayıtlısın! `ozet` yazıp listeyi görebilirsin.")
                return

            # Diğer komutlar için abone değilse reddet
            if admin_id != 'me' and sender_id not in subs and sender_id != admin_id:
                return

        except Exception:
            pass
            
        text = event.message.text.lower()
        if text == "ozet":
            mesaj = await event.reply("🔄 Manuel özet ve güncel Yahoo Finance fiyatları çekiliyor...")
            await pazar_ozeti_ve_kapanis(client, cfg)
        elif text == "tetik":
            await event.reply("⚡ Sistem tetikleyicileri Yahoo'dan kontrole başladı...")
            await check_market_prices(client, cfg)
            await event.reply("✅ Kontrol tamamlandı!")

    print("\n👉 Bot şu anda arka planda Yahoo Finance'i sessizce tarıyor ve Telegram grubunda bekliyor.")
    print("👉 Bota (veya Kayıtlı Mesajlara) 'ozet' yazarak güncel tabloyu anında çekebilirsin.")
    
    # ── 3. Arka Plan Poller ve Bağlantıyı Beklet ──
    client.loop.create_task(market_poller(client, cfg))
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
