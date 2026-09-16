import webbrowser
from urllib.parse import quote_plus

def search_flights(departure: str, destination: str) -> str:
    """
    Kalkış ve varış noktasına göre Google Uçuşlar (Flights) üzerinden 
    tüm havayollarını (THY, Pegasus vb.) karşılaştırmalı olarak açar.
    """
    print(f"C.O.R.E. İşlem: Uçuşlar aranıyor -> Kalkış: {departure}, Varış: {destination}...")
    
    # Google Flights doğrudan rota parametresiyle arama sayfası
    query = f"{departure} - {destination} uçak bileti"
    url = f"https://www.google.com/travel/flights?q={quote_plus(query)}"
    
    webbrowser.open(url)
    
    return f"{departure} ve {destination} arası tüm havayolu firmalarının biletleri Google Uçuşlar üzerinde listelendi efendim."