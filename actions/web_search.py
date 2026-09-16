import webbrowser
import urllib.parse

def search_web(query: str):
    """Kullanıcı hava durumu, maç sonucu, haber veya genel bir bilgi sorduğunda web araması yapar."""
    print(f"C.O.R.E. İşlem: Ekrana getiriliyor -> '{query}'...")
    try:
        # Sorguyu Google'da aratacak linke çevirir ve tarayıcıda açar
        url = f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"
        webbrowser.open(url)
        return "İstediğiniz bilgileri ekrana getirdim efendim."
    except Exception as e:
        return "Tarayıcıyı açarken bir hata oluştu."