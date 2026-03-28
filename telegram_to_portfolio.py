"""
telegram_to_portfolio.py
────────────────────────
Telegram grubundaki sinyal mesajlarını okur ve hissetakip.py içindeki
`portfolio` ve `signal_categories` dict'lerini otomatik doldurur.

Kullanım:
  python telegram_to_portfolio.py --from-date 2025-08-01

  • İlk çalıştırmada API bilgileri sorulur ve config.json'a kaydedilir.
  • Verilen tarihten itibaren (o tarih dahil) yeni tarihe doğru mesajlar
    okunur.
  • Aynı hisse birden fazla kez gelmişse EN ERKEN sinyal tutulur.
  • 3 başlık kategorisi ayrı ayrı işlenir ve portfolio'ya etiketiyle yazılır.
"""

import asyncio
import re
import json
import os
import sys
import argparse
from datetime import datetime, timezone
from telethon import TelegramClient
from telethon.tl.types import MessageService

# ───────────────────────── Config ─────────────────────────
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tg_config.json")
HISSETAKIP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hissetakip.py")

# Sinyal başlıkları → kategori etiketleri (öncelik sırasına göre)
# Emojilere takılmaması için sadece düz metin arıyoruz
SIGNAL_PATTERNS = [
    ("GÜÇLÜ_HACİMLİ", ["GÜÇLÜ HACİMLİ GİRİŞ"]),
    ("HACİMLİ",       ["HACİMLİ GİRİŞ SİNYALİ"]),
    ("GİRİŞ",         ["GİRİŞ SİNYALİ"]),
]

CATEGORY_LABELS = {
    "GÜÇLÜ_HACİMLİ": "🔥 GÜÇLÜ HACİMLİ GİRİŞ",
    "HACİMLİ":       "✅ HACİMLİ GİRİŞ SİNYALİ",
    "GİRİŞ":         "✅ GİRİŞ SİNYALİ",
}

# ────────────────────── Config Helpers ────────────────────

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    print(f"✅ Ayarlar kaydedildi: {CONFIG_FILE}")

def ask_config():
    print("\n📋 Telegram API Bilgileri (my.telegram.org → API development tools)")
    print("─" * 60)
    api_id   = int(input("🔑 API ID         : ").strip())
    api_hash = input("🔑 API Hash       : ").strip()
    phone    = input("📱 Telefon (+90..): ").strip()
    group    = input("💬 Grup @username veya link (@yesil_analiz gibi): ").strip()
    cfg = {"api_id": api_id, "api_hash": api_hash, "phone": phone, "group": group}
    save_config(cfg)
    return cfg

# ───────────────────── Message Parser ─────────────────────

def detect_category(text: str):
    """Mesaj metnindeki başlığa göre kategori döner, yoksa None."""
    text_upper = text.upper()
    for category, keywords in SIGNAL_PATTERNS:
        for kw in keywords:
            if kw.upper() in text_upper:
                return category
    return None

def parse_signal_message(text: str, msg_date: datetime):
    """
    Mesaj metninden (Hisse, Tarih, Giriş Fiyatı) tuple'ı döner.
    Hata durumunda None döner.
    """
    # Telegram markdown karakterlerini (*, _, vs.) tamamen temizleyelim
    text_clean = re.sub(r'[*_~`]', '', text)

    # Hisse kodu bazen GARAN.E olabilir, ve başlıkta Hissee: yazım hatası olabilir
    hisse_match = re.search(r"Hisse[e]?\s*:\s*([A-ZÇĞİÖŞÜa-zçğışöşü0-9.\-]+)", text_clean, re.IGNORECASE)
    
    # Giriş seviyesi veya giriş fiyatı
    fiyat_match = re.search(r"Giri[sş].*?:\s*([\d.,]+)", text_clean, re.IGNORECASE)

    if not (hisse_match and fiyat_match):
        return None

    hisse = hisse_match.group(1).strip().upper()
    fiyat_raw = fiyat_match.group(1).strip().replace(",", ".")

    # Tarihi metin içindeki yazım hatalarından (20266-01-02 vb.) korumak için
    # doğrudan Telegram'ın kendi mesaj zaman damgasını kullanıyoruz!
    tarih_dt = msg_date
    tarih_str = tarih_dt.strftime("%d-%m-%Y")
    
    try:
        fiyat = float(fiyat_raw)
    except ValueError:
        return None

    return hisse, tarih_str, tarih_dt, fiyat

