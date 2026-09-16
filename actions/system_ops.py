import pyautogui
import webbrowser
import time
import platform
import os
from urllib.parse import quote_plus

def open_application(app_name: str):
    """Kullanıcının istediği bir masaüstü uygulamasını açar."""
    print(f"C.O.R.E. İşlem: {app_name} açılıyor...")
    if platform.system() == "Windows":
        pyautogui.press("win")
        time.sleep(0.5)
        pyautogui.write(app_name, interval=0.05)
        time.sleep(0.5)
        pyautogui.press("enter")
        return f"{app_name} başlatıldı efendim."
    return "Bu özellik şu an sadece Windows sistemlerde aktiftir."

def open_youtube_music():
    """YouTube Music platformunu doğrudan varsayılan tarayıcıda açar."""
    print("C.O.R.E. İşlem: YouTube Music açılıyor...")
    webbrowser.open("https://music.youtube.com")
    return "YouTube Music açıldı efendim."

def open_tod():
    """TOD (beIN Connect) platformunu varsayılan tarayıcıda açar."""
    print("C.O.R.E. İşlem: TOD açılıyor...")
    webbrowser.open("https://www.todtv.com.tr")
    return "TOD platformu açıldı efendim. İyi seyirler."

def play_youtube_video(query: str):
    """YouTube üzerinde arama yapıp ilk video sonucunu açar."""
    print(f"C.O.R.E. İşlem: YouTube üzerinde aranıyor -> '{query}'...")
    url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
    webbrowser.open(url)
    return f"YouTube üzerinde '{query}' aratıldı efendim."

def mute_volume():
    """Bilgisayarın sesini kapatır veya açar."""
    print("C.O.R.E. İşlem: Ses durumu değiştiriliyor...")
    pyautogui.press("volumemute")
    return "Sistem sesi kapatıldı."

def volume_up():
    """Bilgisayarın sesini artırır."""
    print("C.O.R.E. İşlem: Ses artırılıyor...")
    for _ in range(5): 
        pyautogui.press("volumeup")
    return "Ses seviyesi artırıldı."

def close_tab():
    """Aktif tarayıcı sekmesini kapatır."""
    print("C.O.R.E. İşlem: Sekme kapatılıyor...")
    pyautogui.hotkey("ctrl", "w")
    return "Sekme kapatıldı."

def full_screen():
    """Ekranı veya videoyu tam ekran moduna alır ya da çıkarır."""
    print("C.O.R.E. İşlem: Tam ekran modu...")
    pyautogui.press("f11")
    return "Tam ekran uygulandı."

def minimize_window():
    """Mevcut pencereyi simge durumuna küçültür veya masaüstünü gösterir."""
    print("C.O.R.E. İşlem: Pencereler küçültülüyor...")
    pyautogui.hotkey("win", "d")
    return "Masaüstüne dönüldü."

def take_screenshot():
    """Tam ekran görüntüsü alıp kullanıcının masaüstüne otomatik kaydeder."""
    print("C.O.R.E. İşlem: Ekran görüntüsü alınıp kaydediliyor...")
    try:
        # Masaüstü yolunu bul
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        # Benzersiz bir dosya ismi oluştur (örn: CORE_SS_1694...png)
        file_name = f"CORE_SS_{int(time.time())}.png"
        save_path = os.path.join(desktop_path, file_name)
        
        # Tam ekran görüntüsünü al ve kaydet
        screenshot = pyautogui.screenshot()
        screenshot.save(save_path)
        
        return "Ekran görüntüsü başarıyla alındı ve masaüstünüze kaydedildi."
    except Exception as e:
        print(f"Ekran Görüntüsü Hatası: {e}")
        return "Ekran görüntüsü alınırken bir sorun oluştu."