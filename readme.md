Markdown

# ENGLISH

# C.O.R.E. — Centralized Operational Response Engine v5.1
**Developer:** Murat Barış Güler  
**Version:** 5.1 Stable (Open-Source J.A.R.V.I.S. Architecture)

C.O.R.E. is an advanced, fully Python-based AI desktop assistant designed for desktop automation, natural language processing (NLP), hardware control, voice interaction, and personal life management. With the new update, it has become fully hardware-independent and tailored for open-source developers.

---

## 🚀 Highlighted Features & Integrations

### 1. 🌐 Environmental & System Monitoring
* **Cyber Interface:** Futuristic neon headers and the eye-friendly 'Consolas' terminal font for long-term use.
* **Live Clock & Location:** Real-time clock tracking and automated weather integration based on your location.
* **Advanced Hardware Tracking:** Real-time visual bars for CPU, RAM, and **GPU usage** tracking per second (integrated with psutil & GPUtil).

### 2. 📋 Voice Notes, Agenda, and Obsidian Integration
* **Voice Note Infrastructure:** Instantly process your thoughts into your permanent Obsidian Markdown journal (`CORE_Obsidian_Notes.md`).
* **Smart Calendar:** Interactive calendar interface where specific daily notes and events can be saved for desired dates.

### 3. 💳 Finance, Subscription, and Expense Tracking
* **Smart Budgeting:** Instantly record bills and expenses into the system using voice commands via NLP capabilities (e.g., "*Netflix subscription 200 Lira*").
* **Recurring Cycles:** Automatically create recurring payment cycles on the calendar by mathematically processing specified commands.
* **Morning Finance Summary:** Triggered by the "Good morning" command, reports the number of payments due that day and live exchange rates (USD/EUR/GBP).

### 4. 💬 WhatsApp Communication Automation
* **Direct Messaging:** Doesn't just open WhatsApp; the assistant automatically sends messages in the background to your saved contacts using voice commands (e.g., "*Text Ahmet that I'm on my way*").

### 5. ✈️ Travel & Ticket Automation (Flights and Buses)
* **Smart Ticket Search:** The assistant activates with commands like "*Find flight tickets*" or "*Look for bus tickets*" and opens comparison tabs across platforms like Skyscanner, Enuygun, THY, Pegasus, Obilet, and Kamilkoç within seconds to find the cheapest ticket.

### 6. 👁️ AI Vision Analysis & Smart Clipboard
* **Screen Reading:** With commands like "*Look at the screen*" or "*Analyze the code*", the assistant takes an instant screenshot, analyzes the visuals/code using the Gemini Vision model, and provides a vocal solution.
* **Clipboard Catcher:** Automatically detects long and important copied texts and offers to save them permanently to your Obsidian journal.

### 7. 💪 Sports, Health & Focus Center
* **Daily Goal Tracking:** Tracks Steps, Calories, and Water/Detox, alongside a dynamic calorie deficit calculator.
* **Pomodoro & Lofi:** Dynamic Focus Mode initiated by voice command. A countdown appears on the interface, and Lofi focus music automatically plays in the background.

### 8. ⚽ Sports Ecosystem & Live Scores
* **Wide League Coverage:** Voice command access to standings and fixtures for the Champions League, Europa League, Trendyol Super League, and Europe's Top 5 Leagues.
* **Smart Team Tracking:** Direct vocal routing to updated team fixtures and match highlights via YouTube/beIN.
* **Quick Streams:** One-click transition to live match streams (TOD) and the Kick platform via the quick access panel.

### 9. 🗺️ Flexible Routing & Dynamic Directory Detection
* **Smart Route Analysis:** Detects daily language and suffix errors to draw routes intelligently on Google Maps.
* **Universal Directory Paths:** No matter which Windows PC the assistant runs on, it automatically finds and opens the user's Desktop, Documents, School, and Downloads folders flawlessly using the `USERPROFILE` variable.

### 10. 💻 OS Control & Game Mode
* **Game Mode:** With the "*Start game mode*" command, the assistant closes browsers, cleans the background, and launches Steam directly.
* **Goodnight Protocol:** Automation to mute the system, stop playing media, and put the computer to sleep within 60 seconds.
* **Media Management:** Hardware-level control over all media actions like skipping tracks, pausing, and adjusting volume.

