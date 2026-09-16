import threading
import time
from plyer import notification
from core.mouth import speak

def _countdown_thread(seconds: int, note: str):
    time.sleep(seconds)
    # Windows masaüstü bildirimi
    try:
        notification.notify(
            title="C.O.R.E. Hatırlatıcı",
            message=note,
            app_name="C.O.R.E.",
            timeout=10
        )
    except Exception as e:
        print(f"Bildirim Hatası: {e}")
    
    # Sesli uyarı
    speak(f"Efendim, süreniz doldu: {note}")

def set_reminder(minutes: float, note: str = "Zaman doldu!") -> str:
    """Belirtilen dakika sonra sesli ve pencereli hatırlatıcı kurar."""
    print(f"C.O.R.E. İşlem: {minutes} dakikalık hatırlatıcı ayarlanıyor -> '{note}'...")
    total_seconds = int(minutes * 60)
    
    # Ana programın donmaması için arka plan iş parçacığı (threading) kullanıyoruz
    t = threading.Thread(target=_countdown_thread, args=(total_seconds, note), daemon=True)
    t.start()
    
    return f"{minutes} dakika sonra '{note}' için hatırlatıcı ayarlandı efendim."