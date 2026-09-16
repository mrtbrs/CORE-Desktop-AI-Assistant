import pyautogui
import os

SCREENSHOT_PATH = "actions/temp_screen.png"

def capture_screen_description() -> str:
    """Ekranın anlık görüntüsünü yakalar ve analiz için kaydeder."""
    print("C.O.R.E. İşlem: Ekran görüntüsü yakalanıyor...")
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(SCREENSHOT_PATH)
        return "Ekran görüntüsü başarıyla alındı. Görüntü analiz ediliyor."
    except Exception as e:
        print(f"Ekran Yakalama Hatası: {e}")
        return "Ekran görüntüsü alınırken bir sorun oluştu."