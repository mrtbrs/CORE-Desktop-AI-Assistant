import pyautogui

def show_desktop() -> str:
    """
    Tüm açık pencereleri anında simge durumuna küçültür ve masaüstünü gösterir (Win+D).
    Tekrar çağrıldığında pencereleri eski haline getirir.
    """
    print("C.O.R.E. İşlem: Masaüstü görünümüne geçiliyor...")
    pyautogui.hotkey('win', 'd')
    return "Tüm pencereler gizlendi ve masaüstü gösterildi efendim."

def align_window(direction: str) -> str:
    """
    Aktif olan pencereyi ekranın sağına, soluna veya tam ekrana hizalar.
    Parametreler: 'left', 'right', 'up' (tam ekran), 'down' (küçült)
    """
    print(f"C.O.R.E. İşlem: Pencere hizalanıyor -> {direction}")
    
    if direction == 'left':
        pyautogui.hotkey('win', 'left')
        mesaj = "sola hizalandı"
    elif direction == 'right':
        pyautogui.hotkey('win', 'right')
        mesaj = "sağa hizalandı"
    elif direction == 'up':
        pyautogui.hotkey('win', 'up')
        mesaj = "tam ekran yapıldı"
    elif direction == 'down':
        pyautogui.hotkey('win', 'down')
        mesaj = "aşağıya küçültüldü"
    else:
        return "Geçersiz yön komutu. Lütfen 'left', 'right', 'up' veya 'down' kullanın."
        
    return f"Aktif pencere başarıyla {mesaj} efendim."