import os

# Masaüstü yolunu otomatik bul
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

def read_file_content(file_name: str) -> str:
    """
    Masaüstündeki belirtilen metin dosyasının içeriğini okur ve yapay zekaya iletir.
    Özellikle metin özetleme ve analiz için kullanılır.
    """
    print(f"C.O.R.E. İşlem: '{file_name}' dosyasının içeriği okunuyor...")
    
    # Eğer uzantı belirtilmemişse otomatik olarak .txt arayalım
    path = os.path.join(DESKTOP_PATH, file_name)
    if not os.path.exists(path):
        path_with_txt = os.path.join(DESKTOP_PATH, file_name + '.txt')
        if os.path.exists(path_with_txt):
            path = path_with_txt
        else:
            return f"Hata: Masaüstünde '{file_name}' adında bir dosya bulunamadı efendim."
            
    try:
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
            
        # Eğer dosya çok uzunsa (token sınırını aşmamak için) sadece ilk 5000 karakterini al
        if len(content) > 5000:
            content = content[:5000] + "\n... [Sistem Notu: Metin çok uzun olduğu için sonu kırpıldı]"
            
        return f"'{file_name}' dosyasının içeriği:\n\n{content}"
    except Exception as e:
        return f"Dosya okunurken sistemsel bir hata oluştu: {str(e)}"