# ──────────────────── Portfolio Writer ────────────────────

def build_portfolio_block(signals: dict):
    """
    signals: { ticker: {"tarih": "dd-mm-yyyy", "fiyat": x.xx, "category": "..."} }
    Kategori bazlı gruplanmış Python kod bloğu döner.
    """
    # Kategorilere göre grupla
    groups = {cat: {} for cat in CATEGORY_LABELS}
    for ticker, info in sorted(signals.items(), key=lambda i: i[1]["tarih_dt"]):
        cat = info["category"]
        groups[cat][ticker] = info

    lines = ["portfolio = {", ""]

    for cat, label in CATEGORY_LABELS.items():
        group = groups[cat]
        if not group:
            continue
        lines.append(f"    # {'=' * 10} {label} ({len(group)} hisse) {'=' * 10}")
        for ticker, info in sorted(group.items(), key=lambda i: i[1]["tarih_dt"]):
            lines.append(f'    "{ticker}": ["{info["tarih"]}", {info["fiyat"]}],  # {cat}')
        lines.append("")

    lines.append("}")
    return "\n".join(lines)

def build_categories_block(signals: dict):
    """signal_categories dict kod bloğu döner."""
    lines = ["signal_categories = {"]
    for ticker, info in sorted(signals.items()):
        lines.append(f'    "{ticker}": "{info["category"]}",')
    lines.append("}")
    return "\n".join(lines)

