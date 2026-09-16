import webbrowser
from urllib.parse import quote_plus

def search_bus_ticket(departure: str, destination: str) -> str:
    """
    Kalkış ve varış noktasına göre otobüs bileti seferlerini arar.
    """
    print(f"C.O.R.E. İşlem: Otobüs seferleri aranıyor -> Kalkış: {departure}, Varış: {destination}...")
    
    # Arama sorgusunu oluştur
    query = f"{departure} {destination} otobüs bileti"
    url = f"https://www.google.com/search?q={quote_plus(query)}"
    
    webbrowser.open(url)
    
    return f"{departure} ve {destination} arası otobüs bileti seferleri tarayıcıda listelendi efendim."