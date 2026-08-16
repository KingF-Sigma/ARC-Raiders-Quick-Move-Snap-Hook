import threading
import time
import customtkinter as ctk
from pynput import keyboard
from config import load_config, save_config
from automation import move_item

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ARCInventoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("ARC Raiders - Safe Pocket Automation")
        self.geometry("450x520")
        self.resizable(False, False)
        
        self.cfg = load_config()
        self.listener = None
        
        self.setup_ui()
        self.start_hotkey_listener()

    def setup_ui(self):
        # Header / Status
        self.status_label = ctk.CTkLabel(self, text="Status: Bereit", font=("Helvetica", 16, "bold"), text_color="green")
        self.status_label.pack(pady=15)
        
        # Power Switch
        self.switch_var = ctk.StringVar(value="on" if self.cfg["enabled"] else "off")
        self.power_switch = ctk.CTkSwitch(
            self, text="Automatisierung Aktiviert", command=self.toggle_power,
            variable=self.switch_var, onvalue="on", offvalue="off"
        )
        self.power_switch.pack(pady=10)
        
        # Frame für Einstellungen
        settings_frame = ctk.CTkFrame(self)
        settings_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Hotkey Eingabe
        ctk.CTkLabel(settings_frame, text="Hotkey (z.B. F6):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.hotkey_entry = ctk.CTkEntry(settings_frame, width=120)
        self.hotkey_entry.insert(0, self.cfg["hotkey"])
        self.hotkey_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Verzögerung (Delay)
        ctk.CTkLabel(settings_frame, text="Delay (ms):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.delay_entry = ctk.CTkEntry(settings_frame, width=120)
        self.delay_entry.insert(0, str(self.cfg["delay_ms"]))
        self.delay_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Position Safe Pocket Slot 1
        ctk.CTkLabel(settings_frame, text="Safe Pocket Slot 1 (X, Y):").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        sp_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        sp_frame.grid(row=2, column=1, padx=10, pady=5)
        self.sp_x = ctk.CTkEntry(sp_frame, width=55)
        self.sp_x.insert(0, str(self.cfg["safe_pocket_slot_1"]["x"]))
        self.sp_x.pack(side="left", padx=2)
        self.sp_y = ctk.CTkEntry(sp_frame, width=55)
        self.sp_y.insert(0, str(self.cfg["safe_pocket_slot_1"]["y"]))
        self.sp_y.pack(side="left", padx=2)

        # Position Quick Use Slot 1
        ctk.CTkLabel(settings_frame, text="Quick Use Slot 1 (X, Y):").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        qu_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        qu_frame.grid(row=3, column=1, padx=10, pady=5)
        self.qu_x = ctk.CTkEntry(qu_frame, width=55)
        self.qu_x.insert(0, str(self.cfg["quick_use_slot_1"]["x"]))
        self.qu_x.pack(side="left", padx=2)
        self.qu_y = ctk.CTkEntry(qu_frame, width=55)
        self.qu_y.insert(0, str(self.cfg["quick_use_slot_1"]["y"]))
        self.qu_y.pack(side="left", padx=2)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        self.save_btn = ctk.CTkButton(btn_frame, text="Speichern", command=self.save_settings)
        self.save_btn.pack(side="left", padx=10)
        
        self.test_btn = ctk.CTkButton(btn_frame, text="Aktion Testen", command=self.trigger_action)
        self.test_btn.pack(side="left", padx=10)

    def toggle_power(self):
        self.cfg["enabled"] = (self.switch_var.get() == "on")
        status = "Bereit" if self.cfg["enabled"] else "Deaktiviert"
        color = "green" if self.cfg["enabled"] else "red"
        self.update_status(f"Status: {status}", color)
        save_config(self.cfg)

    def update_status(self, text, text_color="white"):
        self.status_label.configure(text=text, text_color=text_color)

    def save_settings(self):
        try:
            self.cfg["hotkey"] = self.hotkey_entry.get().strip().upper()
            self.cfg["delay_ms"] = int(self.delay_entry.get().strip())
            self.cfg["safe_pocket_slot_1"]["x"] = int(self.sp_x.get().strip())
            self.cfg["safe_pocket_slot_1"]["y"] = int(self.sp_y.get().strip())
            self.cfg["quick_use_slot_1"]["x"] = int(self.qu_x.get().strip())
            self.cfg["quick_use_slot_1"]["y"] = int(self.qu_y.get().strip())
            
            save_config(self.cfg)
            self.update_status("Status: Einstellungen gespeichert", "cyan")
            self.restart_hotkey_listener()
        except ValueError:
            self.update_status("Fehler: Ungültige Eingabewerte", "red")

    def trigger_action(self):
        if not self.cfg["enabled"]:
            return

        def run():
            self.update_status("Status: Verschiebe Item...", "yellow")
            try:
                # Zieht jetzt von Quick Use Slot zu Safe Pocket Slot!
                move_item(
                    self.cfg["quick_use_slot_1"]["x"],
                    self.cfg["quick_use_slot_1"]["y"],
                    self.cfg["safe_pocket_slot_1"]["x"],
                    self.cfg["safe_pocket_slot_1"]["y"],
                    self.cfg["delay_ms"]
                )
                self.update_status("Status: Item verschoben!", "green")
            except Exception as e:
                self.update_status("Fehler bei Ausführung", "red")
            
            time.sleep(2)
            if self.cfg["enabled"]:
                self.update_status("Status: Bereit", "green")

        threading.Thread(target=run, daemon=True).start()

    def on_key_press(self, key):
        try:
            hk = self.cfg["hotkey"]
            pressed_key = ""
            if hasattr(key, 'name'):
                pressed_key = key.name.upper()
            elif hasattr(key, 'char') and key.char:
                pressed_key = key.char.upper()
                
            if pressed_key == hk and self.cfg["enabled"]:
                self.trigger_action()
        except Exception:
            pass

    def start_hotkey_listener(self):
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

    def restart_hotkey_listener(self):
        if self.listener:
            self.listener.stop()
        self.start_hotkey_listener()

if __name__ == "__main__":
    app = ARCInventoryApp()
    app.mainloop()