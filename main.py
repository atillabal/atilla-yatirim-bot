import telebot
import yfinance as yf
import os
import datetime
import feedparser
from textblob import TextBlob

# --- GÜVENLİ AYARLAR ---
API_TOKEN = os.getenv("TELEGRAM_TOKEN")
KULLANICI_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(API_TOKEN)

# 1. Analiz Edilecek 12 Ana Kanal (Gümüş ve Bakır Eklendi)
varliklar = {
    "1. ABD Borsası (S&P 500)": "^GSPC",
    "2. ABD 10Y Tahvil (Faiz)": "^TNX",
    "3. Güvenli Liman (Altın)": "GC=F",
    "4. Güvenli Liman (Gümüş)": "SI=F",
    "5. Endüstriyel (Bakır)": "HG=F",
    "6. Enerji (Petrol)": "CL=F",
    "7. Dolar Endeksi (DXY)": "DX-Y.NYB",
    "8. Kripto (Bitcoin)": "BTC-USD",
    "9. Tarım (Buğday)": "ZW=F",
    "10. Gelişen Piyasalar": "EEM",
    "11. Şirket Tahvilleri": "LQD"
}

def yapay_zeka_haber_analizi():
    """Küresel RSS akışından haberleri okur ve NLP ile duygu analizi yapar."""
    try:
        # Yahoo Finance Küresel Piyasa Haberleri RSS Akışı
        rss_url = "https://finance.yahoo.com/news/rssindex"
        feed = feedparser.parse(rss_url)
        
        toplam_duygu_puani = 0
        haber_sayisi = 0
        
        for entry in feed.entries[:15]: # Son 15 haberi analiz et
            analiz = TextBlob(entry.title)
            toplam_duygu_puani += analiz.sentiment.polarity
            haber_sayisi += 1
            
        ortalama_duygu = toplam_duygu_puani / haber_sayisi if haber_sayisi > 0 else 0
        
        if ortalama_duygu > 0.05:
            return "🟢 *POZİTİF* (Piyasalarda risk iştahı ve iyimserlik hakim)"
        elif ortalama_duygu < -0.05:
            return "🔴 *NEGATİF* (Küresel haberlerde korku ve satış baskısı öne çıkıyor)"
        else:
            return "⚪ *NÖTR* (Haber akışı belirsiz veya dengeli)"
    except Exception as e:
        return "⚪ Analiz Edilemedi (RSS Bağlantı Hatası)"

def piyasa_verilerini_cek_ve_analiz_et():
    rapor = f"🌍 *KÜRESEL MAKRO PİYASA RAPORU* ({datetime.datetime.now().strftime('%H:%M')})\n"
    rapor += "--------------------------------------\n"
    
    veri_sozlugu = {}

    # Verileri çek ve yüzdeleri hesapla
    for isim, sembol in varliklar.items():
        try:
            data = yf.download(sembol, period="5d", progress=False)['Close'].dropna()
            if len(data) >= 2:
                dunku_kapanis = data.iloc[-2].item()
                bugunku_kapanis = data.iloc[-1].item()
                degisim_yuzdesi = ((bugunku_kapanis - dunku_kapanis) / dunku_kapanis) * 100
                veri_sozlugu[isim] = degisim_yuzdesi
                
                ikon = "🟢" if degisim_yuzdesi > 0 else "🔴"
                rapor += f"{ikon} {isim}: %{degisim_yuzdesi:.2f}\n"
        except:
            veri_sozlugu[isim] = 0 # Hata durumunda 0 kabul et
            rapor += f"⚪ {isim}: Veri çekilemedi.\n"
            
    rapor += "--------------------------------------\n"
    
    # --- YAPAY ZEKA HABER ANALİZİ ---
    rapor += "🧠 *YAPAY ZEKA HABER DUYARLILIĞI:*\n"
    rapor += yapay_zeka_haber_analizi() + "\n\n"
    
    # --- DİNAMİK ÇAPRAZ RASYO YORUMLARI (Kesin Çıktı Üretir) ---
    rapor += "🤖 *ALGORİTMA PİYASA YORUMU:*\n"
    
    dxy_yon = veri_sozlugu.get("7. Dolar Endeksi (DXY)", 0)
    altin_yon = veri_sozlugu.get("3. Güvenli Liman (Altın)", 0)
    bakir_yon = veri_sozlugu.get("5. Endüstriyel (Bakır)", 0)
    borsa_yon = veri_sozlugu.get("1. ABD Borsası (S&P 500)", 0)
    faiz_yon = veri_sozlugu.get("2. ABD 10Y Tahvil (Faiz)", 0)

    # Dolar Analizi
    if dxy_yon > 0:
        rapor += "⚠️ *Dolar Güçleniyor:* Küresel likidite dolara çekiliyor, bu durum emtia ve borsalarda baskı yaratır.\n"
    else:
        rapor += "💵 *Dolar Zayıflıyor:* Doların geri çekilmesi, riskli varlıklara ve değerli metallere nefes aldırıyor.\n"

    # Altın / Bakır (Korku vs Büyüme) Analizi
    if bakir_yon > 0 and altin_yon <= 0:
        rapor += "🏭 *Sanayi Çarkları Dönüyor:* Bakırın altına karşı güçlenmesi, piyasaların resesyon (kriz) beklemediğini gösterir.\n"
    elif altin_yon > 0 and bakir_yon <= 0:
        rapor += "🛡️ *Güvenli Liman Talebi:* Bakır düşerken Altının yükselmesi, yatırımcıların bir riskten kaçarak nakit korumaya geçtiğinin net sinyalidir.\n"

    # Tahvil vs Borsa Analizi
    if faiz_yon > 0 and borsa_yon < 0:
        rapor += "📉 *Sermaye Göçü:* Tahvil faizlerindeki artış, parayı borsadan risksiz getiriye doğru çekiyor.\n"
    elif borsa_yon > 0:
        rapor += "📈 *Risk İştahı Açık:* Borsalara para girişi devam ediyor, faiz baskısı şu an için fiyatlanmıyor.\n"

    return rapor

@bot.message_handler(commands=['start', 'rapor'])
def handle_commands(message):
    if str(message.from_user.id) == str(KULLANICI_ID):
        bot.send_message(message.chat.id, "🤖 Makro analiz, rasyolar ve Yapay Zeka haber okuması yapılıyor. Lütfen bekleyin...")
        metin = piyasa_verilerini_cek_ve_analiz_et()
        bot.send_message(message.chat.id, metin, parse_mode="Markdown")
    else:
        bot.reply_to(message, "Bu bot kişiye özeldir. Erişim reddedildi.")

if __name__ == "__main__":
    print("Bot yayına başladı...")
    bot.infinity_polling()
