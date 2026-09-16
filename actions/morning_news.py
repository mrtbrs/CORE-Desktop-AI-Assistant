import urllib.request
import xml.etree.ElementTree as ET
import datetime
import locale
import json

def fetch_rss_titles(url: str, limit: int = 3) -> list:
    """Belirtilen RSS kaynağından hızlıca haber başlıklarını çeker."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=2) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            return [item.find('title').text for item in root.findall('./channel/item')[:limit]]
    except Exception:
        return []

def get_morning_summary() -> str:
    """Arayüz (settings.json) ayarlarına göre dinamik sabah özeti oluşturur."""
    print("C.O.R.E. İşlem: Dinamik sabah özeti hazırlanıyor...")
    
    # 1. Ayarları Oku
    settings = {"morning_brief": {"date_time": True, "weather": True, "news": True, "sports": False}}
    try:
        with open('settings.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            if "morning_brief" in data:
                settings["morning_brief"] = data["morning_brief"]
    except Exception:
        pass

    brief_config = settings["morning_brief"]
    rapor_parcalari = []
    
    # 2. İstenen Verileri Topla
    if brief_config.get("date_time", True):
        try:
            locale.setlocale(locale.LC_TIME, '') 
        except:
            pass
        now = datetime.datetime.now()
        rapor_parcalari.append(f"Tarih: {now.strftime('%d %B %Y, %A')}\nSaat: {now.strftime('%H:%M')}")
        
    if brief_config.get("weather", True):
        try:
            from actions.weather_forecast import get_weather
            hava = get_weather("Torbalı") # İstersen burayı da settings.json'a bağlayabilirsin
            rapor_parcalari.append(f"Hava Durumu: {hava}")
        except Exception:
            pass
            
    if brief_config.get("news", True):
        gundem = fetch_rss_titles("https://www.trthaber.com/manset_articles.rss", 3)
        if gundem:
            rapor_parcalari.append("Gündem Haberleri:\n" + "\n".join([f"- {h}" for h in gundem]))
            
    if brief_config.get("sports", False):
        spor = fetch_rss_titles("https://www.trtspor.com.tr/rss/anasayfa.xml", 3)
        if spor:
            rapor_parcalari.append("Spor Gelişmeleri:\n" + "\n".join([f"- {s}" for s in spor]))

    final_rapor = "\n\n".join(rapor_parcalari)
    
    return (
        f"{final_rapor}\n\n"
        "Senin Görevin: Kullanıcıyı çok profesyonel ve enerjik bir şekilde selamla. "
        "Yukarıdaki verileri akıcı bir radyocu veya asistan edasıyla özetle. "
        "Bugün için hazır olduğunu belirt."
    )