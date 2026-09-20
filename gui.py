import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import sys
import os
import random
import threading
import time
import subprocess
import psutil 
import requests
import json
import ctypes
import asyncio
import edge_tts
import multiprocessing
import math
import re
import urllib.parse
from datetime import datetime, timedelta

# --- GÖRÜNMEZ MOD ÇÖKME KORUMASI VE PYGAME SUSTURUCU ---
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
# -------------------------------------------------------

# --- PENCERE YÖNETİMİ İÇİN ---
import win32gui
import win32con

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, 
    QHBoxLayout, QWidget, QTextEdit, QLineEdit, 
    QPushButton, QFileDialog, QProgressBar, QDialog, 
    QFormLayout, QComboBox, QDialogButtonBox, QFrame, 
    QCheckBox, QGroupBox, QCalendarWidget, QListWidget, 
    QGridLayout, QInputDialog, QGraphicsDropShadowEffect,
    QColorDialog 
)
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QBrush, QIcon, QFontDatabase, QFont
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize

# API ve Yan Kütüphaneler
import google.generativeai as genai
import pygame
import speech_recognition as sr
from PIL import ImageGrab
import PIL.Image

# C.O.R.E. AKSİYON MODÜLLERİ
try:
    from actions import (
        browser_control, bus_booking, coding, computer_control, desktop, 
        file_controller, file_processor, flight_booking, gaming, 
        morning_news, reminder, screen_processor, system_monitor, 
        system_ops, system_watcher, weather_forecast, web_search, whatsapp
    )
except Exception as e:
    pass

from main import run_core, start_global_hotkey

# Ses Motoru Başlatma
pygame.mixer.init()

# Medya Kontrol Tuş Kodları
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_PLAY_PAUSE = 0xB3

# --- ASENKRON ÇALIŞTIRICI (Kasma Engelleme) ---
def run_async(cmd):
    threading.Thread(target=lambda: os.system(cmd), daemon=True).start()

def resource_path(relative_path):
    try: 
        base_path = sys._MEIPASS
    except Exception: 
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def turkce_karakter_temizle(metin):
    tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    return metin.translate(tr_map).lower().strip()

class DayManagerDialog(QDialog):
    def __init__(self, parent_core, date_str, day_str, theme_color="#add8e6"):
        super().__init__(parent_core)
        self.parent_core = parent_core
        self.date_str = date_str
        self.day_str = day_str
        self.setWindowTitle(f"AJANDA: {date_str}")
        self.setFixedSize(420, 600)
        
        self.setStyleSheet(f"""
            QDialog {{ background-color: #0f111a; border: 1px solid {theme_color}; }}
            QLabel {{ color: {theme_color}; font-family: 'Consolas'; font-weight: bold; font-size: 12px; }}
            QListWidget {{ background-color: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); padding: 8px; color: #e0e0e0; outline: none; }}
            QListWidget::item:selected {{ background-color: rgba(255, 255, 255, 0.1); color: {theme_color}; font-weight: bold; }}
            QLineEdit, QComboBox {{ background-color: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 2px; padding: 8px; color: #fff; font-family: 'Consolas'; }}
            QLineEdit:focus, QComboBox:focus {{ border: 1px solid {theme_color}; background-color: rgba(255, 255, 255, 0.1); }}
            QPushButton {{ background-color: rgba(255, 255, 255, 0.05); border: 1px solid {theme_color}; border-radius: 2px; padding: 10px; color: {theme_color}; font-weight: bold; font-family: 'Consolas'; }}
            QPushButton:hover {{ background-color: {theme_color}; color: #000; }}
            QCheckBox {{ color: #e0e0e0; font-family: 'Consolas'; }}
            QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid {theme_color}; background: transparent; }}
            QCheckBox::indicator:checked {{ background-color: {theme_color}; }}
        """)
        
        layout = QVBoxLayout(self)
        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)
        
        self.del_btn = QPushButton("🗑️ SEÇİLİ KAYDI SİL", self)
        self.del_btn.setStyleSheet("QPushButton { border: 1px solid #ff4444; color: #ff4444; background: transparent; } QPushButton:hover { background-color: #ff4444; color: #fff; }")
        self.del_btn.clicked.connect(self.delete_event)
        layout.addWidget(self.del_btn)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.type_combo = QComboBox(self)
        self.type_combo.addItems(["Abonelik Yenilenmesi", "Harcama / Fatura", "Özel Gün / Hatırlatıcı", "Ders / Okul"])
        self.desc_input = QLineEdit(self)
        self.desc_input.setPlaceholderText("Örn: Netflix, Kira, Doğum Günü...")
        self.amount_input = QLineEdit(self)
        self.amount_input.setPlaceholderText("Tutar (Opsiyonel)")
        self.recurring_check = QCheckBox("Her Ay Tekrarla (Aylık Abonelik)")
        
        form_layout.addRow("Kayıt Türü:", self.type_combo)
        form_layout.addRow("Açıklama:", self.desc_input)
        form_layout.addRow("Tutar (TL):", self.amount_input)
        form_layout.addRow("", self.recurring_check)
        layout.addLayout(form_layout)
        
        self.add_btn = QPushButton("+ YENİ KAYIT EKLE", self)
        self.add_btn.clicked.connect(self.add_event)
        layout.addWidget(self.add_btn)
        
        self.close_btn = QPushButton("KAPAT", self)
        self.close_btn.clicked.connect(self.accept)
        layout.addWidget(self.close_btn)
        
        self.refresh_list()
        
    def refresh_list(self):
        self.list_widget.clear()
        events_today = self.parent_core.calendar_events.get(self.date_str, [])
        events_recurring = self.parent_core.recurring_events.get(self.day_str, [])
        
        self.all_events = []
        for idx, ev in enumerate(events_today): self.all_events.append({"source": "calendar", "idx": idx, "data": ev})
        for idx, ev in enumerate(events_recurring): self.all_events.append({"source": "recurring", "idx": idx, "data": ev})
            
        if not self.all_events:
            self.list_widget.addItem(">> Bu tarih için kayıtlı veri bulunmuyor.")
        else:
            for ev_wrapper in self.all_events:
                ev = ev_wrapper["data"]
                amt_str = f" | {ev.get('amount', '')} TL" if ev.get('amount') else ""
                rec_str = " 🔁 (Her Ay)" if ev_wrapper["source"] == "recurring" else ""
                self.list_widget.addItem(f"[{ev['type']}] {ev['desc']}{amt_str}{rec_str}")
                
    def delete_event(self):
        row = self.list_widget.currentRow()
        if row < 0 or not self.all_events: return
        item_to_del = self.all_events[row]
        
        if item_to_del["source"] == "calendar":
            del self.parent_core.calendar_events[self.date_str][item_to_del["idx"]]
            if not self.parent_core.calendar_events[self.date_str]: del self.parent_core.calendar_events[self.date_str]
        else:
            del self.parent_core.recurring_events[self.day_str][item_to_del["idx"]]
            if not self.parent_core.recurring_events[self.day_str]: del self.parent_core.recurring_events[self.day_str]
        
        self.parent_core.save_memory(); self.refresh_list()
        
    def add_event(self):
        desc = self.desc_input.text().strip()
        if not desc: return
        ev = {"type": self.type_combo.currentText(), "desc": desc, "amount": self.amount_input.text().strip(), "recurring": self.recurring_check.isChecked()}
        
        if self.recurring_check.isChecked():
            if self.day_str not in self.parent_core.recurring_events: self.parent_core.recurring_events[self.day_str] = []
            self.parent_core.recurring_events[self.day_str].append(ev)
        else:
            if self.date_str not in self.parent_core.calendar_events: self.parent_core.calendar_events[self.date_str] = []
            self.parent_core.calendar_events[self.date_str].append(ev)
            
        self.parent_core.save_memory(); self.refresh_list(); self.desc_input.clear(); self.amount_input.clear()

# --- ORİJİNAL JARVIS REAKTÖRÜ (YUMUŞAK ANİMASYON) ---
class AnimatedOrbWidget(QWidget):
    def __init__(self, parent=None, size=400):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._size = size
        self._center = size / 2
        self._state = "bekliyor"
        self._tick = 0
        self._angles = [0.0] * 8 
        
        self.state_animations = {
            "bekliyor": {"spin_base": 0.5, "pulse_speed": 0.05, "pulse_amp": 0.03}, 
            "dinliyor": {"spin_base": 1.5, "pulse_speed": 0.12, "pulse_amp": 0.05}, 
            "dusunuyor": {"spin_base": 2.5, "pulse_speed": 0.08, "pulse_amp": 0.04}, 
            "konusuyor": {"spin_base": 2.0, "pulse_speed": 0.20, "pulse_amp": 0.08}, 
        }
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30) 

    def set_state(self, state: str): 
        self._state = state if state in self.state_animations else "bekliyor"

    def update_animation(self):
        self._tick += 1
        style = self.state_animations.get(self._state, self.state_animations["bekliyor"])
        speeds = [0.8, -1.2, 1.5, -0.9, 2.0, -2.5, 0.5, -0.7]
        for i in range(8): 
            self._angles[i] = (self._angles[i] + style["spin_base"] * speeds[i]) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        style = self.state_animations.get(self._state, self.state_animations["bekliyor"])
        pulse_speed = style["pulse_speed"]; pulse_amp = style["pulse_amp"]
        
        parent_window = self.window()
        hex_color = parent_window.current_theme_color if hasattr(parent_window, "current_theme_color") else "#00ff00"
        base_color = QColor(hex_color)
        
        cx = self._center
        cy = self._center
        
        # PÜRÜZSÜZ SES DALGASI
        pulse_factor = 1.0 + (math.sin(self._tick * pulse_speed) * pulse_amp)
        if self._state == "konusuyor":
            pulse_factor += (math.cos(self._tick * 0.08) * 0.03)
        
        def draw_hud_ring(radius, pen_width, alpha, dash_pattern=None, angle_idx=None, arcs=None):
            r = radius * pulse_factor
            pen = QPen(base_color, pen_width); c = QColor(base_color); c.setAlpha(alpha); pen.setColor(c)
            if dash_pattern: pen.setDashPattern(dash_pattern)
            painter.setPen(pen)
            if angle_idx is not None:
                painter.translate(cx, cy); painter.rotate(self._angles[angle_idx])
                if arcs:
                    for start, span in arcs: painter.drawArc(int(-r), int(-r), int(r*2), int(r*2), int(start * 16), int(span * 16))
                else: painter.drawEllipse(int(-r), int(-r), int(r*2), int(r*2))
                painter.rotate(-self._angles[angle_idx]); painter.translate(-cx, -cy)
            else:
                painter.drawEllipse(int(cx - r), int(cy - r), int(r*2), int(r*2))

        draw_hud_ring(radius=180, pen_width=1, alpha=80, dash_pattern=[2, 4], angle_idx=6)
        draw_hud_ring(radius=160, pen_width=4, alpha=150, dash_pattern=[15, 10, 5, 10], angle_idx=0)
        draw_hud_ring(radius=145, pen_width=2, alpha=100, angle_idx=1)
        draw_hud_ring(radius=130, pen_width=8, alpha=200, angle_idx=2, arcs=[(0, 60), (120, 60), (240, 60)])
        draw_hud_ring(radius=115, pen_width=3, alpha=180, angle_idx=3, arcs=[(45, 90), (225, 90)])
        draw_hud_ring(radius=95, pen_width=5, alpha=150, dash_pattern=[5, 5, 20, 5], angle_idx=4)
        
        r_cross = 80 * pulse_factor
        painter.setPen(QPen(QColor(base_color.red(), base_color.green(), base_color.blue(), 100), 1))
        painter.drawLine(int(cx - r_cross), int(cy), int(cx + r_cross), int(cy))
        painter.drawLine(int(cx), int(cy - r_cross), int(cx), int(cy + r_cross))

        core_r = (50) * pulse_factor
        painter.setPen(Qt.NoPen); halo_color = QColor(base_color)
        halo_alpha_base = 140 if self._state == "konusuyor" else 100
        halo_color.setAlpha(int(halo_alpha_base + (40 * math.sin(self._tick * pulse_speed))))
            
        painter.setBrush(QBrush(halo_color))
        painter.drawEllipse(int(cx - core_r - 10), int(cy - core_r - 10), int((core_r + 10)*2), int((core_r + 10)*2))
        solid_color = QColor(base_color); solid_color.setAlpha(255); painter.setBrush(QBrush(solid_color))
        painter.drawEllipse(int(cx - core_r), int(cy - core_r), int(core_r*2), int(core_r*2))
        inner_core_r = core_r * 0.5
        inner_color = QColor(255, 255, 255, 200); painter.setBrush(QBrush(inner_color))
        painter.drawEllipse(int(cx - inner_core_r), int(cy - inner_core_r), int(inner_core_r*2), int(inner_core_r*2))