def update_hissetakip(new_portfolio_code: str, new_categories_code: str):
    """
    hissetakip.py içindeki `portfolio = { ... }` bloğunu ve
    `signal_categories = { ... }` bloğunu değiştirir (veya ekler).
    """
    with open(HISSETAKIP_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # ── portfolio bloğunu değiştir ──────────────────────
    port_pattern = re.compile(
        r'^portfolio\s*=\s*\{.*?\n\}', re.MULTILINE | re.DOTALL
    )
    if port_pattern.search(content):
        content = port_pattern.sub(new_portfolio_code, content, count=1)
    else:
        # Dosyanın başına ekle (import bloğundan sonra)
        import_end = re.search(r'^((?:import |from ).*\n)+', content, re.MULTILINE)
        if import_end:
            insert_at = import_end.end()
            content = content[:insert_at] + "\n" + new_portfolio_code + "\n" + content[insert_at:]
        else:
            content = new_portfolio_code + "\n\n" + content

    # ── signal_categories bloğunu değiştir / ekle ───────
    cat_pattern = re.compile(
        r'^signal_categories\s*=\s*\{.*?\n\}', re.MULTILINE | re.DOTALL
    )
    if cat_pattern.search(content):
        content = cat_pattern.sub(new_categories_code, content, count=1)
    else:
        # portfolio bloğundan hemen sonrasına ekle
        port_match = re.search(r'^portfolio\s*=\s*\{.*?\n\}', content, re.MULTILINE | re.DOTALL)
        if port_match:
            insert_at = port_match.end()
            content = content[:insert_at] + "\n\n" + new_categories_code + content[insert_at:]
        else:
            content = new_categories_code + "\n\n" + content

    with open(HISSETAKIP_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ hissetakip.py güncellendi!")

# ──────────────────────── Main ────────────────────────────

async def fetch_signals(cfg: dict, from_date: datetime):
    """Telegram grubundan sinyal mesajlarını çeker ve dict döner."""
    session_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tg_session")

    client = TelegramClient(session_path, cfg["api_id"], cfg["api_hash"])
    await client.start(phone=cfg["phone"])
    print(f"✅ Telegram bağlantısı kuruldu.")

    group = cfg["group"]
    print(f"📡 Grup okunuyor: {group}")
    print(f"📅 Başlangıç tarihi: {from_date.strftime('%d-%m-%Y')}")
    print("─" * 60)

    # from_date'i UTC offset-aware yap
    from_date_aware = from_date.replace(tzinfo=timezone.utc)

    # Sonuçlar: { ticker: { tarih, tarih_dt, fiyat, category } }
    signals: dict = {}

    total_read = 0
    matched = 0

    # iter_messages reverse=True → en eski mesajdan yeniye
    # offset_date → from_date'den itibaren
    async for msg in client.iter_messages(
        group,
        reverse=True,
        offset_date=from_date_aware,
        limit=None,
    ):
        if isinstance(msg, MessageService) or not msg.text:
            continue

        total_read += 1
        text = msg.text

        category = detect_category(text)
        if category is None:
            if "hisse:" in text.lower() and matched == 0:
                print(f"⚠️ DİKKAT: Kategori (Başlık) bulunamadı! Mesajın Başı: {text[:100].replace(chr(10), ' ')}")
            continue

        parsed = parse_signal_message(text, msg.date)
        if parsed is None:
            if "hisse:" in text.lower() and matched == 0:
                print(f"⚠️ DİKKAT: İçerik parse edilemedi! Kategori: {category}. Mesajın Başı: {text[:100].replace(chr(10), ' ')}")
            continue

        hisse, tarih_str, tarih_dt, fiyat = parsed
        matched += 1

        if hisse not in signals:
            # İlk kez görüldü − kaydet
            signals[hisse] = {
                "tarih":    tarih_str,
                "tarih_dt": tarih_dt,
                "fiyat":    fiyat,
                "category": category,
            }
            print(f"  ✅ {hisse:10s} [{category:15s}] {tarih_str}  {fiyat:.2f} TL")
        else:
            # Daha önce görüldü − daha eski tarihi tut
            if tarih_dt < signals[hisse]["tarih_dt"]:
                signals[hisse] = {
                    "tarih":    tarih_str,
                    "tarih_dt": tarih_dt,
                    "fiyat":    fiyat,
                    "category": category,
                }
                print(f"  🔄 {hisse:10s} [{category:15s}] {tarih_str}  {fiyat:.2f} TL  (güncellendi-eskisi)")

    await client.disconnect()
    print("─" * 60)
    print(f"📊 Okunan mesaj: {total_read}  |  Eşleşen sinyal: {matched}  |  Benzersiz hisse: {len(signals)}")
    return signals


def print_summary(signals: dict):
    print("\n" + "=" * 60)
    print("📊 KATEGORİ BAZLI ÖZET")
    print("=" * 60)
    for cat, label in CATEGORY_LABELS.items():
        group_signals = {k: v for k, v in signals.items() if v["category"] == cat}
        if group_signals:
            print(f"\n{label}  ({len(group_signals)} hisse)")
            for ticker, info in sorted(group_signals.items(), key=lambda i: i[1]["tarih_dt"]):
                print(f"  • {ticker:10s} {info['tarih']}  {info['fiyat']:.2f} TL")
    print()


def main():
    parser = argparse.ArgumentParser(description="Telegram sinyal → hissetakip.py portfolio")
    parser.add_argument(
        "--from-date",
        required=True,
        metavar="YYYY-MM-DD",
        help="Bu tarihten itibaren mesajları oku (bu tarih dahil)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dosyayı değiştirme, sadece ne yazılacağını göster"
    )
    args = parser.parse_args()

    # Tarih parse
    try:
        from_date = datetime.strptime(args.from_date, "%Y-%m-%d")
    except ValueError:
        print("❌ Tarih formatı yanlış. Örnek: --from-date 2025-08-01")
        sys.exit(1)

    # Config yükle / sor
    cfg = load_config()
    if cfg is None:
        print("⚙️  Config bulunamadı. Telegram bilgileri girilecek...")
        cfg = ask_config()

    # Sinyal çek
    print("\n🚀 Telegrama bağlanılıyor...\n")
    signals = asyncio.get_event_loop().run_until_complete(fetch_signals(cfg, from_date))

    if not signals:
        print("⚠️  Hiç sinyal bulunamadı. Grup adı veya başlangıç tarihi kontrol edin.")
        sys.exit(0)

    # Portfolio ve kategori bloklarını oluştur
    portfolio_code   = build_portfolio_block(signals)
    categories_code  = build_categories_block(signals)

    print_summary(signals)

    if args.dry_run:
        print("─── DRY RUN: hissetakip.py DEĞİŞTİRİLMEDİ ───")
        print("\n[portfolio]\n")
        print(portfolio_code)
        print("\n[signal_categories]\n")
        print(categories_code)
    else:
        print("📝 hissetakip.py güncelleniyor...")
        update_hissetakip(portfolio_code, categories_code)
        print("\n✅ İşlem tamamlandı!")
        print(f"   {len(signals)} hisse portföye yazıldı.")
        print(f"   Şimdi 'python hissetakip.py' çalıştırabilirsiniz.")


if __name__ == "__main__":
    main()
