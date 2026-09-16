import os
import pyautogui
import urllib.parse

def open_new_tab(url_or_search: str) -> str:
    """
    Tarayıcıda yeni bir sekme açar (Doğrudan Chrome'u hedefler).
    """
    print(f"C.O.R.E. İşlem: Yeni sekme açılıyor -> {url_or_search}")
    
    # Eğer doğrudan bir web adresi değilse Google araması yapacak formata çevir
    if not url_or_search.startswith("http"):
        # Boşlukları ve Türkçe karakterleri URL formatına uygun hale getiriyoruz
        safe_query = urllib.parse.quote_plus(url_or_search)
        url = f"https://www.google.com/search?q={safe_query}"
    else:
        url = url_or_search
        
    # Windows'ta Chrome'u doğrudan ve hiç beklemeden başlatmanın en hızlı yolu
    try:
        os.system(f'start chrome "{url}"')
    except Exception:
        # Eğer sistemde Chrome bulunamazsa varsayılan tarayıcıyı zorla
        import webbrowser
        webbrowser.open_new_tab(url)
        
    return f"Yeni sekme açıldı ve {url_or_search} sayfasına yönlendirildi efendim."

def switch_browser_tab(direction: str) -> str:
    """Açık olan sekmeler arasında ileri veya geri geçiş yapar."""
    print(f"C.O.R.E. İşlem: Sekmeler arası geçiş yapılıyor ({direction})...")
    
    if direction == "next":
        pyautogui.hotkey('ctrl', 'tab')
    elif direction == "previous":
        pyautogui.hotkey('ctrl', 'shift', 'tab')
    else:
        return "Geçersiz yön parametresi. 'next' veya 'previous' kullanmalısınız."
        
    return f"Tarayıcı sekmesi başarıyla değiştirildi."

def refresh_page() -> str:
    """Aktif tarayıcı sekmesini yeniler (F5)."""
    print("C.O.R.E. İşlem: Sayfa yenileniyor...")
    pyautogui.press('f5')
    return "Aktif sekme yenilendi efendim."