class SysWorker(QThread):
    update_signal = pyqtSignal(float, float, float, float, str)
    def __init__(self):
        super().__init__()
        self.is_running = True
    def run(self):
        while self.is_running:
            try:
                c = psutil.cpu_percent(interval=None)
                r = psutil.virtual_memory()
                gpu_text = "GPU Usage: Kapalı"
                self.update_signal.emit(c, r.percent, r.used / (1024**3), r.total / (1024**3), gpu_text)
            except: pass
            time.sleep(1) 
    def stop(self): self.is_running = False

class WeatherWorker(QThread):
    weather_ready = pyqtSignal(str)
    def __init__(self, location): 
        super().__init__()
        self.location = location
    def run(self):
        try:
            sehir = self.location.split(",")[-1].strip()
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(sehir)}&count=1&language=tr&format=json"
            geo_resp = requests.get(geo_url, timeout=5).json()
            if "results" in geo_resp and len(geo_resp["results"]) > 0:
                lat = geo_resp["results"][0]["latitude"]; lon = geo_resp["results"][0]["longitude"]
                weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
                w_resp = requests.get(weather_url, timeout=5).json()
                if "current_weather" in w_resp:
                    temp = w_resp["current_weather"]["temperature"]; code = w_resp["current_weather"]["weathercode"]
                    durum = "Açık"
                    if code in [1, 2, 3]: durum = "Parçalı Bulutlu"
                    elif code in [45, 48]: durum = "Sisli"
                    elif code in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]: durum = "Yağmurlu"
                    elif code in [71, 73, 75, 77, 85, 86]: durum = "Karlı"
                    elif code in [95, 96, 99]: durum = "Fırtınalı"
                    self.weather_ready.emit(f"☁️ {temp}°C {durum}")
                else: self.weather_ready.emit("☁️ Veri Alınamadı")
            else: self.weather_ready.emit("☁️ Şehir Bulunamadı")
        except: self.weather_ready.emit("☁️ Bağlantı Yok")

