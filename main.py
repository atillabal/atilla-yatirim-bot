import telebot
import yfinance as yf
import os
import matplotlib.pyplot as plt
import datetime

# --- GÜVENLİ AYARLAR ---
# Bu değerler kodun içine yazılmaz, GitHub Secrets üzerinden çekilir.
API_TOKEN = os.getenv("TELEGRAM_TOKEN")
KULLANICI_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(API_TOKEN)

def analiz_hazirla():
    # En çok para akan 3 ana kanalı örnek alıyoruz
    data = yf.download("GC=F ^GSPC DX-Y.NYB", period="2d", progress=False)['Close']
    
    altin_degisim = ((data['GC=F'].iloc[-1] - data['GC=F'].iloc[-2]) / data['GC=F'].iloc[-2]) * 100
    borsa_degisim = ((data['^GSPC'].iloc[-1] - data['^GSPC'].iloc[-2]) / data['^GSPC'].iloc[-2]) * 100
    
    rapor = f"📊 *ATİLLA YATIRIM ANALİZİ* ({datetime.datetime.now().strftime('%H:%M')})\n\n"
    rapor += f"{'🟢' if altin_degisim > 0 else '🔴'} Altın (Ons): %{altin_degisim:.2f}\n"
    rapor += f"{'🟢' if borsa_degisim > 0 else '🔴'} S&P 500: %{borsa_degisim:.2f}\n"
    rapor += "\n💡 Not: /rapor komutuyla anlık analiz alabilirsin."
    return rapor

@bot.message_handler(commands=['start', 'rapor'])
def handle_commands(message):
    # Sadece sizin ID'nizden gelen mesajlara cevap verir
    if str(message.from_user.id) == str(KULLANICI_ID):
        bot.send_message(message.chat.id, "Analiz hazırlanıyor...")
        metin = analiz_hazirla()
        bot.send_message(message.chat.id, metin, parse_mode="Markdown")
    else:
        bot.reply_to(message, "Bu bot kişiye özeldir, erişim reddedildi.")

if __name__ == "__main__":
    print("Bot yayına başladı...")
    bot.infinity_polling()