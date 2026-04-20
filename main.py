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

# 1. Analiz Edilecek 11 Ana Kanal
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

def ucretsiz_yapay_zeka_analizi():
    """Haberleri toplayıp TextBlob ile ücretsiz duygu analizi yapar."""
    try:
        rss_url = "https://finance.yahoo.com/news/rssindex"
        feed = feedparser.parse(rss_url)
        
        toplam_duygu = 0
        sayac = 0
        
        for entry in feed.entries[:15]:
            analiz = TextBlob(entry.title)
            toplam_duygu += analiz.sentiment.polarity
            sayac += 1
            
        ortalama = toplam_duygu / sayac if sayac > 0 else 0
        
        if ortalama > 0.05:
            return "🟢 *POZİTİF* (Piyasalarda alım iştahı ve iyimserlik hakim)"
        elif ortalama < -0.05:
            return "🔴 *NEGATİF* (Haberlerde korku ve satış baskısı öne çıkıyor)"
        else:
            return "⚪ *NÖTR* (Haber akışı belirsiz veya dengeli)"
            
    except Exception as e:
        return f"⚪ AI Analizi Başarısız Oldu: {str(e)}"

def piyasa_verilerini_cek_ve_analiz_et():
    rapor = f"🌍 *KÜRESEL MAKRO PİYASA RAPORU* ({datetime.datetime.now().strftime('%H:%M')})\n"
    rapor += "--------------------------------------\n"
    
    veri_sozlugu = {}

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
            else:
                rapor += f"⚪ {isim}: Veri yetersiz.\n"
        except:
            veri_sozlugu[isim] = 0
            rapor += f"⚪ {isim}: Veri çekilemedi.\n"
            
    rapor += "--------------------------------------\n"
    
    # --- ÜCRETSİZ AI HABER ANALİZİ ---
    rapor += "🧠 *YAPAY ZEKA HABER DUYARLILIĞI:*\n"
    rapor += ucretsiz_yapay_zeka_analizi() + "\n\n"
    
    # --- DİNAMİK ÇAPRAZ RASYO YORUMLARI ---
    rapor += "🤖 *ALGORİTMA PİYASA YORUMU:*\n"
    
    dxy_yon = veri_sozlugu.get("7. Dolar Endeksi (DXY)", 0)
    altin_yon = veri_sozlugu.get("3. Güvenli Liman (Altın)", 0)
    bakir_yon = veri_sozlugu.get("5. Endüstriyel (Bakır)", 0)
    borsa_yon = veri_sozlugu.get("1. ABD Borsası (S&P 500)", 0)
    faiz_yon = veri_sozlugu.get("2. ABD 10Y Tahvil (Faiz)", 0)

    if dxy_yon > 0:
        rapor += "⚠️ *Dolar Güçleniyor:* Küresel likidite dolara çekiliyor, bu durum emtia ve borsalarda baskı yaratır.\n"
    else:
        rapor += "💵 *Dolar Zayıflıyor:* Doların geri çekilmesi, riskli varlıklara ve değerli metallere nefes aldırıyor.\n"

    if bakir_yon > 0 and altin_yon <= 0:
        rapor += "🏭 *Sanayi Çarkları Dönüyor:* Bakırın altına karşı güçlenmesi, piyasaların resesyon (kriz) beklemediğini gösterir.\n"
    elif altin_yon > 0 and bakir_yon <= 0:
        rapor += "🛡️ *Güvenli Liman Talebi:* Bakır düşerken Altının yükselmesi, yatırımcıların riskten kaçarak nakit korumaya geçtiğinin sinyalidir.\n"

    if faiz_yon > 0 and borsa_yon < 0:
        rapor += "📉 *Sermaye Göçü:* Tahvil faizlerindeki artış, parayı borsadan risksiz getiriye doğru çekiyor.\n"
    elif borsa_yon > 0:
        rapor += "📈 *Risk İştahı Açık:* Borsalara para girişi devam ediyor, faiz baskısı şu an fiyatlanmıyor.\n"

    return rapor

@bot.message_handler(commands=['start', 'rapor'])
def handle_commands(message):
    if str(message.from_user.id) == str(KULLANICI_ID):
        bot.send_message(message.chat.id, "🤖 Makro analiz, rasyolar ve AI haber okuması yapılıyor. Lütfen bekleyin...")
        metin = piyasa_verilerini_cek_ve_analiz_et()
        bot.send_message(message.chat.id, metin, parse_mode="Markdown")
    else:
        bot.reply_to(message, "Bu bot kişiye özeldir. Erişim reddedildi.")

if __name__ == "__main__":
    bot.infinity_polling()
