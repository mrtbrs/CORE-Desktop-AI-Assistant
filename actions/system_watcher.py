import psutil
import time
import threading
from plyer import notification

# İzleyici durumunu kontrol eden global değişken
is_monitoring = False

def _monitor_loop():
    """Arka planda sessizce çalışan izleme döngüsü."""
    global is_monitoring
    while is_monitoring:
        try:
            # 1. İşlemci Yükü Kontrolü
            cpu_usage = psutil.cpu_percent(interval=1)
            if cpu_usage > 90:
                notification.notify(
                    title="C.O.R.E. Uyarı: Yüksek İşlemci Yükü",
                    message=f"İşlemci kullanımı %{cpu_usage} seviyesine ulaştı. Sistem zorlanıyor.",
                    app_name="C.O.R.E.",
                    timeout=5
                )
            
            # 2. Pil Seviyesi Kontrolü
            battery = psutil.sensors_battery()
            if battery and not battery.power_plugged and battery.percent < 20:
                notification.notify(
                    title="C.O.R.E. Uyarı: Düşük Pil",
                    message=f"Pil seviyesi %{battery.percent}. Lütfen bilgisayarı şarja takın.",
                    app_name="C.O.R.E.",
                    timeout=5
                )
        except Exception as e:
            print(f"Gözcü Hatası: {e}")
        
        # Her 60 saniyede bir sistemi kontrol et (bilgisayarı yormamak için)
        time.sleep(60)

def start_system_watcher() -> str:
    """Arka planda sistemi (CPU, Pil) sürekli izlemeyi başlatır."""
    global is_monitoring
    if is_monitoring:
        return "Sistem izleme (Gözcü) zaten aktif durumda efendim."
    
    is_monitoring = True
    t = threading.Thread(target=_monitor_loop, daemon=True)
    t.start()
    print("C.O.R.E. İşlem: Sistem gözcüsü başlatıldı.")
    return "Arka plan sistem izleyicisi başlatıldı. Kritik durumlarda (düşük pil, yüksek CPU) sizi uyaracağım."

def stop_system_watcher() -> str:
    """Arka planda çalışan sistem izlemeyi (Gözcü) durdurur."""
    global is_monitoring
    if not is_monitoring:
        return "Sistem izleme şu an zaten kapalı efendim."
    
    is_monitoring = False
    print("C.O.R.E. İşlem: Sistem gözcüsü durduruldu.")
    return "Sistem izleme devredışı bırakıldı."