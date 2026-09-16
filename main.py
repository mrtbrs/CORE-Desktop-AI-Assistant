import os
import keyboard


_command_handler = None

def set_command_handler(handler):
    """
    Global kısayolun kullanacağı komut işleyicisini kaydeder.
    """
    global _command_handler
    _command_handler = handler

def on_activate():
    """
    Kısayol (Ctrl + Space) basıldığında tetiklenir.
    """
    print("\n[BİLDİRİM] C.O.R.E. Kısayol ile Uyandırıldı! Dinleniyor...")
    if _command_handler is not None:
        _command_handler()

def start_global_hotkey():
    """
    Uygulama arkada çalışırken kısayolları (hotkey) dinler.
    """
    keyboard.add_hotkey('ctrl+space', on_activate)
    keyboard.wait()

def run_core():
    """
    GUI tarafından geriye dönük uyumluluk için çağrılan başlatma noktası.

    Sesli dinleme GUI içindeki ContinuousListenWorker tarafından yönetilir.
    """
    return None

if __name__ == "__main__":
    start_global_hotkey()