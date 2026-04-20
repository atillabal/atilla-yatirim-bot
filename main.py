import telebot
import yfinance as yf
import os
import datetime

# --- GÜVENLİ AYARLAR ---
API_TOKEN = os.getenv("TELEGRAM_TOKEN")
KULLANICI_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(API_TOKEN)

# 1. Analiz Edilecek 10 Ana Kanal ve Yahoo Finance Sembolleri
varliklar = {
    "1. ABD Borsası (S&P 500)": "^GSPC",
    "2. ABD 10Y Tahvil (Faiz)": "^TNX",
    "3. Güvenli Liman (Altın)": "GC=F",
    "4. Endüstriyel (Bakır)": "HG=F",
    "5. Enerji (Petrol)": "CL=F",
    "6. Dolar Endeksi (DXY)": "DX-Y.NYB",
    "7. Kripto (Bitcoin)": "BTC-USD",
    "8. Tarım (Buğday)": "ZW=F",
    "9. Gelişen Piyasalar (EEM)": "EEM",
    "10. Şirket Tahvilleri (LQD)": "LQD"
}

def piyasa_verilerini_cek_ve_analiz_et():
    rapor = f"🌍 *KÜRESEL MAKRO PİYASA RAPORU* ({datetime.datetime.now().strftime('%H:%M')})\n"
    rapor += "--------------------------------------\n"
    
    veri_sozlugu = {}

    # Verileri çekme ve hesaplama döngüsü
    for isim, sembol in varliklar.items():
        try:
            # Doğru Uygulama: Hafta sonu NaN hatası almamak için 5 günlük veri çekip boşlukları siliyoruz
            data = yf.download(sembol, period="5d", progress=False)['Close'].dropna()
            
            if len(data) >= 2:
                dunku_kapanis = data.iloc[-2].item()
                bugunku_kapanis = data.iloc[-1].item()
                
                # Yüzdelik hesaplama
                degisim_yuzdesi = ((bugunku_kapanis - dunku_kapanis) / dunku_kapanis) * 100
                veri_sozlugu[isim] = degisim_yuzdesi
                
                # Görsel formatlama (Yeşil/Kırmızı İkonlar)
                ikon = "🟢" if degisim_yuzdesi > 0 else "🔴"
                rapor += f"{ikon} {isim}: %{degisim_yuzdesi:.2f}\n"
            else:
                rapor += f"⚪ {isim}: Veri okunamadı.\n"
        except Exception as e:
            rapor += f"⚪ {isim}: Hata\n"
            
    rapor += "--------------------------------------\n"
    rapor += "*GÜNLÜK PİYASA YORUMU (ALGORİTMA):*\n"
    
    # İleri Düzey Çapraz Rasyo Analizi
    if veri_sozlugu.get("6. Dolar Endeksi (DXY)", 0) > 0.5:
        rapor += "⚠️ *Dolar Endeksi (DXY) güçleniyor.* Bu durum diğer tüm emtia ve hisse senetleri üzerinde satış baskısı yaratabilir.\n\n"
        
    if veri_sozlugu.get("4. Endüstriyel (Bakır)", 0) > 1.0 and veri_sozlugu.get("3. Güvenli Liman (Altın)", 0) < 0:
        rapor += "🚀 *Bakır yükseliyor, Altın düşüyor.* Sermaye 'korku' psikolojisinden çıkıp 'ekonomik büyüme ve risk' kanallarına akıyor.\n\n"
        
    if veri_sozlugu.get("2. ABD 10Y Tahvil (Faiz)", 0) > 2.0 and veri_sozlugu.get("1. ABD Borsası (S&P 500)", 0) < 0:
        rapor += "📉 *Tahvil faizlerinde sert yükseliş var.* Kurumsal para borsadan çıkıp garantili getiri sunan tahvillere kaçıyor.\n\n"
        
    if not any(v > 0.5 for v in veri_sozlugu.values()) and not any(v < -0.5 for v in veri_sozlugu.values()):
        rapor += "⚖️ Piyasada bugün yatay ve sakin bir seyir hakim. Önemli bir sermaye rotasyonu gözlemlenmedi.\n"

    return rapor

@bot.message_handler(commands=['start', 'rapor'])
def handle_commands(message):
    # Güvenlik kontrolü
    if str(message.from_user.id) == str(KULLANICI_ID):
        bot.send_message(message.chat.id, "Makro analiz ve çapraz rasyolar hesaplanıyor...")
        metin = piyasa_verilerini_cek_ve_analiz_et()
        bot.send_message(message.chat.id, metin, parse_mode="Markdown")
    else:
        bot.reply_to(message, "Bu bot kişiye özeldir. Erişim reddedildi.")

if __name__ == "__main__":
    print("Bot yayına başladı...")
    bot.infinity_polling()
