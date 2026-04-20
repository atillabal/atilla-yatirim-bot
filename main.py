import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import requests
import datetime
import os

# --- GÜVENLİK AYARI (GITHUB SECRETS) ---
# Kod artık tokenları açıkça yazmanızı istemez, sistemden çeker.
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

varliklar = {
    "1. ABD Borsası (S&P 500)": "^GSPC",
    "2. ABD 10Y Tahvil": "^TNX",
    "3. Güvenli Liman (Altın)": "GC=F",
    "4. Endüstriyel (Bakır)": "HG=F",
    "5. Enerji (Petrol)": "CL=F",
    "6. Dolar Endeksi (DXY)": "DX-Y.NYB"
}

def analiz_motoru():
    rapor = f"🛡️ *STRATEJİK PİYASA RAPORU* ({datetime.date.today()})\n"
    rapor += "--------------------------------------\n"
    
    for isim, sembol in varliklar.items():
        try:
            # 200 günlük SMA için en az 260 günlük veri çekiyoruz
            data = yf.download(sembol, period="260d", progress=False)
            if len(data) >= 200:
                # Ortalamaları Hesapla
                data['SMA_50'] = data['Close'].rolling(window=50).mean()
                data['SMA_200'] = data['Close'].rolling(window=200).mean()
                
                bugun = data.iloc[-1]
                dun = data.iloc[-2]
                
                # Günlük Değişim
                degisim = ((bugun['Close'] - dun['Close']) / dun['Close']) * 100
                ikon = "🟢" if degisim > 0 else "🔴"
                rapor += f"{ikon} {isim}: %{degisim:.2f}\n"
                
                # --- ALTIN VURUŞ (GOLDEN CROSS) ANALİZİ ---
                # 50, 200'ü yukarı keserse = Boğa (Yükseliş) Sezonu
                if bugun['SMA_50'] > bugun['SMA_200'] and dun['SMA_50'] <= dun['SMA_200']:
                    rapor += f"   🌟 *GOLDEN CROSS:* {isim.split()[1]} uzun vadeli yükseliş trendine girdi!\n"
                
                # 50, 200'ü aşağı keserse = Ölüm Kavşağı (Death Cross)
                elif bugun['SMA_50'] < bugun['SMA_200'] and dun['SMA_50'] >= dun['SMA_200']:
                    rapor += f"   💀 *DEATH CROSS:* {isim.split()[1]} için tehlike çanları çalıyor, düşüş derinleşebilir.\n"
                    
                # Mevcut trend durumu
                elif bugun['SMA_50'] > bugun['SMA_200']:
                    rapor += "   📈 *Trend:* Pozitif (Boğa)\n"
                else:
                    rapor += "   📉 *Trend:* Negatif (Ayı)\n"
                    
        except Exception as e:
            rapor += f"⚪ {isim}: Hata oluştu.\n"

    rapor += "--------------------------------------\n"
    return rapor

# Grafik ve Gönderim fonksiyonları önceki kod ile aynı kalacaktır...
def kiyaslama_grafigi_ciz():
    sp500 = yf.download("^GSPC", period="1mo", progress=False)['Close']
    dxy = yf.download("DX-Y.NYB", period="1mo", progress=False)['Close']
    sp500_norm = (sp500 / sp500.iloc[0]) * 100
    dxy_norm = (dxy / dxy.iloc[0]) * 100
    plt.figure(figsize=(10, 5))
    plt.plot(sp500_norm.index, sp500_norm, label="Borsa", color='blue')
    plt.plot(dxy_norm.index, dxy_norm, label="Dolar", color='green')
    plt.title("Borsa vs Dolar (1 Aylık Kıyas)")
    plt.savefig("kiyaslama.png")
    plt.close()
    return "kiyaslama.png"

def telegram_gonder(mesaj, foto):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Hata: API Anahtarları bulunamadı!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    with open(foto, 'rb') as f:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "caption": mesaj, "parse_mode": "Markdown"}, files={"photo": f})
    os.remove(foto)

if __name__ == "__main__":
    rapor = analiz_motoru()
    grafik = kiyaslama_grafigi_ciz()
    telegram_gonder(rapor, grafik)
