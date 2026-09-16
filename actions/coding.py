import subprocess

def run_terminal_command(command: str) -> str:
    """
    Terminalde (CMD/PowerShell) belirtilen komutu çalıştırır ve çıktısını döndürür.
    """
    print(f"C.O.R.E. İşlem: Terminal komutu çalıştırılıyor -> '{command}'")
    try:
        # Komutu çalıştır ve çıktısını yakala
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            # Başarılı olursa çıktıyı döndür
            output = result.stdout.strip()
            if not output:
                return "Komut başarıyla çalıştırıldı ancak ekrana bir çıktı vermedi."
            
            # Çıktı çok uzunsa kırp
            if len(output) > 2000:
                output = output[:2000] + "\n... [Çıktı çok uzun olduğu için kırpıldı]"
            return f"Komut başarıyla çalıştı. Çıktı:\n{output}"
        else:
            # Hata verirse hatayı döndür
            error = result.stderr.strip()
            return f"Komut çalıştırıldı ancak hata verdi. Hata detayı:\n{error}"
            
    except subprocess.TimeoutExpired:
        return "Komutun çalışması çok uzun sürdüğü için zaman aşımına uğradı ve durduruldu."
    except Exception as e:
        return f"Komut çalıştırılırken sistemsel bir hata oluştu: {str(e)}"