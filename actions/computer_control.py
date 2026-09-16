import pyautogui

def scroll_screen(direction: str, amount: int = 500) -> str:
    """
    Fare tekerleği ile ekranı aşağı veya yukarı kaydırır.
    Yön (direction) 'up' (yukarı) veya 'down' (aşağı) olmalıdır.
    """
    print(f"C.O.R.E. İşlem: Ekran {direction} yönüne kaydırılıyor...")
    if direction == "down":
        pyautogui.scroll(-amount)
    elif direction == "up":
        pyautogui.scroll(amount)
    return f"Ekran {direction} yönüne kaydırıldı."

def click_mouse(button: str = "left", clicks: int = 1) -> str:
    """
    Mevcut fare konumunda tıklama yapar. 
    button: 'left' (sol tık) veya 'right' (sağ tık) olabilir.
    clicks: Tıklama sayısı (çift tıklama için 2).
    """
    print(f"C.O.R.E. İşlem: Fare ile {button} tıklama yapılıyor...")
    pyautogui.click(button=button, clicks=clicks)
    return f"Fare ile {clicks} kez {button} tıklandı."

def press_key(key_name: str) -> str:
    """
    Belirtilen klavye tuşuna basar (örn: 'space', 'enter', 'esc', 'backspace').
    """
    print(f"C.O.R.E. İşlem: '{key_name}' tuşuna basılıyor...")
    pyautogui.press(key_name)
    return f"Klavye üzerinden {key_name} tuşuna basıldı."

def write_text(text: str) -> str:
    """
    Klavyeyi kullanarak belirtilen metni fiziksel olarak yazar.
    """
    print(f"C.O.R.E. İşlem: Metin yazılıyor -> '{text}'")
    pyautogui.write(text, interval=0.05)
    return f"Metin başarıyla yazıldı."