class FinanceWorker(QThread):
    rates_ready = pyqtSignal(str, str, str)
    def run(self):
        try:
            response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5).json()
            usd_try = response['rates']['TRY']; eur_try = usd_try / response['rates']['EUR']; gbp_try = usd_try / response['rates']['GBP']
            self.rates_ready.emit(f"{usd_try:.2f} ₺", f"{eur_try:.2f} ₺", f"{gbp_try:.2f} ₺")
        except: self.rates_ready.emit("Hata", "Hata", "Hata")

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_model="gemini-3.8-flash", current_speed="+15%", current_volume="100%", current_color="#00ff00", current_name="C.O.R.E.", current_loc="Istanbul,Turkiye", current_salutation="efendim", current_api_key="", summary_prefs=None):
        super().__init__(parent)
        self.setWindowTitle("KONTROL PANELİ")
        self.setFixedSize(480, 720) 
        
        c_primary = current_color if current_color else "#00ff00"
            
        self.setStyleSheet(f"""
            QDialog {{ background-color: #0f111a; border: 1px solid {c_primary}; }}
            QLabel {{ color: {c_primary}; font-family: 'Consolas'; font-weight: bold; font-size: 12px; }}
            QLineEdit, QComboBox {{ background-color: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 2px; padding: 7px; color: #fff; font-family: 'Consolas'; }}
            QLineEdit:focus, QComboBox:focus {{ border: 1px solid {c_primary}; background-color: rgba(255, 255, 255, 0.1); }}
            QGroupBox {{ border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 4px; margin-top: 15px; font-weight: bold; color: {c_primary}; }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; }}
            QCheckBox {{ color: #e0e0e0; font-family: 'Consolas'; margin-top: 4px; }}
            QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid rgba(255, 255, 255, 0.4); background: transparent; }}
            QCheckBox::indicator:checked {{ background-color: {c_primary}; border: 1px solid {c_primary}; }}
            QPushButton {{ background-color: transparent; border: 1px solid {c_primary}; border-radius: 2px; padding: 8px 15px; color: {c_primary}; font-weight: bold; font-family: 'Consolas'; }}
            QPushButton:hover {{ background-color: {c_primary}; color: #000; }}
        """)
        
        self.summary_prefs = summary_prefs if summary_prefs is not None else {"time": True, "weather": True, "tasks": True, "football": True, "currency": True}

        layout = QFormLayout(self)
        layout.setSpacing(12) 
        
        self.name_input = QLineEdit(self); self.name_input.setText(current_name)
        self.salutation_input = QLineEdit(self); self.salutation_input.setText(current_salutation)
        self.api_key_input = QLineEdit(self); self.api_key_input.setText(current_api_key); self.api_key_input.setEchoMode(QLineEdit.Password)
        self.loc_input = QLineEdit(self); self.loc_input.setText(current_loc)

        self.color_combo = QComboBox(self)
        self.colors = {
            "Orijinal Yeşil": "#00ff00", "Zehir Yeşili": "#32cd32", "Orman Yeşili": "#228b22", "Açık Yeşil": "#90ee90",
            "Siber Mavi": "#00d0ff", "Okyanus Mavisi": "#00a8ff", "Buz Mavisi": "#add8e6", "Gece Mavisi": "#191970",
            "Güneş (Sarı)": "#ffff00", "Altın": "#ffd700", "Kehribar (Turuncu)": "#ffac00", "Ateş (Turuncu)": "#ff4500",
            "Kızıl (Kırmızı)": "#ff0000", "Kan Kırmızı": "#8b0000",
            "Neon Pembe": "#ff00ff", "Sıcak Pembe": "#ff69b4", "Derin Mor": "#8a2be2", "Ametist": "#9966cc",
            "Beyaz": "#ffffff", "Gümüş": "#c0c0c0", "Özel Renk Seç (Palet)...": "custom"
        }
        self.color_combo.addItems(self.colors.keys())
        self.custom_hex = current_color
        
        if current_color not in self.colors.values():
            self.color_combo.setCurrentText("Özel Renk Seç (Palet)...")
        else:
            for text, hex_val in self.colors.items():
                if hex_val == current_color: self.color_combo.setCurrentText(text)
                
        color_layout = QHBoxLayout()
        color_layout.addWidget(self.color_combo)
        self.btn_pick_color = QPushButton("🎨", self)
        self.btn_pick_color.setFixedWidth(40)
        self.btn_pick_color.clicked.connect(self.open_color_picker)
        color_layout.addWidget(self.btn_pick_color)

        self.model_combo = QComboBox(self)
        self.model_combo.addItems(["gemini-3.6-flash", "gemini-3.8-flash", "gemini-1.5-flash"]); self.model_combo.setCurrentText(current_model)
        self.speed_combo = QComboBox(self)
        self.speed_combo.addItems(["+0%", "+10%", "+15%", "+20%", "+25%", "+30%"]); self.speed_combo.setCurrentText(current_speed)
        self.volume_combo = QComboBox(self)
        self.volume_combo.addItems(["10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"]); self.volume_combo.setCurrentText(current_volume)

        layout.addRow("Asistan Adı:", self.name_input); layout.addRow("Hitap Şekli:", self.salutation_input); layout.addRow("Google API Key:", self.api_key_input); layout.addRow("Tema Rengi:", color_layout); layout.addRow("Konum:", self.loc_input); layout.addRow("Yapay Zeka Modeli:", self.model_combo); layout.addRow("Ses Hızı:", self.speed_combo); layout.addRow("Ses Düzeyi:", self.volume_combo)
        
        self.summary_group = QGroupBox("GÜNAYDIN ÖZETİ")
        summary_layout = QVBoxLayout()
        self.chk_time = QCheckBox("Tarih ve Saat"); self.chk_weather = QCheckBox("Hava Durumu"); self.chk_tasks = QCheckBox("Bekleyen Görevler"); self.chk_football = QCheckBox("Süper Lig & Şampiyonlar Ligi Maçları"); self.chk_currency = QCheckBox("Dolar/Euro Kuru")
        self.chk_time.setChecked(self.summary_prefs.get("time", True)); self.chk_weather.setChecked(self.summary_prefs.get("weather", True)); self.chk_tasks.setChecked(self.summary_prefs.get("tasks", True)); self.chk_football.setChecked(self.summary_prefs.get("football", True)); self.chk_currency.setChecked(self.summary_prefs.get("currency", True))
        for chk in [self.chk_time, self.chk_weather, self.chk_tasks, self.chk_football, self.chk_currency]: 
            summary_layout.addWidget(chk)
        self.summary_group.setLayout(summary_layout); layout.addRow(self.summary_group)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept); self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def open_color_picker(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.custom_hex = color.name()
            self.color_combo.setCurrentText("Özel Renk Seç (Palet)...")

    def get_summary_prefs(self): return {"time": self.chk_time.isChecked(), "weather": self.chk_weather.isChecked(), "tasks": self.chk_tasks.isChecked(), "football": self.chk_football.isChecked(), "currency": self.chk_currency.isChecked()}

class ContinuousListenWorker(QThread):
    text_ready = pyqtSignal(str)
    def __init__(self): super().__init__(); self.is_running = True
    def run(self):
        r = sr.Recognizer()
        r.energy_threshold = 300
        r.pause_threshold = 1.2
        r.dynamic_energy_threshold = True 
        with sr.Microphone() as src:
            r.adjust_for_ambient_noise(src, duration=1.0)
            while self.is_running:
                try:
                    audio = r.listen(src, timeout=3, phrase_time_limit=15)
                    text = r.recognize_google(audio, language="tr-TR")
                    if text: self.text_ready.emit(text)
                except sr.WaitTimeoutError: continue
                except Exception: time.sleep(0.1)
    def stop(self): self.is_running = False

class ChatWorker(QThread):
    response_ready = pyqtSignal(str)
    task_added = pyqtSignal(str, str)
    action_triggered = pyqtSignal(str, str)
    close_app_signal = pyqtSignal()
    state_changed = pyqtSignal(str)
    
    def __init__(self, raw_user_text, gemini_prompt, image_path, model_name, voice_speed, voice_volume, ai_name, salutation, api_key, is_direct_speech=False, health_data=None):
        super().__init__()
        self.raw_user_text = raw_user_text; self.gemini_prompt = gemini_prompt; self.image_path = image_path; self.model_name = model_name
        self.voice_speed = voice_speed; self.voice_volume = voice_volume; self.vol_float = int(self.voice_volume.replace("%", "")) / 100.0
        self.ai_name = ai_name; self.salutation = salutation; self.api_key = api_key; self.is_direct_speech = is_direct_speech; self.health_data = health_data or {}
    
    def run(self):
        try:
            if self.is_direct_speech: 
                self.state_changed.emit("konusuyor"); self.speak_text(self.gemini_prompt); self.state_changed.emit("bekliyor"); return
                
            clean_text = self.raw_user_text.lower()
            clean_text_tr = turkce_karakter_temizle(clean_text)

            # --- ÇOKLU PLATFORM AÇICI (YouTube, TOD, HBO Max vb.) ---
            if any(w in clean_text_tr for w in ["aç", "ac", "başlat", "baslat", "gir", "izle"]):
                acilanlar = []
                
                if any(w in clean_text_tr for w in ["youtube music", "youtube müzik", "yt music"]):
                    run_async("start https://music.youtube.com")
                    acilanlar.append("YouTube Music")
                    clean_text_tr = clean_text_tr.replace("youtube music", "").replace("youtube müzik", "")
                
                if "youtube" in clean_text_tr:
                    run_async("start https://www.youtube.com")
                    acilanlar.append("YouTube")
                    
                if any(w in clean_text_tr for w in ["tod", "bein sport", "beinsport", "bein sports", "lig tv"]):
                    run_async("start https://www.todtv.com.tr/canli-tv/bein-sports-1?c=spor")
                    acilanlar.append("TOD (beIN Sports)")
                    
                if any(w in clean_text_tr for w in ["hbo", "max", "hbo max"]):
                    run_async("start https://www.max.com")
                    acilanlar.append("HBO Max")
                    
                if any(w in clean_text_tr for w in ["yeni sekme", "sekme aç", "sekme ac"]):
                    run_async("start https://www.google.com")
                    acilanlar.append("Yeni Sekme")

                if acilanlar:
                    c = f"İstediğiniz {', '.join(acilanlar)} platformları anında başlatılıyor {self.salutation}."
                    self.response_ready.emit(c)
                    self.state_changed.emit("konusuyor")
                    self.speak_text(c)
                    self.state_changed.emit("bekliyor")
                    return
            # --------------------------------------------------------

            # --- SUSTURMA KOMUTU ---
            if clean_text_tr in ["sus", "yeter", "sesi kes", "konuşmayı durdur", "tamamdır", "teşekkürler"]:
                pygame.mixer.music.stop()
                self.response_ready.emit("Susturuldu.")
                self.state_changed.emit("bekliyor")
                return

            # --- SİSTEMİ KAPATMA / VEDA PROTOKOLÜ ---
            if any(w in clean_text_tr for w in ["kendini kapat", "kapan", "sistemi kapat", "dışarı çıkıyorum", "disari cikiyorum"]):
                mesajlar = [
                    f"Görüşmek üzere {self.salutation}, iyi eğlenceler dilerim.",
                    f"Sistemleri kapatıyorum. Görüşürüz {self.salutation}, iyi seyirler.",
                    f"Harika bir gün geçirmenizi dilerim {self.salutation}. Çıkış yapılıyor."
                ]
                c = random.choice(mesajlar)
                self.response_ready.emit(c)
                self.state_changed.emit("konusuyor")
                self.speak_text(c)
                time.sleep(0.5) 
                self.close_app_signal.emit()
                return

            # --- KUSURSUZ WHATSAPP (TÜRKÇE KARAKTER KORUMASI EKLENDİ) ---
            if "whatsapp" in clean_text_tr:
                if any(w in clean_text_tr for w in ["yaz", "mesaj", "gönder", "gonder"]):
                    try:
                        import webbrowser
                        kisi_bulundu = None
                        mesaj_icerik = "Sistem üzerinden iletildi."
                        
                        try:
                            aktif_rehber = whatsapp.REHBER
                        except Exception:
                            # AÇIK KAYNAK İÇİN ANONİMLEŞTİRİLMİŞ ÖRNEK REHBER
                            aktif_rehber = {
                                "kisi1": "+905550000001",
                                "kisi2": "+905550000002",
                                "grup_adi": "GRUP"
                            }

                        for isim in aktif_rehber.keys():
                            if isim in clean_text_tr:
                                kisi_bulundu = isim
                                ham_mesaj = self.raw_user_text.lower()
                                
                                silinecekler = ["whatsapp'ı", "whatsapp'i", "whatsappı", "whatsappi", "whatsapp'tan", "whatsapptan", "whatsapp", "aç", "ac"]
                                for s in silinecekler:
                                    ham_mesaj = ham_mesaj.replace(s, "")
                                ham_mesaj = ham_mesaj.strip()
                                
                                idx = ham_mesaj.find(isim)
                                if idx != -1:
                                    kalan = ham_mesaj[idx + len(isim):].strip()
                                else:
                                    kalan = ham_mesaj
                                
                                for ek in ["'a ", "'e ", "a ", "e ", "ya ", "ye ", "na ", "ne ", "dan ", "den ", "tan ", "ten ", "grubuna ", "gruba "]:
                                    if kalan.startswith(ek):
                                        kalan = kalan[len(ek):].strip()
                                        break
                                
                                for bitis in [" yaz", " gönder", " gonder", " mesaj at", " yolla", " yollarmısın", " yollar mısın"]:
                                    if kalan.endswith(bitis):
                                        kalan = kalan[:-len(bitis)].strip()
                                        break
                                
                                if kalan:
                                    mesaj_icerik = kalan.capitalize()
                                break
                        
                        if kisi_bulundu:
                            telefon = aktif_rehber[kisi_bulundu].replace(" ", "")
                            
                            def whatsapp_web_fallback(hedef_url):
                                import webbrowser, time
                                try: import pyautogui
                                except ImportError: pyautogui = None
                                webbrowser.open(hedef_url)
                                if pyautogui:
                                    time.sleep(15) 
                                    pyautogui.press('enter') 
                                    time.sleep(2)
                                    pyautogui.hotkey('ctrl', 'w') 

                            try:
                                threading.Thread(target=whatsapp.send_whatsapp_message, args=(kisi_bulundu, mesaj_icerik), daemon=True).start()
                            except Exception:
                                if telefon == "GRUP":
                                    threading.Thread(target=lambda: webbrowser.open("https://web.whatsapp.com/"), daemon=True).start()
                                else:
                                    url = f"https://web.whatsapp.com/send?phone={telefon}&text={urllib.parse.quote(mesaj_icerik)}"
                                    threading.Thread(target=whatsapp_web_fallback, args=(url,), daemon=True).start()
                            
                            c = f"Hemen {kisi_bulundu} kişisine '{mesaj_icerik}' mesajını iletiyorum {self.salutation}."
                        else:
                            threading.Thread(target=lambda: webbrowser.open("https://web.whatsapp.com/"), daemon=True).start()
                            c = f"Rehberde eşleşen kişi bulunamadı, WhatsApp Web açıldı {self.salutation}."
                    except Exception as e:
                        import webbrowser
                        threading.Thread(target=lambda: webbrowser.open("https://web.whatsapp.com/"), daemon=True).start()
                        c = f"WhatsApp Web açıldı {self.salutation}."
                else:
                    import webbrowser
                    threading.Thread(target=lambda: webbrowser.open("https://web.whatsapp.com/"), daemon=True).start()
                    c = f"WhatsApp başlatıldı {self.salutation}."
                self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return
            # -----------------------------------------------------------------
            
            # --- MASAÜSTÜNÜ GÖSTER VE KÜÇÜLT (Doğrudan Windows API) ---
            if any(w in clean_text_tr for w in ["masaüstünü göster", "masaustunu goster", "pencereleri küçült", "pencereleri kucult", "pencereyi küçült"]):
                ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0) # Win
                ctypes.windll.user32.keybd_event(0x44, 0, 0, 0) # D
                ctypes.windll.user32.keybd_event(0x44, 0, 2, 0)
                ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)
                c = f"Masaüstü gösteriliyor {self.salutation}."
                self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return

            # --- SES KONTROLÜ (Doğrudan Windows Medya API) ---
            if any(w in clean_text_tr for w in ["sesi artır", "sesi artir", "sesi aç", "sesi ac", "ses seviyesi"]):
                for _ in range(5): 
                    ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0); ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
                c = f"Ses seviyesi artırıldı {self.salutation}."
                self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return

            if any(w in clean_text_tr for w in ["sesi kıs", "sesi kis", "sesi azalt"]):
                for _ in range(5): 
                    ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0); ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)
                c = f"Ses seviyesi düşürüldü {self.salutation}."
                self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return

            if any(w in clean_text_tr for w in ["sesi kapat", "sessize al"]):
                ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0); ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
                c = f"Sistem sesi kapatıldı {self.salutation}."
                self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return

            # --- MANUEL GOOGLE ARAMA TETİKLEYİCİSİ ---
            if "internette ara" in clean_text_tr or ("google" in clean_text_tr and "ara" in clean_text_tr) or "google'dan bul" in clean_text_tr:
                search_query = clean_text_tr.replace("internette", "").replace("google'da", "").replace("google da", "").replace("ara", "").replace("bul", "").strip()
                if search_query:
                    run_async(f"start https://www.google.com/search?q={urllib.parse.quote(search_query)}")
                    c = f"'{search_query}' için anında Google araması başlatıyorum {self.salutation}."
                    self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return

            if any(w in clean_text for w in ["word dosyası", "word aç", "word belgesi"]):
                run_async("start winword")
                c = f"Microsoft Word başlatılıyor {self.salutation}."
                self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return

            if any(w in clean_text for w in ["excel dosyası", "excel aç", "tablo aç"]):
                run_async("start excel")
                c = f"Microsoft Excel başlatılıyor {self.salutation}."
                self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return

            dosya_tetikleyiciler = ["okul", "belge", "indir", "bilgisayar", "dosya", "klasor", "klaosr", "proje", "gezgin"]
            if any(w in clean_text_tr for w in dosya_tetikleyiciler):
                klasor_acildi = False
                user_profile = os.environ.get('USERPROFILE', 'C:\\')
                if "okul" in clean_text_tr:
                    run_async(f'start explorer "{user_profile}\\Desktop"')
                    c = f"Masaüstü açılıyor {self.salutation}."
                    klasor_acildi = True
                elif "belge" in clean_text_tr:
                    run_async(f'start explorer "{user_profile}\\Documents"')
                    c = f"Belgeler klasörünüz açılıyor {self.salutation}."
                    klasor_acildi = True
                elif "indir" in clean_text_tr:
                    run_async(f'start explorer "{user_profile}\\Downloads"')
                    c = f"İndirilenler klasörünüz açılıyor {self.salutation}."
                    klasor_acildi = True
                elif "proje" in clean_text_tr or "core" in clean_text_tr:
                    current_dir = os.getcwd()
                    run_async(f'start explorer "{current_dir}"')
                    c = f"Proje klasörünüz açılıyor {self.salutation}."
                    klasor_acildi = True
                elif any(w in clean_text_tr for w in ["bilgisayar", "dosya", "klasor", "klaosr", "gezgin"]):
                    run_async("start explorer")
                    c = f"Dosya gezgini açılıyor {self.salutation}."
                    klasor_acildi = True
                if klasor_acildi:
                    self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return
                self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return
            
            if "hesap makine" in clean_text_tr and "ac" in clean_text_tr:
                run_async("start calc")
                c = "Hesap makinesi açılıyor efendim."
                self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return

            if any(w in clean_text for w in ["hava nasıl", "hava durumu", "bugün hava"]):
                try: 
                    ans = weather_forecast.get_weather()
                    self.gemini_prompt = f"Şu hava durumu bilgisini radyocu edasıyla kısaca sun: {ans}"
                except: pass

            if any(w in clean_text for w in ["sistem gözcü", "gözcüyü aç", "izlemeyi başlat"]):
                try: 
                    ans = system_watcher.start_system_watcher()
                    self.response_ready.emit(ans); self.state_changed.emit("konusuyor"); self.speak_text(ans); self.state_changed.emit("bekliyor"); return
                except: pass

            if any(w in clean_text_tr for w in ["su ", "suyu", "kalori", "adim", "adım", "kcal"]):
                is_set = any(w in clean_text_tr for w in ["yap", "olsun", "ayarla", "esitle"])
                islem_yapildi = False; mesajlar = []
                parts = clean_text_tr.replace(",", " ve ").split(" ve ")
                for part in parts:
                    m = re.search(r'(\d+[.,]?\d*)', part)
                    if m:
                        val = m.group(1).replace(',', '.')
                        if "su" in part:
                            self.action_triggered.emit("set_water" if is_set else "add_water", val)
                            mesajlar.append("Su"); islem_yapildi = True
                        elif "kalori" in part or "kcal" in part:
                            val_int = str(int(float(val)))
                            if "acik" in part or "açık" in part or "acigi" in part or "açığı" in part:
                                self.action_triggered.emit("set_daily_deficit" if is_set else "add_daily_deficit", val_int)
                                mesajlar.append("Kalori Açığı")
                            else:
                                self.action_triggered.emit("set_cals" if is_set else "add_cals", val_int)
                                mesajlar.append("Kalori")
                            islem_yapildi = True
                        elif "adim" in part or "adım" in part:
                            val_int = str(int(float(val)))
                            self.action_triggered.emit("set_steps" if is_set else "add_steps", val_int)
                            mesajlar.append("Adım"); islem_yapildi = True
                if islem_yapildi:
                    c = f"{', '.join(mesajlar)} verileriniz eşzamanlı olarak işlendi efendim."
                    self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return
            
            if any(w in clean_text for w in ["ekrana bak", "ekranı incele", "kodu incele", "buna bak", "ekran görüntüsü al", "ekran goruntusu al"]):
                try: 
                    screen_processor.capture_screen_description()
                    self.image_path = "actions/temp_screen.png"
                except Exception as e:
                    screen_path = f"screenshot_{int(time.time())}.png"
                    ImageGrab.grab().save(screen_path); self.image_path = screen_path
                self.gemini_prompt = "Şu an ekranımdaki görüntüyü incele ve soruma cevap ver: " + self.gemini_prompt
            
            if any(w in clean_text for w in ["iyi geceler", "gece modu"]):
                if "protokol" in clean_text or "geceler" in clean_text:
                    self.action_triggered.emit("goodnight_protocol", "")
                    c = f"İyi geceler {self.salutation}. Sistem sessize alınıyor, müzikler durduruldu ve PC 60 saniye içinde uykuya geçecek."
                    self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return
            
            if any(w in clean_text for w in ["oyun modu", "oyun modunu baslat"]):
                self.action_triggered.emit("game_mode", "")
                try: gaming.launch_game_platform("steam")
                except: pass
                c = f"Oyun modu aktif ediliyor {self.salutation}. Arka plan işlemleri optimize ediliyor ve Steam başlatılıyor."
                self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return
            if any(w in clean_text_tr for w in ["oyun modunu kapat", "oyun modundan cik", "oyun modunu bitir"]):
                self.action_triggered.emit("stop_game_mode", "")
                c = f"Oyun modu kapatıldı {self.salutation}. Normal çalışma düzenine dönülüyor."
                self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return
            
            if any(w in clean_text for w in ["panoyu kaydet", "kopyaladigimi kaydet", "kopyaladığımı kaydet"]):
                self.action_triggered.emit("save_clipboard", "")
                c = "Panodaki veriler Obsidian günlüğünüze kalıcı olarak kaydedildi efendim."
                self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return

            if any(word in clean_text for word in ["sarkiyi durdur", "müzigi durdur", "oynatmayi durdur", "sarkiyi baslat", "müzigi baslat"]):
                self.action_triggered.emit("media_play_pause", ""); self.state_changed.emit("bekliyor"); return
            if any(word in clean_text for word in ["sonraki sarki", "sarkiyi gec"]):
                self.action_triggered.emit("media_next", ""); self.state_changed.emit("bekliyor"); return
            if any(word in clean_text for word in ["onceki sarki", "bası sar", "geri sar"]):
                self.action_triggered.emit("media_prev", ""); self.state_changed.emit("bekliyor"); return

            if any(w in clean_text for w in ["odaklanma", "odaklama", "pomodoro", "odak modu", "calisma modu", "odaklan"]):
                if any(w in clean_text for w in ["kapat", "durdur", "bitir", "iptal"]):
                    self.action_triggered.emit("stop_pomodoro", "")
                    c = f"Odaklanma protokolü iptal edildi {self.salutation}."
                else:
                    match = re.search(r'(\d+)\s*dakika', clean_text)
                    pomo_mins = int(match.group(1)) if match else 40
                    self.action_triggered.emit("start_pomodoro", str(pomo_mins))
                    c = f"{pomo_mins} dakikalık odaklanma protokolü başlatıldı {self.salutation}. Lofi Girl canlı yayını açılıyor."
                self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return

            if any(w in clean_text for w in ["sisteme not al", "not al", "gunluge yaz", "günlüğe yaz"]):
                note_content = ""
                if "sisteme not al" in clean_text: note_content = self.raw_user_text.lower().split("sisteme not al", 1)[-1].strip()
                elif "not al" in clean_text: note_content = self.raw_user_text.lower().split("not al", 1)[-1].strip()
                elif "günlüğe yaz" in clean_text: note_content = self.raw_user_text.lower().split("günlüğe yaz", 1)[-1].strip()
                elif "gunluge yaz" in clean_text: note_content = self.raw_user_text.lower().split("gunluge yaz", 1)[-1].strip()
                if note_content:
                    self.task_added.emit("note", note_content.capitalize())
                    c = "Notunuz Obsidian veri tabanına kaydedildi efendim."
                    self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return
        
            if "sil" in clean_text_tr and any(w in clean_text_tr for w in ["not", "obsidian", "gunluk"]):
                hedef_not = clean_text_tr.replace("notunu", "").replace("notu", "").replace("obsidiandan", "").replace("sil", "").replace("lütfen", "").strip()
                if hedef_not:
                    self.action_triggered.emit("delete_note", hedef_not)
                    c = f"İçinde '{hedef_not}' geçen not Obsidian'dan silindi efendim."
                else:
                    c = "Hangi notu sileceğimi anlayamadım efendim."
                self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return
                
            if any(w in clean_text_tr for w in ["ucak bileti", "uçak bileti", "ucus bak", "uçuş bak", "bilet bak"]):
                c = f"Sizin için en uygun fiyatlı uçak bileti karşılaştırma sitelerini ve firmaları açıyorum {self.salutation}."
                self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c)
                run_async("start https://www.skyscanner.com.tr/")
                run_async("start https://www.enuygun.com/ucak-bileti/")
                run_async("start https://www.flypgs.com/")
                run_async("start https://www.turkishairlines.com/")
                self.state_changed.emit("bekliyor"); return

            if any(w in clean_text_tr for w in ["otobus bileti", "otobüs bileti", "otobus bak", "otobüs bak"]):
                c = f"Sizin için popüler otobüs bilet ve karşılaştırma sayfalarını açıyorum {self.salutation}."
                self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c)
                run_async("start https://www.obilet.com/")
                run_async("start https://www.enuygun.com/otobus-bileti/")
                run_async("start https://www.kamilkoc.com.tr/")
                self.state_changed.emit("bekliyor"); return

            spor_tetikleyiciler = ["mac", "maç", "fikst", "puan", "tablo", "lig", "ucl", "uel", "sampiyonlar", "fener", "fb", "galatasaray", "gs", "besiktas", "bjk", "trabzon", "ts", "skor", "hafta"]
            if any(w in clean_text_tr for w in spor_tetikleyiciler) and not ("ozet" in clean_text_tr or "özet" in clean_text_tr):
                urls_to_open = []; hedefler = []
                if any(w in clean_text_tr for w in ["galatasaray", "gs"]): urls_to_open.append("https://ofsayt.com/futbol/takim/galatasaray/63345ed9-00e4-4874-af53-2afe719458a0/detay"); hedefler.append("Galatasaray")
                if any(w in clean_text_tr for w in ["fenerbahce", "fenerbahçe", "fener", "fb"]): urls_to_open.append("https://ofsayt.com/futbol/takim/fenerbahce/964c7974-f92c-4b56-bc90-d086cf7a2afc/detay"); hedefler.append("Fenerbahçe")
                if any(w in clean_text_tr for w in ["besiktas", "beşiktaş", "bjk"]): urls_to_open.append("https://ofsayt.com/futbol/takim/besiktas/d745aea6-9531-4680-bb2a-7347a98e64e8/detay"); hedefler.append("Beşiktaş")
                if any(w in clean_text_tr for w in ["trabzon", "ts"]): urls_to_open.append("https://ofsayt.com/futbol/takim/trabzonspor/4b96c631-18ab-4551-9bd3-4bcbaefae014/detay"); hedefler.append("Trabzonspor")
                if "süper" in clean_text_tr or "super" in clean_text_tr: urls_to_open.append("https://ofsayt.com/futbol/lig/turkiye-super-lig/1a18dcb4-95ee-4b8b-bc4f-73c1e577df2d/detay/puan-durumu"); hedefler.append("Süper Lig")
                if "şampiyon" in clean_text_tr or "sampiyon" in clean_text_tr or "ucl" in clean_text_tr: urls_to_open.append("https://ofsayt.com/futbol/lig/sampiyonlar-ligi/453b75c9-858b-4040-9441-2506bcabf723/detay/puan-durumu"); hedefler.append("Şampiyonlar Ligi")
                if "premier" in clean_text_tr or "ingiltere" in clean_text_tr: urls_to_open.append("https://ofsayt.com/futbol/lig/ingiltere-premier-league/deddfd01-82c5-4ae7-b5e3-140e63ecc3aa/detay/puan-durumu"); hedefler.append("Premier Lig")
                if "la liga" in clean_text_tr or "ispanya" in clean_text_tr: urls_to_open.append("https://ofsayt.com/futbol/lig/ispanya-laliga/dbdb4f92-f12b-4c58-a718-1fb253aeeec7/detay/puan-durumu"); hedefler.append("La Liga")
                if "bundesliga" in clean_text_tr or "almanya" in clean_text_tr: urls_to_open.append("https://ofsayt.com/futbol/lig/almanya-bundesliga/8c156a73-2fac-45ae-b5e5-8ccab0f51b21/detay/puan-durumu"); hedefler.append("Bundesliga")
                if "serie" in clean_text_tr or "italya" in clean_text_tr: urls_to_open.append("https://ofsayt.com/futbol/lig/italya-serie-a/7860bc37-4741-4e1e-a138-f19a975ecb7b/detay/puan-durumu"); hedefler.append("Serie A")
                if any(w in clean_text_tr for w in ["ofsayt", "canli", "bugun", "skor", "maclar"]): urls_to_open.append("https://ofsayt.com/"); hedefler.append("Canlı Skorlar")

                if urls_to_open:
                    c = f"İstediğiniz {', '.join(hedefler)} maç, fikstür ve tablo verilerini anında açıyorum {self.salutation}."
                    self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c)
                    for u in urls_to_open: run_async(f"start {u}")
                    self.state_changed.emit("bekliyor"); return

            if "ozet" in clean_text_tr or "özet" in clean_text_tr:
                urls_to_open = []; hedefler = []
                if any(w in clean_text_tr for w in ["süper lig", "super lig", "turkiye", "türkiye"]): urls_to_open.append("https://beinsports.com.tr/mac-ozetleri-goller/super-lig"); hedefler.append("Süper Lig")
                if any(w in clean_text_tr for w in ["şampiyon", "sampiyon", "ucl"]): urls_to_open.append("https://www.youtube.com/watch?v=Zc82hO8ZHsc&list=PLQs_w-FaXbl0"); hedefler.append("Şampiyonlar Ligi")
                if "premier" in clean_text_tr or "ingiltere" in clean_text_tr: urls_to_open.append("https://www.youtube.com/watch?v=3XR24K12ETM&list=PLC-ntSjW5uvU"); hedefler.append("Premier Lig")
                if "la liga" in clean_text_tr or "ispanya" in clean_text_tr: urls_to_open.append("https://www.youtube.com/watch?v=Zc2TL6QzrJw&list=PLc1u-zFXPFvA"); hedefler.append("La Liga")
                if "bayern" in clean_text_tr: urls_to_open.append("https://www.youtube.com/results?search_query=bayern+m%C3%BCnih"); hedefler.append("Bayern Münih")
                if any(w in clean_text_tr for w in ["serie a", "seri a", "italya"]): urls_to_open.append("https://www.youtube.com/watch?v=VYhe3m-fw-o&list=PLWi99Pdx7Qjo"); hedefler.append("Serie A")

                if urls_to_open:
                    c = f"Hemen {', '.join(hedefler)} maç özetlerini açıyorum {self.salutation}."
                    self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c)
                    for u in urls_to_open: run_async(f"start {u}")
                    self.state_changed.emit("bekliyor"); return

            if "haftalik" in clean_text_tr and "sifirla" in clean_text_tr:
                self.action_triggered.emit("reset_weekly", "")
                cevap = "Haftalık sağlık verileriniz sıfırlandı efendim."
                self.response_ready.emit(cevap); self.state_changed.emit("konusuyor"); self.speak_text(cevap); self.state_changed.emit("bekliyor"); return

            if ("abonelik" in clean_text_tr or "fatura" in clean_text_tr) and "ekle" in clean_text_tr:
                m = list(re.finditer(r"her\s+ayin\s+(\d+)['’\w]*\s+(.*?)\s*=\s*(\d+)", clean_text_tr))
                if m:
                    for x in m: 
                        self.task_added.emit("recurring_event", json.dumps({"day": x.group(1), "type": "Abonelik", "desc": x.group(2).title(), "amount": x.group(3)}))
                    cevap = f"Abonelikler eklendi {self.salutation}."
                    self.response_ready.emit(cevap); self.state_changed.emit("konusuyor"); self.speak_text(cevap); self.state_changed.emit("bekliyor"); return

            if any(p in clean_text_tr for p in ["gore ekle", "yapilacak ekle", "hatırlatma ekle", "hatirlatma ekle"]):
                cl = self.raw_user_text.split(":", 1)[1].strip() if ":" in self.raw_user_text else self.raw_user_text.replace("görev ekle", "").replace("hatırlatma ekle", "").strip()
                if cl: 
                    self.task_added.emit("reminder", cl)
                    c = f"Hatırlatma Obsidian günlüğüne eklendi efendim."
                    self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return

            if any(p in clean_text_tr for p in ["gorevleri sil", "yapilacaklari temizle"]):
                self.task_added.emit("clear_tasks", ""); c = f"Görevler silindi."
                self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); self.state_changed.emit("bekliyor"); return

            self.state_changed.emit("dusunuyor")
            content_to_send = [self.gemini_prompt]
            if self.image_path and os.path.exists(self.image_path): content_to_send.append(PIL.Image.open(self.image_path))
                
            api_keys = [k.strip() for k in self.api_key.split(",") if k.strip()]
            if not api_keys: 
                self.response_ready.emit(">> [API HATASI]")
                self.state_changed.emit("bekliyor"); return

            sys_inst = f"Senin adın {self.ai_name}. Asla markdown kullanma. Sahibine '{self.salutation}' diye hitap et. Bilmediğin veya güncel bir konu sorulursa internette arama yaparak cevap ver."

            success = False
            for k in api_keys:
                try:
                    genai.configure(api_key=k)
                    try:
                        model = genai.GenerativeModel(self.model_name, tools='google_search_retrieval', system_instruction=sys_inst)
                        c = model.generate_content(content_to_send).text.strip().replace("**", "").replace("*", "")
                    except Exception:
                        model = genai.GenerativeModel(self.model_name, system_instruction=sys_inst)
                        c = model.generate_content(content_to_send).text.strip().replace("**", "").replace("*", "")
                    
                    self.response_ready.emit(c); self.state_changed.emit("konusuyor"); self.speak_text(c); success = True; break 
                except Exception: 
                    continue 
            
            if not success: 
                self.response_ready.emit(f">> [API HATASI]")
                self.state_changed.emit("konusuyor"); self.speak_text("Bağlantı hatası efendim.")
                
            if self.image_path and self.image_path.startswith("screenshot_"):
                try: os.remove(self.image_path)
                except: pass
                    
            self.state_changed.emit("bekliyor")
            
        except Exception: 
            self.response_ready.emit(f">> [SİSTEM HATASI]: Komut işlenirken bir sorun oluştu.")
            self.state_changed.emit("bekliyor")
    
    def speak_text(self, text):
        try:
            cl = " ".join(text.replace(",", " ").replace(".", " ").replace("!", " ").replace("?", " ").split())
            if not cl: return
            af = f"core_resp_{int(time.time())}.mp3"
            
            async def gen(): 
                await edge_tts.Communicate(cl, "tr-TR-AhmetNeural", rate=self.voice_speed).save(af)
            
            try: asyncio.run(gen())
            except: return

            if os.path.exists(af):
                pygame.mixer.music.load(af)
                pygame.mixer.music.set_volume(self.vol_float)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy(): time.sleep(0.05)
                pygame.mixer.music.unload()
                time.sleep(0.1)
                try: os.remove(af)
                except: pass
        except: pass

class CoreInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.memory_file = "core_memory.json"
        self.load_memory() 
        
        c_primary = getattr(self, "current_theme_color", "#00ff00")
        self.setStyleSheet(f"QMainWindow {{ background-color: #12121c; color: #f5f5f7; border: 1px solid {c_primary}; }}")
        
        font_yolu = resource_path("orbitron.ttf")
        if os.path.exists(font_yolu):
            QFontDatabase.addApplicationFont(font_yolu)
        try: ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("MyCoreAssistant.CORE.v51")
        except: pass
            
        icon_yolu = resource_path("icon.ico")
        if os.path.exists(icon_yolu): 
            app_icon = QIcon(icon_yolu)
            self.setWindowIcon(app_icon); QApplication.setWindowIcon(app_icon)
                
        try:
            for f in os.listdir():
                if f.startswith("core_resp_") and f.endswith(".mp3"):
                    try: os.remove(f)
                    except: pass
        except: pass

        self.is_listening_active = True
        self.pomodoro_time = 0; self.pomo_timer = QTimer(self); self.pomo_timer.timeout.connect(self.update_pomodoro)
        
        self.clip = QApplication.clipboard()
        self.clip.dataChanged.connect(self.on_clipboard_change)
        self.latest_clip = ""; self.last_clip_time = 0
        
        self.setWindowTitle(f"{self.ai_name} — Centralized Operational Response Engine")
        self.setMinimumSize(1400, 850)
        self.showMaximized()
        
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        left_layout = QVBoxLayout(); left_layout.setAlignment(Qt.AlignTop)
        self.env_title = QLabel("ORTAM VERİLERİ", self); left_layout.addWidget(self.env_title)
        self.env_frame = QFrame(self); env_layout = QVBoxLayout(self.env_frame); env_layout.setContentsMargins(10, 5, 10, 5) 
        
        self.clock_label = QLabel("🕒 00:00:00", self); self.loc_label = QLabel(f"📍 {self.current_location}", self); self.weather_label = QLabel("☁️ ...", self)
        for lbl in [self.clock_label, self.loc_label, self.weather_label]: env_layout.addWidget(lbl)
            
        fin_lay = QHBoxLayout()
        self.lbl_usd = QLabel("USD: ...", self); self.lbl_eur = QLabel("EUR: ...", self); self.lbl_gbp = QLabel("GBP: ...", self)
        for lbl in [self.lbl_usd, self.lbl_eur, self.lbl_gbp]: fin_lay.addWidget(lbl)
        env_layout.addLayout(fin_lay); left_layout.addWidget(self.env_frame); left_layout.addSpacing(4) 
        
        self.sys_title = QLabel("SİSTEM DURUMU", self); left_layout.addWidget(self.sys_title)
        
        self.sys_frame = QFrame(self); sys_layout = QVBoxLayout(self.sys_frame)
        sys_layout.setContentsMargins(15, 15, 15, 15) 
        sys_layout.setSpacing(8) 
        
        self.cpu_label = QLabel("CPU Usage: %0", self)
        self.cpu_bar = QProgressBar(self); self.cpu_bar.setMaximum(100); self.cpu_bar.setFixedHeight(8) 
        
        self.ram_label = QLabel("RAM Usage: %0", self)
        self.ram_bar = QProgressBar(self); self.ram_bar.setMaximum(100); self.ram_bar.setFixedHeight(8) 
        
        self.net_label = QLabel(self); self.net_label.hide() 
        
        for w in [self.cpu_label, self.cpu_bar, self.ram_label, self.ram_bar]: sys_layout.addWidget(w)
        left_layout.addWidget(self.sys_frame); left_layout.addSpacing(4) 
        
        self.tasks_title = QLabel("BUGÜNKÜ YAPILACAKLAR", self); self.tasks_title.hide()
        self.tasks_box = QTextEdit(self); self.tasks_box.setText(self.saved_tasks); self.tasks_box.hide()
        
        self.health_title = QLabel("SAĞLIK PANELİ", self); left_layout.addWidget(self.health_title)
        self.health_frame = QFrame(self); health_layout = QVBoxLayout(self.health_frame); health_layout.setContentsMargins(10, 2, 10, 2); health_layout.setSpacing(1)
        
        s_lay = QHBoxLayout(); self.lbl_steps = QLabel(f"Günlük Adım: {self.health_data.get('steps', 0)} / 9000", self)
        self.btn_s_add = QPushButton("+500", self); self.btn_s_add.setFixedWidth(38); self.btn_s_add.clicked.connect(lambda: self.add_health("steps", 500))
        self.btn_s_edit = QPushButton("✏️", self); self.btn_s_edit.setFixedWidth(28); self.btn_s_edit.clicked.connect(lambda: self.set_health_manual("steps", "Adım"))
        s_lay.addWidget(self.lbl_steps); s_lay.addWidget(self.btn_s_add); s_lay.addWidget(self.btn_s_edit); health_layout.addLayout(s_lay)
        
        c_lay = QHBoxLayout(); self.lbl_cals = QLabel(f"Günlük Harcanan: {2200 + self.health_data.get('cals', 0)} / 3000 kcal", self)
        self.btn_c_add = QPushButton("+300", self); self.btn_c_add.setFixedWidth(38); self.btn_c_add.clicked.connect(lambda: self.add_health("cals", 300))
        self.btn_c_edit = QPushButton("✏️", self); self.btn_c_edit.setFixedWidth(28); self.btn_c_edit.clicked.connect(lambda: self.set_health_manual("cals", "Ekstra Harcanan Kalori"))
        c_lay.addWidget(self.lbl_cals); c_lay.addWidget(self.btn_c_add); c_lay.addWidget(self.btn_c_edit); health_layout.addLayout(c_lay)

        w_lay = QHBoxLayout(); self.lbl_water = QLabel(f"Su: {self.health_data.get('water', 0.0):.1f} / 2.5 L", self)
        self.btn_w_add = QPushButton("+0.5L", self); self.btn_w_add.setFixedWidth(38); self.btn_w_add.clicked.connect(lambda: self.add_health("water", 0.5))
        self.btn_w_edit = QPushButton("✏️", self); self.btn_w_edit.setFixedWidth(28); self.btn_w_edit.clicked.connect(lambda: self.set_health_manual("water", "Su"))
        w_lay.addWidget(self.lbl_water); w_lay.addWidget(self.btn_w_add); w_lay.addWidget(self.btn_w_edit); health_layout.addLayout(w_lay)

        dd_lay = QHBoxLayout(); self.lbl_dd = QLabel(f"Günlük Açık: {self.health_data.get('daily_deficit', 0)} / 1100 kcal", self)
        self.btn_dd_add = QPushButton("+100", self); self.btn_dd_add.setFixedWidth(38); self.btn_dd_add.clicked.connect(lambda: self.add_health("daily_deficit", 100))
        self.btn_dd_edit = QPushButton("✏️", self); self.btn_dd_edit.setFixedWidth(28); self.btn_dd_edit.clicked.connect(lambda: self.set_health_manual("daily_deficit", "Günlük Açık"))
        dd_lay.addWidget(self.lbl_dd); dd_lay.addWidget(self.btn_dd_add); dd_lay.addWidget(self.btn_dd_edit); health_layout.addLayout(dd_lay)

        wd_lay = QHBoxLayout(); self.lbl_wd = QLabel(f"1 KG Hedefi (Toplam Açık): {self.health_data.get('weekly_deficit', 0)} / 7700 kcal", self)
        self.btn_wd_add = QPushButton("+100", self); self.btn_wd_add.setFixedWidth(38); self.btn_wd_add.clicked.connect(lambda: self.add_health("weekly_deficit", 100))
        self.btn_wd_edit = QPushButton("✏️", self); self.btn_wd_edit.setFixedWidth(28); self.btn_wd_edit.clicked.connect(lambda: self.set_health_manual("weekly_deficit", "Toplam Açık"))
        wd_lay.addWidget(self.lbl_wd); wd_lay.addWidget(self.btn_wd_add); wd_lay.addWidget(self.btn_wd_edit); health_layout.addLayout(wd_lay)

        left_layout.addWidget(self.health_frame); left_layout.addSpacing(4)
        
        self.qa_title = QLabel("HIZLI ERİŞİM", self); left_layout.addWidget(self.qa_title)
        self.qa_frame = QFrame(self); qa_layout = QGridLayout(self.qa_frame); qa_layout.setContentsMargins(2, 2, 2, 2); qa_layout.setSpacing(2)
        
        qa_buttons = [("YouTube", "https://youtube.com", "▶"), ("WhatsApp", "https://web.whatsapp.com", "💬"), ("TOD", "https://www.todtv.com.tr/canli-tv/bein-sports-1?c=spor", "⚽"), ("X", "https://twitter.com/home", "✖"), ("Gemini", "https://gemini.google.com", "✨"), ("Haritalar", "https://maps.google.com", "🗺"), ("Google", "https://google.com", "🔍"), ("Kick", "https://kick.com", "")]
        row, col = 0, 0
        self.qa_buttons_list = []
        os.makedirs("icons", exist_ok=True)
        
        for n, u, e in qa_buttons:
            b = QPushButton(f"  {n}", self)
            ip = f"icons/{n}.png"
            if not os.path.exists(ip) and "http" in u:
                try: open(ip, 'wb').write(requests.get(f"https://www.google.com/s2/favicons?domain={u}&sz=64", timeout=2).content)
                except: pass
            if os.path.exists(ip): b.setIcon(QIcon(ip)); b.setIconSize(QSize(20, 20))
            else: b.setText(f"{e} {n}")
            b.clicked.connect(lambda checked, url=u: run_async(f"start {url}"))
            qa_layout.addWidget(b, row, col); self.qa_buttons_list.append(b)
            col += 1
            if col > 3: col = 0; row += 1
                
        left_layout.addWidget(self.qa_frame); left_layout.addSpacing(4)
        self.calendar_title = QLabel("TAKVİM", self); left_layout.addWidget(self.calendar_title)
        self.calendar = QCalendarWidget(self); self.calendar.clicked.connect(self.handle_calendar_click); left_layout.addWidget(self.calendar)
        self.signature_label = QLabel("Geliştiren: [Adınız Soyadınız]", self); self.signature_label.setAlignment(Qt.AlignCenter); left_layout.addWidget(self.signature_label)
        
        main_layout.addLayout(left_layout, stretch=1)
        
        self.fetch_weather() 
        self.finance_worker = FinanceWorker(); self.finance_worker.rates_ready.connect(self.update_finance_ui); self.finance_worker.start()
        self.finance_timer = QTimer(self); self.finance_timer.timeout.connect(self.finance_worker.start); self.finance_timer.start(28800000) 
        
        self.sys_worker = SysWorker()
        self.sys_worker.update_signal.connect(self.update_sys_ui)
        self.sys_worker.start()
        
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock_and_notes)
        self.clock_timer.start(1000) 
        
        center_layout = QVBoxLayout(); center_layout.setAlignment(Qt.AlignCenter) 
        self.ai_name_label = QLabel(self.ai_name, self); self.ai_name_label.setAlignment(Qt.AlignCenter); center_layout.addWidget(self.ai_name_label)
        
        pomo_lay = QHBoxLayout(); pomo_lay.setAlignment(Qt.AlignCenter)
        self.btn_pomo_start = QPushButton("⏱ ODAK", self); self.btn_pomo_start.setFixedSize(80, 25); self.btn_pomo_start.clicked.connect(self.manual_start_pomodoro); pomo_lay.addWidget(self.btn_pomo_start)
        self.lbl_pomodoro = QLabel("", self); self.lbl_pomodoro.setAlignment(Qt.AlignCenter); pomo_lay.addWidget(self.lbl_pomodoro)
        self.btn_pomo_stop = QPushButton("✖", self); self.btn_pomo_stop.setFixedSize(25, 25); self.btn_pomo_stop.clicked.connect(lambda: self.worker.action_triggered.emit("stop_pomodoro", "") if hasattr(self, 'worker') else self.stop_pomodoro()); self.btn_pomo_stop.hide(); pomo_lay.addWidget(self.btn_pomo_stop)
        center_layout.addLayout(pomo_lay); center_layout.addStretch(1) 
        
        self.orb = AnimatedOrbWidget(self, size=400); center_layout.addWidget(self.orb, alignment=Qt.AlignCenter)
        self.status_label = QLabel("SİSTEMLER AKTİF — SÜREKLİ DİNLENİYOR...", self); self.status_label.setAlignment(Qt.AlignCenter); center_layout.addWidget(self.status_label); center_layout.addSpacing(10)
        self.center_mic_btn = QPushButton("🎤 MİKROFONU KAPAT", self); self.center_mic_btn.setFixedSize(250, 45); self.center_mic_btn.clicked.connect(self.toggle_continuous_listening); center_layout.addWidget(self.center_mic_btn, alignment=Qt.AlignCenter); center_layout.addSpacing(10)
        
        self.media_frame = QFrame(self); self.media_frame.setObjectName("MediaFrame")
        media_lay = QHBoxLayout(self.media_frame); media_lay.setAlignment(Qt.AlignCenter); media_lay.setContentsMargins(20, 5, 20, 5); media_lay.setSpacing(15)
        self.yt_icon_lbl = QLabel(self)
        if os.path.exists("icons/YT Music.png"): self.yt_icon_lbl.setPixmap(QPixmap("icons/YT Music.png").scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else: self.yt_icon_lbl.setText("🎵")
        self.yt_icon_lbl.setCursor(Qt.PointingHandCursor)
        
        self.yt_icon_lbl.mousePressEvent = lambda event: run_async("start https://music.youtube.com/playlist?list=PLGuea1yszEwjIJgc6PL_b-Spy-4jCODSh")
            
        self.btn_prev = QPushButton("⏮", self); self.btn_play = QPushButton("⏯", self); self.btn_next = QPushButton("⏭", self)
        media_lay.addWidget(self.yt_icon_lbl)
        for mb in [self.btn_prev, self.btn_play, self.btn_next]: mb.setFixedSize(40, 40); media_lay.addWidget(mb)
            
        self.btn_prev.clicked.connect(lambda: self.trigger_media("media_prev", "")); self.btn_play.clicked.connect(lambda: self.trigger_media("media_play_pause", "")); self.btn_next.clicked.connect(lambda: self.trigger_media("media_next", ""))
        center_layout.addWidget(self.media_frame, alignment=Qt.AlignCenter); center_layout.addStretch(1) 
        main_layout.addLayout(center_layout, stretch=3) 
        
        right_layout = QVBoxLayout(); right_layout.setAlignment(Qt.AlignTop)
        self.log_title = QLabel("SİSTEM GÜNLÜĞÜ VE SOHBET", self); right_layout.addWidget(self.log_title)
        self.log_box = QTextEdit(self); self.log_box.setReadOnly(True)
        self.log_box.setText(f">> {self.ai_name} v5.1 Stabil Sürüm.\n>> Modüller entegre edildi. Ortam bağımsız algılama devrede.")
        self.saved_chat_history += f"\n\n--- YENİ OTURUM: {datetime.now().strftime('%d/%m/%Y %H:%M')} ---\n"
        right_layout.addWidget(self.log_box); right_layout.addSpacing(5)
        
        self.notes_title = QLabel("SESLİ NOTLAR (OBSIDIAN)", self); right_layout.addWidget(self.notes_title)
        self.notes_box = QTextEdit(self); self.notes_box.setReadOnly(True); self.notes_box.setText(self.saved_notes); self.notes_box.setMaximumHeight(150)
        right_layout.addWidget(self.notes_box); right_layout.addSpacing(5)
        
        chat_box_layout = QHBoxLayout()
        self.settings_btn = QPushButton("⚙️", self); self.settings_btn.clicked.connect(self.open_settings); chat_box_layout.addWidget(self.settings_btn)
        self.file_btn = QPushButton("+", self); self.file_btn.clicked.connect(self.select_file); chat_box_layout.addWidget(self.file_btn)
        self.chat_input = QLineEdit(self); self.chat_input.setPlaceholderText("Komut yazın veya action tetikleyin..."); self.chat_input.returnPressed.connect(self.send_message); chat_box_layout.addWidget(self.chat_input)
        self.send_btn = QPushButton("GÖNDER", self); self.send_btn.clicked.connect(self.send_message); chat_box_layout.addWidget(self.send_btn)
        right_layout.addLayout(chat_box_layout); main_layout.addLayout(right_layout, stretch=1)

        self.apply_styles(); self.update_health_ui()
        self.continuous_worker = ContinuousListenWorker(); self.continuous_worker.text_ready.connect(self.handle_continuous_speech); self.continuous_worker.start()
        threading.Thread(target=run_core, daemon=True).start(); threading.Thread(target=start_global_hotkey, daemon=True).start()
        
        self.daily_timer = QTimer(self); self.daily_timer.timeout.connect(self.check_daily_reminders); self.daily_timer.start(3600000); QTimer.singleShot(1000, self.check_daily_reminders) 

    def apply_neon_glow(self, widget, color_hex="#00ff00", blur_radius=30, alpha=200):
        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(blur_radius)
        color = QColor(color_hex)
        color.setAlpha(alpha)
        glow.setColor(color)
        glow.setOffset(0, 0)
        widget.setGraphicsEffect(glow)

    def on_clipboard_change(self):
        text = self.clip.text().strip()
        current_time = time.time()
        cumle_sayisi = len([s for s in text.replace('!', '.').replace('?', '.').split('.') if len(s.strip()) > 3])
        satir_sayisi = len([s for s in text.split('\n') if len(s.strip()) > 3])
        if text and text != self.latest_clip and (cumle_sayisi >= 3 or satir_sayisi >= 3) and (current_time - self.last_clip_time > 5):
            self.latest_clip = text
            self.last_clip_time = current_time
            self.append_to_log(">> [PANO]: Yeni ve uzun veri tespit edildi.")
            msg = "Efendim, panoya oldukça uzun bir metin kopyaladınız. Bunu Obsidian günlüğünüze kalıcı olarak kaydedeyim mi?"
            self.worker = ChatWorker(msg, msg, None, self.current_model, self.voice_speed, self.voice_volume, self.ai_name, self.current_salutation, self.custom_api_key, is_direct_speech=True)
            self.worker.start()

    def update_finance_ui(self, usd, eur, gbp): self.lbl_usd.setText(f"USD: {usd}"); self.lbl_eur.setText(f"EUR: {eur}"); self.lbl_gbp.setText(f"GBP: {gbp}")

    def trigger_media(self, action_type, query=""):
        if action_type == "media_play_pause": ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0); ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 2, 0)
        elif action_type == "media_next": ctypes.windll.user32.keybd_event(VK_MEDIA_NEXT_TRACK, 0, 0, 0); ctypes.windll.user32.keybd_event(VK_MEDIA_NEXT_TRACK, 0, 2, 0)
        elif action_type == "media_prev": ctypes.windll.user32.keybd_event(VK_MEDIA_PREV_TRACK, 0, 0, 0); ctypes.windll.user32.keybd_event(VK_MEDIA_PREV_TRACK, 0, 2, 0)

    def manual_start_pomodoro(self):
        val, ok = QInputDialog.getInt(self, "Odak Modu", "Kaç dakika odaklanmak istersiniz?", 40, 1, 180)
        if ok: self.start_pomodoro(val)

    def start_pomodoro(self, minutes=40):
        self.pomodoro_time = int(minutes) * 60
        self.lbl_pomodoro.setStyleSheet(f"font-family: 'Consolas'; font-size: 24px; font-weight: bold; color: {self.current_theme_color.split(',')[0]};")
        self.btn_pomo_start.hide()
        self.btn_pomo_stop.show()
        self.pomo_timer.start(1000)
        run_async("start https://www.youtube.com/live/sF80I-TQiW0?si=bpJvHBdhLIqSmiUz")

    def stop_pomodoro(self): 
        self.pomo_timer.stop()
        self.pomodoro_time = 0
        self.lbl_pomodoro.setText("")
        self.btn_pomo_stop.hide()
        self.btn_pomo_start.show()

    def update_pomodoro(self):
        if self.pomodoro_time > 0:
            self.pomodoro_time -= 1
            mins, secs = divmod(self.pomodoro_time, 60)
            self.lbl_pomodoro.setText(f"🎯 ODAK MODU: {mins:02d}:{secs:02d}")
        else:
            self.stop_pomodoro()
            msg = "Odaklanma süreniz doldu efendim. Lütfen 5 dakika mola veriniz."
            self.append_to_log(f">> [SİSTEM]: {msg}")
            self.worker = ChatWorker(msg, msg, None, self.current_model, self.voice_speed, self.voice_volume, self.ai_name, self.current_salutation, self.custom_api_key, is_direct_speech=True)
            self.worker.start()

    def add_obsidian_note(self, content):
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
        try:
            with open("CORE_Obsidian_Notes.md", "a", encoding="utf-8") as f: 
                f.write(f"- **{timestamp}**: {content}\n")
        except: pass
        self.sync_obsidian_notes()

    def update_health_ui(self):
        self.lbl_steps.setText(f"Günlük Adım: {self.health_data.get('steps', 0)} / 9000")
        self.lbl_cals.setText(f"Günlük Harcanan: {2200 + self.health_data.get('cals', 0)} / 3000 kcal")
        self.lbl_water.setText(f"Su: {self.health_data.get('water', 0.0):.1f} / 2.5 L")
        self.lbl_dd.setText(f"Günlük Kalori Açığı: {self.health_data.get('daily_deficit', 0)} / 1100 kcal")
        self.lbl_wd.setText(f"1 KG Hedefi (Toplam Açık): {self.health_data.get('weekly_deficit', 0)} / 7700 kcal")
    
    def add_health(self, key, amount):
        self.health_data[key] = self.health_data.get(key, 0) + amount
        if key == "steps": self.health_data["weekly_steps"] = self.health_data.get("weekly_steps", 0) + amount
        elif key == "cals": self.health_data["weekly_cals"] = self.health_data.get("weekly_cals", 0) + amount
        elif key == "daily_deficit": self.health_data["weekly_deficit"] = self.health_data.get("weekly_deficit", 0) + amount
        self.update_health_ui(); self.save_memory()

    def set_health_manual(self, key, title):
        val, ok = QInputDialog.getDouble(self, f"{title} Güncelle", f"Yeni {title} değerini girin:", 0, 0, 100000, 1 if key == "water" else 0)
        if ok:
            if key == "water": self.health_data["water"] = val
            elif key in ["weekly_steps", "weekly_cals", "weekly_deficit"]: self.health_data[key] = int(val)
            else:
                diff = int(val) - self.health_data.get(key, 0); self.health_data[key] = int(val)
                if key == "steps": self.health_data["weekly_steps"] = self.health_data.get("weekly_steps", 0) + diff
                elif key == "cals": self.health_data["weekly_cals"] = self.health_data.get("weekly_cals", 0) + diff
                elif key == "daily_deficit": self.health_data["weekly_deficit"] = self.health_data.get("weekly_deficit", 0) + diff
            self.update_health_ui(); self.save_memory()

    def check_daily_reminders(self):
        now = datetime.now(); today_str = now.strftime("%dd.%m.%Y"); tomorrow = now + timedelta(days=1); tom_str = tomorrow.strftime("%dd.%m.%Y")
        e_tom = self.calendar_events.get(tom_str, []) + self.recurring_events.get(str(tomorrow.day), [])

        if now.weekday() == 0 and getattr(self, 'last_weekly_reset', "") != today_str:
            self.health_data["weekly_steps"] = 0; self.health_data["weekly_cals"] = 0; self.health_data["weekly_deficit"] = 0; self.last_weekly_reset = today_str; self.update_health_ui()

        if self.health_data.get("last_reset_date", "") != today_str:
            self.health_data["steps"] = 0; self.health_data["cals"] = 0; self.health_data["water"] = 0.0; self.health_data["daily_deficit"] = 0; self.health_data["last_reset_date"] = today_str; self.update_health_ui(); self.save_memory()

        if getattr(self, 'last_reminded_date', "") != today_str and e_tom:
            self.last_reminded_date = today_str; msg = f"Yarın için planlanmış {len(e_tom)} ödemeniz var."
            for ev in e_tom: self.append_to_log(f">> [TAKVİM HATIRLATMASI]: Yarın: {ev['desc']}")
            self.append_to_log(f">> [SİSTEM]: {msg}")
            ChatWorker(msg, msg, None, self.current_model, self.voice_speed, self.voice_volume, self.ai_name, self.current_salutation, self.custom_api_key, is_direct_speech=True).start(); self.save_memory()

    def handle_calendar_click(self, qdate):
        d_str = qdate.toString("dd.MM.yyyy")
        d_day = str(qdate.day())
        dlg = DayManagerDialog(self, d_str, d_day, self.current_theme_color.split(',')[0])
        dlg.exec_()
        self.append_to_log(f">> [TAKVİM]: {d_str} güncellendi.")
        
    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.ai_name = data.get("ai_name", "C.O.R.E.")
                    
                    raw_color = data.get("theme_color", "#00ff00")
                    if "," in raw_color: self.current_theme_color = raw_color.split(",")[0]
                    else: self.current_theme_color = raw_color
                        
                    self.current_location = data.get("location", "Istanbul,Turkiye")
                    self.current_model = data.get("model", "gemini-3.8-flash")
                    self.voice_speed = data.get("speed", "+15%"); self.voice_volume = data.get("volume", "100%")
                    self.current_salutation = data.get("salutation", "efendim"); self.custom_api_key = data.get("api_key", "")
                    self.saved_tasks = data.get("tasks", "- Python kodlarını düzenle")
                    self.saved_notes = data.get("notes", ""); self.saved_chat_history = data.get("chat_history", "")
                    self.summary_prefs = data.get("summary_prefs", {"time": True, "weather": True, "tasks": True, "football": True, "currency": True})
                    self.calendar_events = data.get("calendar_events", {}); self.recurring_events = data.get("recurring_events", {})
                    self.last_reminded_date = data.get("last_reminded_date", ""); self.last_weekly_reset = data.get("last_weekly_reset", "")
                    self.health_data = data.get("health_data", {"steps": 0, "cals": 0, "water": 0.0, "weekly_steps": 0, "weekly_cals": 0, "daily_deficit": 0, "weekly_deficit": 0, "last_reset_date": ""})
                    for k in ["weekly_steps", "weekly_cals", "daily_deficit", "weekly_deficit"]:
                        if k not in self.health_data: self.health_data[k] = 0
                    if "last_reset_date" not in self.health_data: self.health_data["last_reset_date"] = ""
                    self.current_image_path = None
            except: self.set_default_memory()
        else: self.set_default_memory()

    def set_default_memory(self):
        self.ai_name = "C.O.R.E."; self.current_theme_color = "#00ff00"; self.current_location = "Istanbul,Turkiye"
        self.current_model = "gemini-3.8-flash"; self.voice_speed = "+15%"; self.voice_volume = "100%"; self.current_salutation = "efendim"
        self.custom_api_key = ""; self.saved_tasks = "- Python kodlarını düzenle"
        self.saved_notes = ""; self.saved_chat_history = ""
        self.summary_prefs = {"time": True, "weather": True, "tasks": True, "football": True, "currency": True}
        self.calendar_events = {}; self.recurring_events = {}; self.last_reminded_date = ""; self.last_weekly_reset = ""
        self.health_data = {"steps": 0, "cals": 0, "water": 0.0, "weekly_steps": 0, "weekly_cals": 0, "daily_deficit": 0, "weekly_deficit": 0, "last_reset_date": ""}
        self.current_image_path = None

    def save_memory(self):
        data_to_save = {
            "ai_name": self.ai_name, "theme_color": self.current_theme_color, "location": self.current_location, 
            "model": self.current_model, "speed": self.voice_speed, "volume": self.voice_volume, 
            "salutation": self.current_salutation, "api_key": self.custom_api_key, 
            "tasks": self.tasks_box.toPlainText(), "reminders": "", 
            "notes": self.notes_box.toPlainText(), "chat_history": self.saved_chat_history, 
            "summary_prefs": self.summary_prefs, "calendar_events": self.calendar_events, 
            "recurring_events": self.recurring_events, "last_reminded_date": self.last_reminded_date, 
            "last_weekly_reset": self.last_weekly_reset, "health_data": self.health_data
        }
        with open(self.memory_file, "w", encoding="utf-8") as f: json.dump(data_to_save, f, ensure_ascii=False, indent=4)

    def closeEvent(self, event):
        if hasattr(self, 'continuous_worker'): self.continuous_worker.stop()
        if hasattr(self, 'sys_worker'): self.sys_worker.stop()
        self.save_memory(); event.accept()

    def apply_styles(self):
        c = self.current_theme_color.split(",")[0]
        bg = "#12121c"; p_bg = "#1b1b2b"; bc = "#3d3d5c"; tc = "#f5f5f7"; mt = "#9a9ab0"
        self.setStyleSheet(f"QMainWindow {{ background-color: {bg}; color: {tc}; }}")
        
        ts = f"font-family: 'Orbitron', 'Consolas'; font-weight: bold; font-size: 13px; border: 1px solid {c}; border-radius: 8px; padding: 5px; margin-bottom: 5px; margin-top: 5px; color: {c}; background-color: rgba(27, 27, 43, 0.7);"
        
        paneller = [self.env_title, self.sys_title, self.log_title, self.health_title, self.qa_title, self.calendar_title, self.notes_title]
        for lbl in paneller:
            if lbl:
                lbl.setStyleSheet(ts)
                lbl.setAlignment(Qt.AlignCenter)
                self.apply_neon_glow(lbl, c, blur_radius=15, alpha=150)

        fs = f"border: 1px solid {bc}; border-radius: 6px; background-color: {p_bg};"
        self.env_frame.setStyleSheet(fs); self.sys_frame.setStyleSheet(fs); self.health_frame.setStyleSheet(fs); self.qa_frame.setStyleSheet(fs)
        
        self.clock_label.setStyleSheet(f"border: none; font-family: 'Orbitron', 'Consolas'; font-size: 20px; font-weight: bold; letter-spacing: 2px; color: {c}; background: transparent;")
        self.ai_name_label.setStyleSheet(f"font-family: 'Orbitron', 'Consolas'; font-size: 48px; font-weight: bold; color: {c}; letter-spacing: 12px; margin-top: 10px;")
        for lbl in [self.lbl_usd, self.lbl_eur, self.lbl_gbp]: lbl.setStyleSheet(f"border: none; font-family: 'Orbitron', 'Consolas'; font-size: 11px; font-weight: bold; color: {c}; background: transparent;")
        
        self.loc_label.setStyleSheet(f"border: none; font-family: 'Consolas'; font-size: 11px; color: {mt}; background: transparent;")
        self.weather_label.setStyleSheet(f"border: none; font-family: 'Consolas'; font-size: 11px; color: {tc}; background: transparent;")
        
        for lbl in [self.cpu_label, self.ram_label, getattr(self, 'net_label', None)]: 
            if lbl:
                lbl.setStyleSheet(f"font-family: 'Consolas'; font-size: 11px; margin-top: 2px; color: {mt}; border: none; background: transparent;")
                
        for lbl in [self.lbl_steps, self.lbl_cals, self.lbl_water, self.lbl_dd, self.lbl_wd]: lbl.setStyleSheet(f"font-family: 'Consolas'; font-size: 10px; color: {tc}; border: none;")
        self.status_label.setStyleSheet(f"font-family: 'Consolas'; font-size: 14px; font-weight: bold; margin-top: 10px; letter-spacing: 2px; color: {tc};")
        self.signature_label.setStyleSheet(f"font-family: 'Consolas'; font-size: 11px; font-weight: bold; color: {mt}; margin-top: 3px;")
        
        mc = "#e74c3c" if not self.is_listening_active else c
        self.center_mic_btn.setStyleSheet(f"background-color: {p_bg}; border: 2px solid {mc}; border-radius: 20px; color: {mc}; font-family: 'Consolas'; font-weight: bold; font-size: 13px; padding: 10px;")
        
        self.apply_neon_glow(self.center_mic_btn, mc, blur_radius=40, alpha=200)
        self.apply_neon_glow(self.health_frame, c, blur_radius=15, alpha=60)
        self.apply_neon_glow(self.sys_frame, c, blur_radius=15, alpha=60)

        self.btn_pomo_start.setStyleSheet(f"background-color: transparent; border: 1px solid {c}; border-radius: 12px; color: {c}; font-weight: bold; font-size: 11px; font-family: 'Consolas';")
        self.btn_pomo_stop.setStyleSheet(f"background-color: transparent; border: 1px solid #e74c3c; border-radius: 12px; color: #e74c3c; font-weight: bold; font-family: 'Consolas';")
        
        bs = f"QProgressBar {{ border: 1px solid {bc}; background-color: {bg}; text-align: center; color: transparent; border-radius: 4px; }} QProgressBar::chunk {{ background-color: {c}; border-radius: 3px; }}"
        self.cpu_bar.setStyleSheet(bs); self.ram_bar.setStyleSheet(bs)
        
        bxs = f"background-color: {p_bg}; border: 1px solid {bc}; border-radius: 6px; color: {tc}; font-family: 'Consolas'; font-size: 11px; padding: 5px;"
        for box in [self.log_box, self.tasks_box, self.notes_box]: box.setStyleSheet(bxs)
        self.chat_input.setStyleSheet(f"background-color: {bg}; border: 1px solid {bc}; border-radius: 6px; color: {tc}; font-family: 'Consolas'; font-size: 12px; padding: 8px;")
        
        self.calendar.setStyleSheet(f"QCalendarWidget QWidget {{ alternate-background-color: {p_bg}; font-family: 'Consolas'; }} QCalendarWidget QToolButton {{ color: {c}; background-color: transparent; border: none; font-size: 11px; font-weight: bold; font-family: 'Consolas'; }} QCalendarWidget QMenu {{ background-color: {bg}; color: {c}; font-family: 'Consolas'; }} QCalendarWidget QSpinBox {{ background-color: {p_bg}; color: {c}; font-family: 'Consolas'; }} QCalendarWidget QAbstractItemView:enabled {{ background-color: {p_bg}; color: {tc}; selection-background-color: {c}; selection-color: #000; border: 1px solid {bc}; border-radius: 6px; font-family: 'Consolas'; }}")
        bns = f"background-color: {p_bg}; border: 1px solid {bc}; border-radius: 6px; color: {c}; font-family: 'Consolas'; font-weight: bold; font-size: 12px; padding: 6px 10px;"
        self.settings_btn.setStyleSheet(bns); self.file_btn.setStyleSheet(bns); self.send_btn.setStyleSheet(bns)
        self.yt_icon_lbl.setStyleSheet("background: transparent; border: none;")
        self.media_frame.setStyleSheet(f"QFrame#MediaFrame {{ background-color: rgba(27, 27, 43, 0.6); border: 1px solid {bc}; border-radius: 25px; }}")
        mbs = f"QPushButton {{ background-color: transparent; border: none; border-radius: 20px; color: {tc}; font-size: 20px; }} QPushButton:hover {{ background-color: {c}; color: #050505; }}"
        for mb in [self.btn_prev, self.btn_play, self.btn_next]: mb.setStyleSheet(mbs)
        
        sbs = f"background-color: {bg}; border: 1px solid {bc}; border-radius: 4px; color: {c}; font-family: 'Consolas'; font-weight: bold; font-size: 9px; padding: 1px;"
        for btn in [self.btn_s_add, self.btn_s_edit, self.btn_c_add, self.btn_c_edit, self.btn_w_add, self.btn_w_edit, self.btn_dd_add, self.btn_dd_edit, self.btn_wd_add, self.btn_wd_edit]: btn.setStyleSheet(sbs)
        if hasattr(self, 'qa_buttons_list'):
            for btn in self.qa_buttons_list: btn.setStyleSheet(f"background-color: #2b2b3b; border: 1px solid {bc}; border-radius: 4px; color: #ffffff; font-family: 'Consolas'; font-weight: bold; font-size: 11px; padding: 5px;")
            
        if hasattr(self, 'orb') and hasattr(self.orb, 'set_state'):
            self.orb.update()

    def open_settings(self):
        d = SettingsDialog(self, self.current_model, self.voice_speed, self.voice_volume, self.current_theme_color, self.ai_name, self.current_location, self.current_salutation, self.custom_api_key, self.summary_prefs)
        if d.exec_():
            self.ai_name = d.name_input.text().strip()
            self.current_salutation = d.salutation_input.text().strip()
            self.custom_api_key = d.api_key_input.text().strip()
            
            selected_text = d.color_combo.currentText()
            if selected_text == "Özel Renk Seç (Palet)...":
                self.current_theme_color = d.custom_hex
            else:
                self.current_theme_color = d.colors[selected_text]
                
            self.summary_prefs = d.get_summary_prefs()
            if d.loc_input.text().strip() != self.current_location: 
                self.current_location = d.loc_input.text().strip(); self.loc_label.setText(f"📍 {self.current_location}"); self.fetch_weather() 
            self.current_model, self.voice_speed, self.voice_volume = d.model_combo.currentText(), d.speed_combo.currentText(), d.volume_combo.currentText()
            self.ai_name_label.setText(self.ai_name); self.setWindowTitle(f"{self.ai_name} — Centralized Operational Response Engine")
            self.apply_styles(); self.save_memory(); self.append_to_log(f">> [SİSTEM]: Ayarlar güncellendi.")

    def fetch_weather(self): self.ww = WeatherWorker(self.current_location); self.ww.weather_ready.connect(lambda w: self.weather_label.setText(w)); self.ww.start()

    def update_clock_and_notes(self):
        self.clock_label.setText(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
        self.sync_obsidian_notes()

    def update_sys_ui(self, cpu, ram_pct, ram_used, ram_total, gpu_text):
        self.cpu_label.setText(f"CPU Usage: %{cpu}")
        self.cpu_bar.setValue(int(cpu))
        self.ram_label.setText(f"RAM Usage: %{ram_pct} ({ram_used:.1f} / {ram_total:.1f} GB)")
        self.ram_bar.setValue(int(ram_pct))

    def select_file(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Dosya Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg);;Tüm Dosyalar (*.*)")
        if fn: self.current_image_path = fn; self.chat_input.setText("Bu resmi incele ve bana ne gördüğünü söyle.") 

    def toggle_continuous_listening(self):
        if self.is_listening_active: 
            self.is_listening_active = False; self.continuous_worker.stop(); self.center_mic_btn.setText("🎤 MİKROFONU AÇ"); self.status_label.setText("SİSTEMLER AKTİF — DİNLEME KAPALI"); self.append_to_log(f">> [{self.ai_name}]: Dinleme kapatıldı."); self.orb.set_state("bekliyor")
        else: 
            self.is_listening_active = True; self.continuous_worker = ContinuousListenWorker(); self.continuous_worker.text_ready.connect(self.handle_continuous_speech); self.continuous_worker.start(); self.center_mic_btn.setText("🎤 MİKROFONU KAPAT"); self.status_label.setText("SİSTEMLER AKTİF — SÜREKLİ DİNLENİYOR..."); self.append_to_log(f">> [{self.ai_name}]: Dinleme başlatıldı."); self.orb.set_state("bekliyor")
        self.apply_styles()

    def handle_continuous_speech(self, text):
        if self.is_listening_active and text: self.chat_input.setText(text); self.send_message()

    def send_message(self):
        u_txt = self.chat_input.text().strip()
        if u_txt:
            self.append_to_log(f">> Kullanıcı: {u_txt}")
            self.chat_input.clear()
            self.orb.set_state("dusunuyor")
            
            # --- GÜNAYDIN ÇAKIŞMASI BURADAN ÇÖZÜLDÜ ---
            # Sadece tek başına "günaydın" veya "günaydın core" yazılırsa özeti açar
            if u_txt.lower() in ["günaydın", "gunaydin", "günaydın c.o.r.e.", "günaydın core"]: 
                self.trigger_morning_summary()
                return
            # ------------------------------------------
                
            g_txt = u_txt
            if any(w in u_txt.lower() for w in ["ne zaman", "abonelik", "takvim", "ödeme", "maç", "mac", "kimle", "kaçta"]):
                b = datetime.now(); a = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
                b_str = f"{b.day} {a[b.month]} {b.year}"
                g_txt = u_txt + f"\n\n[SİSTEM BİLGİSİ]: Bugün: {b_str}. Takvim: {json.dumps(self.calendar_events, ensure_ascii=False)}, Abone: {json.dumps(self.recurring_events, ensure_ascii=False)}. DİKKAT: 1) Markdown KULLANMA. 2) Tarihi bugünü ({b_str}) baz alarak yap."
                
            self.worker = ChatWorker(u_txt, g_txt, getattr(self, 'current_image_path', None), self.current_model, self.voice_speed, self.voice_volume, self.ai_name, self.current_salutation, self.custom_api_key, False, self.health_data)
            self.current_image_path = None
            self.worker.response_ready.connect(self.handle_ai_response); self.worker.task_added.connect(self.handle_task_added); self.worker.action_triggered.connect(self.handle_action_triggered); self.worker.close_app_signal.connect(self.close); self.worker.state_changed.connect(self.orb.set_state); self.worker.start()

    def handle_action_triggered(self, action_type, query):
        if action_type == "media_play_pause": self.trigger_media("media_play_pause", "")
        elif action_type == "media_next": self.trigger_media("media_next", "")
        elif action_type == "media_prev": self.trigger_media("media_prev", "")
        elif action_type == "close_app":
            QApplication.quit()
        elif action_type == "start_pomodoro": self.start_pomodoro(int(query) if query else 40)
        elif action_type == "stop_pomodoro": self.stop_pomodoro()
        elif action_type == "reset_weekly": self.health_data["weekly_steps"] = 0; self.health_data["weekly_cals"] = 0; self.health_data["weekly_deficit"] = 0; self.update_health_ui(); self.save_memory()
        elif action_type == "delete_note":
            try:
                hedef = query.strip()
                with open("CORE_Obsidian_Notes.md", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                with open("CORE_Obsidian_Notes.md", "w", encoding="utf-8") as f:
                    for line in lines:
                        temiz_satir = turkce_karakter_temizle(line)
                        if hedef not in temiz_satir:
                            f.write(line)
                self.sync_obsidian_notes()
                self.append_to_log(f">> [OBSIDIAN]: '{query}' içeren not silindi.")
            except Exception as e: 
                pass
        elif action_type == "save_clipboard":
            if hasattr(self, 'latest_clip') and self.latest_clip:
                self.add_obsidian_note(f"Panodan Kaydedildi: {self.latest_clip}"); self.latest_clip = "" 
        elif action_type == "goodnight_protocol":
            try: ctypes.windll.user32.SendMessageW(0xFFFF, 0x319, 0, 0x80000)
            except: pass
            self.add_obsidian_note("Gün sonlandırıldı, hedefler %80 tamamlandı. Sistem uyku moduna geçti.")
            os.system("shutdown /s /t 60")
        elif action_type == "game_mode":
            run_async("taskkill /F /IM msedge.exe /T >nul 2>&1")
            run_async("taskkill /F /IM chrome.exe /T >nul 2>&1")
            run_async("start steam://open/games")
        elif action_type == "stop_game_mode":
            self.append_to_log(f">> [SİSTEM]: Oyun modu kapatıldı, normal moda dönüldü.")  
            
        elif action_type.startswith("set_") or action_type.startswith("add_"):
            try:
                v = float(query)
                if action_type == "set_steps": d = int(v) - self.health_data.get("steps", 0); self.health_data["steps"] = int(v); self.health_data["weekly_steps"] = self.health_data.get("weekly_steps", 0) + d
                elif action_type == "add_steps": self.health_data["steps"] += int(v); self.health_data["weekly_steps"] = self.health_data.get("weekly_steps", 0) + int(v)
                elif action_type == "set_cals": d = int(v) - self.health_data.get("cals", 0); self.health_data["cals"] = int(v); self.health_data["weekly_cals"] = self.health_data.get("weekly_cals", 0) + d
                elif action_type == "add_cals": self.health_data["cals"] += int(v); self.health_data["weekly_cals"] = self.health_data.get("weekly_cals", 0) + int(v)
                elif action_type == "set_weekly_steps": self.health_data["weekly_steps"] = int(v)
                elif action_type == "add_weekly_steps": self.health_data["weekly_steps"] = self.health_data.get("weekly_steps", 0) + int(v)
                elif action_type == "set_weekly_cals": self.health_data["weekly_cals"] = int(v)
                elif action_type == "add_weekly_cals": self.health_data["weekly_cals"] = self.health_data.get("weekly_cals", 0) + int(v)
                elif action_type == "set_daily_deficit": d = int(v) - self.health_data.get("daily_deficit", 0); self.health_data["daily_deficit"] = int(v); self.health_data["weekly_deficit"] = self.health_data.get("weekly_deficit", 0) + d
                elif action_type == "add_daily_deficit": self.health_data["daily_deficit"] = self.health_data.get("daily_deficit", 0) + int(v); self.health_data["weekly_deficit"] = self.health_data.get("weekly_deficit", 0) + int(v)
                elif action_type == "set_weekly_deficit": self.health_data["weekly_deficit"] = int(v)
                elif action_type == "add_weekly_deficit": self.health_data["weekly_deficit"] = self.health_data.get("weekly_deficit", 0) + int(v)
                elif action_type == "set_water": self.health_data["water"] = v
                elif action_type == "add_water": self.health_data["water"] += v
                self.update_health_ui(); self.save_memory()
            except: pass

    def trigger_morning_summary(self):
        n = datetime.now(); a = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]; g = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        ts = f"{n.day} {a[n.month]} {n.year} {g[n.weekday()]}"; sp = [f"Günaydın {self.current_salutation}."]
        
        if self.summary_prefs.get("time", True): sp.append(f"Bugün tarih {ts}, saat {n.strftime('%H:%M')}.")
        if self.summary_prefs.get("weather", True): sp.append(f"Konumunuz için hava durumu: {self.weather_label.text().replace('☁️ ', '')}.")
        if self.summary_prefs.get("tasks", True):
            t = self.tasks_box.toPlainText().strip()
            if t: sp.append(f"İşte bekleyen görevleriniz: {t}")
        tr = self.recurring_events.get(str(n.day), [])
        if tr: sp.append(f"Bugün ödenmesi gereken {len(tr)} aboneliğiniz bulunmaktadır.")
        tm = n + timedelta(days=1)
        at = self.calendar_events.get(tm.strftime("%dd.%m.%Y"), []) + self.recurring_events.get(str(tm.day), [])
        if at: sp.append(f"Yarın için planlanmış {len(at)} ödemeniz bulunmaktadır.")
        if self.summary_prefs.get("football", True): sp.append("Bugün futbol maç programını doğrudan sorgulayabilirsiniz.")
        if self.summary_prefs.get("currency", True): sp.append("Dolar ve Euro kurları anlık olarak kontrol edilmiştir.")
            
        fs = " ".join(sp); self.append_to_log(f">> [{self.ai_name} GÜNAYDIN ÖZETİ]:\n{fs}")
        self.worker = ChatWorker(fs, fs, None, self.current_model, self.voice_speed, self.voice_volume, self.ai_name, self.current_salutation, self.custom_api_key, True, self.health_data)
        self.worker.state_changed.connect(self.orb.set_state); self.worker.start()

    def handle_ai_response(self, response_text): 
        self.append_to_log(f">> {self.ai_name}: {response_text}"); self.save_memory() 

    def handle_task_added(self, task_type, content):
        if task_type == "task":
            ct = self.tasks_box.toPlainText().strip()
            items = [i.strip() for i in content.split(" ve ")] if " ve " in content else ([i.strip() for i in content.split(",")] if "," in content else [content])
            fn = "\n".join([f"- {i.lstrip('- ').strip()}" for i in items if i.lstrip("- ").strip()]); self.tasks_box.setText(f"{ct}\n{fn}" if ct else fn); self.append_to_log(f">> [GÖREV EKLENDİ]:\n{fn}")
        elif task_type == "reminder":
            self.add_obsidian_note(f"📌 {content.lstrip('- ').strip()}")
            self.append_to_log(f">> [OBSIDIAN'A EKLENDİ]: {content.lstrip('- ').strip()}")
        elif task_type == "note": self.add_obsidian_note(content)
        elif task_type == "clear_tasks": self.tasks_box.clear(); self.append_to_log(f">> [SİSTEM]: Yapılacaklar listesi temizlendi.")
        elif task_type == "recurring_event":
            try:
                ev = json.loads(content); d = str(ev["day"])
                if d not in self.recurring_events: self.recurring_events[d] = []
                self.recurring_events[d].append({"type": ev["type"], "desc": ev["desc"], "amount": ev["amount"], "recurring": True}); self.append_to_log(f">> [PERİYODİK KAYIT]: Her ayın {d}. günü - {ev['desc']}")
            except: pass
        self.save_memory()

    def append_to_log(self, text):
        self.log_box.setText(f"{self.log_box.toPlainText()}\n\n{text}"); self.saved_chat_history += f"\n{text}"
        self.log_box.verticalScrollBar().setValue(self.log_box.verticalScrollBar().maximum())

    def sync_obsidian_notes(self):
        try:
            if os.path.exists("CORE_Obsidian_Notes.md"):
                with open("CORE_Obsidian_Notes.md", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                display_text = []
                for line in reversed(lines):
                    line = line.strip()
                    if line.startswith("- **") and "**: " in line:
                        parts = line.split("**: ", 1)
                        ts = parts[0].replace("- **", "")
                        display_text.append(f"[{ts}] - {parts[1]}")
                yeni_metin = "\n".join(display_text)
                if self.notes_box.toPlainText() != yeni_metin:
                    self.notes_box.setText(yeni_metin)
                    self.saved_notes = yeni_metin
            else:
                if self.notes_box.toPlainText() != "":
                    self.notes_box.clear()
        except: pass

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    window = CoreInterface()
    sys.exit(app.exec_())
