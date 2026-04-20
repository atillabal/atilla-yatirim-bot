import telebot
import yfinance as yf
import os
import datetime
import feedparser
import google.generativeai as genai

# --- GÜVENLİ AYARLAR ---
API_TOKEN = os.getenv("TELEGRAM_TOKEN")
KULLANICI_ID = os.getenv("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# API'yi yapılandırıyoruz
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

bot = telebot.TeleBot(API_TOKEN)

# 1. Analiz Edilecek 12 Ana Kanal
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

def gelismis_yapay_zeka_analizi():
    """Haberleri toplayıp Gemini API'ye derinlemesine analiz ettirir."""
    if not GEMINI_API_KEY:
        return "⚪ API Anahtarı eksik, LLM analizi atlandı."
        
    try:
        # 1. Ham Veriyi (Haberleri) Çek
        rss_url = "https://finance.yahoo.com/news/rssindex"
        feed = feedparser.parse(rss_url)
        
        haberler_metni = ""
        for i, entry in enumerate(feed.entries[:15]):
            haberler_metni += f"{i+1}. {entry.title}\n"
            
        # 2. Yapay Zekaya Yönlendirilecek Stratejik Komut (Prompt Engineering)
        prompt = f"""
        Aşağıda küresel finans piyasalarından alınan son 15 haber başlığı bulunmaktadır. 
        Lütfen makroekonomik verileri okuyabilen üst düzey bir kantitatif fon yöneticisi gibi davran.
        Sadece şu soruya odaklan: "Bu haberlere göre kurumsal fonlar (Smart Money) şu anda parayı hangi sektörlere (teknoloji, emtia, tahvil, güvenli liman vb.) sokuyor ve hangilerinden çıkarıyor?"
        
        Cevabını 3 kısa madde halinde, net, kesin yargılarla ve finansal bir dille Türkçe olarak ver. 
        Gereksiz nezaket veya giriş cümleleri kullanma, direkt analizi yaz.
        
        Gelen Haber Başlıkları:
        {haberler_metni}
        """
        
        # 3. Modeli Çağır ve Analizi Al
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content(prompt)
        
        return response.text
        
    except Exception as e:
        return f"⚪ LLM Analizi Başarısız Oldu: {str(e)}"

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
            else:
                rapor += f"⚪ {isim}: Veri yetersiz.\n"
        except:
            veri_sozlugu[isim] = 0
            rapor += f"⚪ {isim}: Veri çekilemedi.\n"
            
    rapor += "--------------------------------------\n"
    
    # --- YAPAY ZEKA HABER ANALİZİ ---
    rapor += "🧠 *YAPAY ZEKA (LLM) KURUMSAL PARA AKIŞI ANALİZİ:*\n"
    rapor += gelismis_yapay_zeka_analizi() + "\n\n"
    
    # --- DİNAMİK ÇAPRAZ RASYO YORUMLARI ---
    rapor += "🤖 *ALGORİTMA PİYASA YORUMU (RASYOLAR):*\n"
    
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

    # Altın / Bakır Analizi
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
        bot.send_message(message.chat.id, "🤖 Makro analiz, rasyolar ve Gemini Yapay Zeka fon akışı analizi yapılıyor. Lütfen bekleyin...")
        metin = piyasa_verilerini_cek_ve_analiz_et()
        bot.send_message(message.chat.id, metin, parse_mode="Markdown")
    else:
        bot.reply_to(message, "Bu bot kişiye özeldir. Erişim reddedildi.")

if __name__ == "__main__":
    bot.infinity_polling()