### 11. 🎙️ Advanced Voice Interaction & J.A.R.V.I.S. Engine
* **Live Animated Orb (Reactor):** A dynamic core interface that breathes slowly on standby and ripples algorithmically while speaking.
* **Edge-TTS & Gemini Intelligence:** Natural/fluent Turkish voice synthesis and instant switching between Gemini models (3.8-Flash, etc.) via the Control Panel.
* **Noise Filter:** A flexible microphone threshold that doesn't cut off commands mid-sentence while breathing or thinking, backed by a redundant multi-API pool.

---

## 🛠️ Installation and Auto-Build

It is very simple to compile and use the project on your own system as open-source:

1. To install the required libraries, type in the terminal:
   
   pip install -r requirements.txt

To test the application via your IDE, type in the terminal:

python gui.py

Auto Build Tool (Creating .exe): Run the custom setup script to create a clean, single-click executable .exe package with an invisible background (--windowed) and embedded icons. Type in the terminal:

python setup.py

When the process is complete, no junk files will remain, and CORE.exe will be waiting for you, ready to use, directly in your root directory.

# TURKISH 

# C.O.R.E. — Centralized Operational Response Engine v5.1
**Geliştiren:** Murat Barış Güler  
**Sürüm:** 5.1 Stabil (Open-Source J.A.R.V.I.S. Mimari)

C.O.R.E., masaüstü otomasyonu, doğal dil işleme (NLP), donanım kontrolü, sesli etkileşim ve kişisel yaşam yönetimi için tasarlanmış, tamamen Python tabanlı gelişmiş bir yapay zeka masaüstü asistanıdır. Yeni güncellemeyle birlikte tamamen donanım bağımsız ve açık kaynak geliştiricilerine uygun hale getirilmiştir.

---

## 🚀 Öne Çıkan Özellikler ve Entegrasyonlar

### 1. 🌐 Çevresel & Sistem Monitörü (ENV & System Monitoring)
* **Siber Arayüz:** Fütüristik neon başlıklar ve uzun süreli kullanımlarda göz yormayan 'Consolas' terminal fontu.
* **Canlı Saat ve Konum:** Anlık saat takibi ve konuma bağlı otomatik hava durumu entegrasyonu.
* **Gelişmiş Donanım Takibi:** CPU, RAM ve anlık **GPU kullanım oranlarının** saniyelik olarak görsel barlarla izlenmesi (psutil & GPUtil entegrasyonu).

### 2. 📋 Sesli Notlar, Ajanda ve Obsidian Entegrasyonu
* **Sesli Not Altyapısı:** Aklınıza gelen fikirleri anında Obsidian Markdown günlüğünüze (`CORE_Obsidian_Notes.md`) kalıcı olarak işleme.
* **Akıllı Takvim:** İstenilen tarihlere özel günlük notlar ve etkinlikler kaydedilebilen interaktif takvim arayüzü.

### 3. 💳 Finans, Abonelik ve Harcama Takibi
* **Akıllı Bütçe Kaydı:** NLP yeteneği sayesinde sesli komutlarla ("*Netflix aboneliği 200 Lira*") faturaları sisteme anında işleyebilme.
* **Periyodik Döngü (Recurring):** Belirtilen komutları matematiksel olarak algılayarak otomatik tekrarlayan ödeme döngüsü oluşturma.
* **Sabah Finans Özeti:** "Günaydın" komutuyla o gün yapılması gereken ödemeleri ve canlı kur bilgisini (USD/EUR/GBP) raporlama.

### 4. 💬 WhatsApp İletişim Otomasyonu
* **Doğrudan Mesaj Gönderimi:** Sadece WhatsApp'ı açmakla kalmaz; asistan, rehberinize kayıtlı kişilere sesli komutlarınızla ("*Ahmet'e yolda olduğumu yaz*") arka planda otomatik olarak mesaj gönderir.

### 5. ✈️ Seyahat & Bilet Otomasyonu (Uçak ve Otobüs)
* **Akıllı Bilet Arama:** "*Uçak bileti bak*" veya "*Otobüs bileti bul*" komutlarıyla asistan devreye girer ve saniyeler içinde Skyscanner, Enuygun, THY, Pegasus, Obilet ve Kamilkoç gibi platformlarda karşılaştırmalı sekmeler açarak en ucuz bileti bulmanızı sağlar.

