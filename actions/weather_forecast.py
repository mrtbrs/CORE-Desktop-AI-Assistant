import urllib.request
import urllib.parse

def get_weather(city: str = "Torbalı") -> str:
    """
    Belirtilen şehrin anlık hava durumunu getirir.
    Şehir parametresi verilmezse varsayılan konumu kullanır.
    """
    print(f"C.O.R.E. İşlem: {city} için hava durumu kontrol ediliyor...")
    
    # Hızlı sonuç almak için wttr.in servisini kullanıyoruz (format=%C+%t sadece durum ve sıcaklığı getirir)
    safe_city = urllib.parse.quote_plus(city)
    url = f"https://wttr.in/{safe_city}?format=%C+%t" 
    
    try:
        # Ağı tıkamaması için maksimum 2 saniye bekler
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=2) as response:
            result = response.read().decode('utf-8').strip()
            
        return f"{city} için anlık hava durumu verisi: '{result}'. Lütfen bu bilgiyi doğal, akıcı ve profesyonel bir Türkçe ile (örneğin: hava bulutlu ve 25 derece gibi) kullanıcıya söyle."
    except Exception:
        return "Şu an hava durumu sunucusuna çok geç yanıt verdiği için bağlantı kesildi, ancak asistan aktif."