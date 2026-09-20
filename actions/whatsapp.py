import webbrowser
import time
from urllib.parse import quote

import pyautogui

# C.O.R.E. için mini bir rehber.
REHBER = {
    "x": "+90",
    "y": "+90",
    "z": "+90",
    "w": "+90",
    "t": "+90",
    
}


def send_whatsapp_message(kisi: str, mesaj: str) -> str:
    """
    WhatsApp Web üzerinden belirtilen kişiye mesaj gönderir ve işlemi bitince sekmeyi temizler.
    """
    print(f"C.O.R.E. İşlem: WhatsApp mesajı hazırlanıyor -> Alıcı: {kisi}")

    telefon_numarasi = REHBER.get(kisi.lower(), kisi)
    telefon_numarasi = telefon_numarasi.replace(" ", "")

    url = f"https://web.whatsapp.com/send?phone={telefon_numarasi}&text={quote(mesaj)}"
    webbrowser.open(url)

    # Sayfanın yüklenmesi için bekle
    time.sleep(15)

    # Mesajı gönder (Enter)
    pyautogui.press("enter")

    # Mesajın sunucuya iletilmesi için 2 saniye ek bekleme
    time.sleep(2)

    # İşimiz bitti, açık olan bu son sekmeyi kapat (Ctrl+W)
    print("C.O.R.E. İşlem: Sekme temizleniyor...")
    pyautogui.hotkey("ctrl", "w")

    return f"WhatsApp üzerinden {kisi} adlı kişiye mesaj iletildi ve sekme kapatıldı efendim."
