import webbrowser

def launch_game_platform(platform_name: str) -> str:
    """
    Belirtilen oyun platformunu (Steam, Epic Games vb.) anında başlatır.
    """
    print(f"C.O.R.E. İşlem: Oyun platformu başlatılıyor -> {platform_name}")
    platform = platform_name.lower()
    
    try:
        if "steam" in platform:
            # Python'u dondurmadan doğrudan protokolü tetikler
            webbrowser.open("steam://open/main")
            return "Steam platformu başarıyla başlatıldı efendim."
        elif "epic" in platform:
            webbrowser.open("com.epicgames.launcher://")
            return "Epic Games Launcher başlatıldı efendim."
        else:
            return f"Sistemde '{platform_name}' adında desteklenen bir platform bulunamadı."
    except Exception as e:
        return f"Platform başlatılırken hata oluştu: {str(e)}"

def check_game_updates() -> str:
    """
    Oyun güncellemelerini yönetmek için Steam'in İndirmeler sayfasını anında açar.
    """
    print("C.O.R.E. İşlem: Oyun güncellemeleri sayfası açılıyor...")
    try:
        webbrowser.open("steam://open/downloads")
        return "Steam indirmeler ve güncellemeler sayfası ekrana getirildi efendim."
    except Exception as e:
        return f"Güncellemeler sayfası açılırken bir hata oluştu: {str(e)}"