### 6. 👁️ Yapay Zeka Ekran Analizi (Vision) & Akıllı Pano
* **Ekran Okuma:** "*Ekrana bak*" veya "*Kodu incele*" komutuyla asistan anlık ekran görüntünüzü alır ve Gemini Vision modeli ile ekrandaki görselleri/kodları analiz ederek size sesli çözüm sunar.
* **Pano (Clipboard) Yakalayıcı:** Kopyaladığınız uzun ve önemli metinleri otomatik olarak algılayıp kalıcı Obsidian günlüğünüze kaydetmeyi teklif eder.

### 7. 💪 Spor, Sağlık ve Odak (Focus) Merkezi
* **Günlük Hedef Takibi:** Adım, Kalori ve Su/Detoks takibinin yanı sıra dinamik kalori açığı (Deficit) hesaplayıcısı.
* **Pomodoro & Lofi:** Sesli komutla başlatılabilen dinamik Odak Modu. Süre başladığında arayüzde geri sayım belirir ve arkada otomatik olarak Lofi müzikleri devreye girer.

### 8. ⚽ Spor Ekosistemi & Canlı Skorlar
* **Geniş Lig Kapsamı:** Şampiyonlar Ligi, Avrupa Ligi, Trendyol Süper Lig ve 5 Büyük Lig'in puan durumu ve fikstürlerine sesli komutla erişim.
* **Akıllı Takım Takibi:** Takımların güncel fikstürü ve maç özetlerine doğrudan YouTube/beIN üzerinden sesli yönlendirme.
* **Hızlı Yayın:** Hızlı erişim paneli üzerinden tek tıkla canlı maç yayınlarına (TOD) ve Kick platformuna geçiş.

### 9. 🗺️ Esnek Rota & Dinamik Dizin Algılama
* **Akıllı Güzergah Analizi:** Günlük dil ve ek hatalarını algılayıp Google Haritalar üzerinde rotayı çizen akıllı yönlendirme.
* **Evrensel Dizin Yolları:** Asistan hangi Windows bilgisayarda çalışırsa çalışsın, `USERPROFILE` değişkeni ile o kullanıcının Masaüstü, Belgeler, Okul ve İndirilenler klasörlerini otomatik bulur ve hatasız açar.

### 10. 💻 İşletim Sistemi Kontrolü & Oyun Modu
* **Oyun Modu (Game Mode):** "*Oyun modunu başlat*" komutuyla asistan tarayıcıları kapatır, arka planı temizler ve doğrudan Steam'i başlatır.
* **İyi Geceler Protokolü:** Sistemi sessize alma, çalan medyayı durdurma ve bilgisayarı 60 saniye içinde uyku moduna alma otomasyonu.
* **Medya Yönetimi:** Şarkı geçme, durdurma, sesi kısıp açma gibi tüm medya işlemleri donanımsal düzeyde yönetilebilir.

### 11. 🎙️ Gelişmiş Sesli Etkileşim & J.A.R.V.I.S. Motoru
* **Canlı Animasyonlu Orb (Reaktör):** Asistan bekleme modundayken yavaşça nefes alan, konuşurken algoritmalarla dalgalanan dinamik çekirdek arayüzü.
* **Edge-TTS & Gemini Zekası:** Doğal/akıcı Türkçe ses sentezi ve Gemini modelleri arasında (3.8-Flash vb.) Kontrol Paneli üzerinden anlık geçiş imkanı.
* **Gürültü Filtresi:** Cümle arasında nefes alırken veya düşünürken komutu yarıda kesmeyen esnek mikrofon eşiği ve yedekli çoklu API havuzu.
---

## 🛠️ Kurulum ve Otomatik Derleme

Açık kaynak olarak projeyi kendi sisteminizde derlemek ve kullanmak çok basittir:

1. Gerekli kütüphaneleri yüklemek için terminale yazın:
   
   pip install -r requirements.txt
Uygulamayı geliştirici (IDE) üzerinden test etmek için terminale yazın:

python gui.py

Otomatik Build Aracı (exe Oluşturma): PyInstaller ile tek tıkla çalıştırılabilir, görünmez arka plana sahip (--windowed) temiz bir .exe paketi oluşturmak ve ikonları gömmek için özel yazılmış setup betiğini çalıştırın terminale yazın:

python setup.py

İşlem bittiğinde hiçbir çöp dosya kalmaz ve CORE.exe doğrudan ana dizininizde kullanıma hazır halde sizi bekler.