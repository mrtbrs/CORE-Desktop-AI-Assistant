import os
import shutil
import subprocess
import sys

def build_core():
    print(">> C.O.R.E. Sistem Derleyicisi Başlatılıyor...")
    
    if os.path.exists("build"):
        shutil.rmtree("build", ignore_errors=True)
                
    print(">> PyInstaller paketleme işlemi başlıyor. Lütfen bekleyin...")
    
    # PyInstaller derleme komutları
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",      
        "--icon=icon.ico",
        "--name=CORE",
        "--distpath=.",    
        
        # Veri dosyaları
        "--add-data=orbitron.ttf;.",
        "--add-data=icon.ico;.",
        
        # PyInstaller gizli importlar (GPUtil silindi)
        "--hidden-import=wmi",
        "--hidden-import=win32com",
        "--hidden-import=edge_tts",
        "--hidden-import=google.generativeai",
        "--hidden-import=speech_recognition",
        "--hidden-import=psutil",
        
        "gui.py"
    ]

    subprocess.run(pyinstaller_cmd)

    if os.path.exists("build"):
        shutil.rmtree("build", ignore_errors=True)
    if os.path.exists("CORE.spec"):
        os.remove("CORE.spec")

    print(">> İŞLEM KUSURSUZ TAMAMLANDI! CORE.exe ana dizininde hazır.")

if __name__ == "__main__":
    build_core()