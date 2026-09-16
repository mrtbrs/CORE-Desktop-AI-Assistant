import os
import shutil

# Masaüstü yolunu otomatik olarak algıla
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

def create_folder(folder_name: str) -> str:
    """Masaüstünde yeni bir klasör oluşturur."""
    print(f"C.O.R.E. İşlem: '{folder_name}' klasörü oluşturuluyor...")
    path = os.path.join(DESKTOP_PATH, folder_name)
    try:
        os.makedirs(path, exist_ok=True)
        return f"Masaüstünde '{folder_name}' adında bir klasör oluşturuldu efendim."
    except Exception as e:
        return f"Klasör oluşturulurken hata oluştu: {str(e)}"

def write_to_file(file_name: str, content: str) -> str:
    """Masaüstünde bir metin dosyası oluşturur ve içine yazı yazar."""
    print(f"C.O.R.E. İşlem: '{file_name}' dosyası yazılıyor...")
    # Dosya adında uzantı yoksa otomatik .txt ekle
    if not file_name.endswith('.txt'):
        file_name += '.txt'
        
    path = os.path.join(DESKTOP_PATH, file_name)
    try:
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
        return f"Masaüstünde '{file_name}' dosyası oluşturuldu ve içine metin yazıldı."
    except Exception as e:
        return f"Dosyaya yazılırken hata oluştu: {str(e)}"

def delete_item(item_name: str) -> str:
    """Masaüstündeki belirtilen dosyayı veya klasörü siler."""
    print(f"C.O.R.E. İşlem: '{item_name}' siliniyor...")
    
    path = os.path.join(DESKTOP_PATH, item_name)
    
    # Tam isimle bulunamazsa sonuna .txt ekleyip tekrar dene
    if not os.path.exists(path):
        path_with_txt = os.path.join(DESKTOP_PATH, item_name + '.txt')
        if os.path.exists(path_with_txt):
            path = path_with_txt
        else:
            return f"Masaüstünde '{item_name}' adında bir dosya veya klasör bulunamadı efendim."
            
    try:
        if os.path.isfile(path):
            os.remove(path)
            return f"'{item_name}' adlı dosya silindi."
        elif os.path.isdir(path):
            shutil.rmtree(path)
            return f"'{item_name}' adlı klasör silindi."
    except Exception as e:
        return f"Silme işlemi başarısız oldu: {str(e)}"