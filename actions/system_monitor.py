import psutil

def get_system_status() -> str:
    """Bilgisayarın anlık işlemci (CPU), bellek (RAM) ve pil durumunu raporlar."""
    print("C.O.R.E. İşlem: Donanım durumu taranıyor...")
    try:
        cpu_usage = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        ram_usage = ram.percent
        
        battery = psutil.sensors_battery()
        battery_text = ""
        if battery:
            plugged = "Şarja takılı" if battery.power_plugged else "Pilde çalışıyor"
            battery_text = f", Pil: %{battery.percent} ({plugged})"
            
        report = f"İşlemci yükü: %{cpu_usage}, RAM kullanımı: %{ram_usage}{battery_text}."
        return report
    except Exception as e:
        print(f"Sistem İzleme Hatası: {e}")
        return "Donanım bilgileri alınırken bir hata oluştu."