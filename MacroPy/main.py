import customtkinter as ctk
import threading
import time
import keyboard
import json
import os
from tkinter import filedialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

FONT = ("Segoe UI", 14)

class MacroManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Macro Manager")
        self.geometry("900x600")

        self.settings_path = os.path.join(os.path.expanduser("~"), "Documents", "settings.json")
        self.json_path = self.load_settings()
        self.macros = []
        self.current_macro = {"name": "", "keys": [], "delay": 1, "repeat": 4, "start_after": 0}
        self.recording = False
        self.stop_macro = False

        self.create_widgets()
        self.load_macros_from_file()

    def load_settings(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    return settings.get("json_path", os.path.join(os.path.expanduser("~"), "Documents", "macros.json"))
            except:
                pass
        return os.path.join(os.path.expanduser("~"), "Documents", "macros.json")

    def save_settings(self):
        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump({"json_path": self.json_path}, f, indent=4)
        except Exception as e:
            print("Error al guardar configuración:", e)

    def create_widgets(self):
        self.left_frame = ctk.CTkFrame(self, width=200)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.macro_list_label = ctk.CTkLabel(self.left_frame, text="Macros disponibles:", font=FONT)
        self.macro_list_label.pack(pady=(10, 5))

        self.macro_buttons_frame = ctk.CTkFrame(self.left_frame)
        self.macro_buttons_frame.pack(fill="y", expand=True)

        self.new_macro_button = ctk.CTkButton(self.left_frame, text="NUEVO", command=self.new_macro, font=FONT)
        self.new_macro_button.pack(pady=(5, 5))

        self.delete_macro_button = ctk.CTkButton(self.left_frame, text="BORRAR", command=self.delete_macro, font=FONT)
        self.delete_macro_button.pack(pady=(5, 5))

        self.settings_button = ctk.CTkButton(self.left_frame, text="CONFIGURACIÓN", command=self.open_settings, font=FONT)
        self.settings_button.pack(pady=(5, 5))

        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.name_label = ctk.CTkLabel(self.right_frame, text="Nombre de la Macro:", anchor="w", font=FONT)
        self.name_label.pack(pady=(10, 0), fill="x")
        self.name_entry = ctk.CTkEntry(self.right_frame, font=FONT)
        self.name_entry.pack(pady=(5, 10), fill="x")

        self.combo_label = ctk.CTkLabel(self.right_frame, text="Siguiente COMBINACIÓN:", anchor="w", font=FONT)
        self.combo_label.pack(pady=(5, 0), fill="x")
        self.combo_entry = ctk.CTkEntry(self.right_frame, font=FONT)
        self.combo_entry.pack(pady=(5, 10), fill="x")
        self.combo_entry.bind("<KeyPress>", self.record_keys)

        self.delay_label = ctk.CTkLabel(self.right_frame, text="TIEMPO ENTRE TECLAS (SEG)", anchor="w", font=FONT)
        self.delay_label.pack(fill="x")
        self.delay_entry = ctk.CTkEntry(self.right_frame, font=FONT)
        self.delay_entry.pack(fill="x")

        self.repeat_label = ctk.CTkLabel(self.right_frame, text="REPETICIONES", anchor="w", font=FONT)
        self.repeat_label.pack(fill="x")
        self.repeat_entry = ctk.CTkEntry(self.right_frame, font=FONT)
        self.repeat_entry.pack(fill="x")

        self.start_label = ctk.CTkLabel(self.right_frame, text="TIEMPO DE INICIO (SEG)", anchor="w", font=FONT)
        self.start_label.pack(fill="x")
        self.start_entry = ctk.CTkEntry(self.right_frame, font=FONT)
        self.start_entry.pack(fill="x")

        self.execute_button = ctk.CTkButton(self.right_frame, text="EJECUTAR", command=self.execute_macro, font=FONT)
        self.execute_button.pack(pady=(20, 10))

        self.stop_button = ctk.CTkButton(self.right_frame, text="DETENER", command=self.stop_macro_execution, font=FONT)
        self.stop_button.pack(pady=(0, 10))

        self.save_button = ctk.CTkButton(self.right_frame, text="GUARDAR", command=self.save_macro, font=FONT)
        self.save_button.pack()

    def open_settings(self):
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Configuración")
        settings_window.geometry("500x180")
        settings_window.resizable(False, False)

        label = ctk.CTkLabel(settings_window, text="Opciones de configuración", font=FONT)
        label.pack(pady=10)

        change_label = ctk.CTkLabel(settings_window, text="Cambiar ruta de macros guardadas", font=FONT)
        change_label.pack(pady=(0, 5))

        path_frame = ctk.CTkFrame(settings_window)
        path_frame.pack(pady=10, fill="x", padx=10)

        self.path_entry = ctk.CTkEntry(path_frame, font=FONT, width=300)
        self.path_entry.insert(0, self.json_path)
        self.path_entry.pack(side="left", padx=5)

        path_button = ctk.CTkButton(path_frame, text="Open folder", command=self.change_json_path)
        path_button.pack(side="left", padx=5)

    def change_json_path(self):
        new_path = filedialog.askdirectory()
        if new_path:
            self.json_path = os.path.join(new_path, "macros.json")
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, self.json_path)
            self.save_macros_to_file()
            self.save_settings()

    def new_macro(self):
        self.current_macro = {"name": "", "keys": [], "delay": 1, "repeat": 4, "start_after": 0}
        self.update_editor()

    def delete_macro(self):
        selected = self.get_selected_macro()
        if selected is not None:
            self.macros.pop(selected)
            self.update_macro_list()
            self.new_macro()
            self.save_macros_to_file()

    def save_macro(self):
        self.current_macro["name"] = self.name_entry.get()
        self.current_macro["delay"] = float(self.delay_entry.get())
        self.current_macro["repeat"] = int(self.repeat_entry.get())
        self.current_macro["start_after"] = float(self.start_entry.get())

        if self.get_selected_macro() is None:
            self.macros.append(self.current_macro.copy())
        else:
            self.macros[self.get_selected_macro()] = self.current_macro.copy()

        self.update_macro_list()
        self.save_macros_to_file()

    def save_macros_to_file(self):
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(self.macros, f, indent=4)
        except Exception as e:
            print("Error al guardar macros:", e)

    def load_macros_from_file(self):
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    self.macros = json.load(f)
                    if self.macros:
                        self.current_macro = self.macros[0].copy()
                        self.update_editor()
                        self.update_macro_list()
            except Exception as e:
                print("Error al cargar macros:", e)

    def execute_macro(self):
        self.stop_macro = False
        threading.Thread(target=self.run_macro, daemon=True).start()

    def stop_macro_execution(self):
        self.stop_macro = True

    def run_macro(self):
        time.sleep(self.current_macro["start_after"])
        for _ in range(self.current_macro["repeat"]):
            if self.stop_macro:
                break
            for key in self.current_macro["keys"]:
                if self.stop_macro:
                    break
                keyboard.press_and_release(key)
                time.sleep(self.current_macro["delay"])

    def update_macro_list(self):
        for widget in self.macro_buttons_frame.winfo_children():
            widget.destroy()

        for idx, macro in enumerate(self.macros):
            b = ctk.CTkButton(self.macro_buttons_frame, text=macro["name"], command=lambda i=idx: self.load_macro(i), font=FONT)
            b.pack(fill="x", pady=2)

    def load_macro(self, index):
        self.current_macro = self.macros[index].copy()
        self.update_editor()

    def update_editor(self):
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, self.current_macro["name"])

        self.combo_entry.delete(0, "end")
        self.combo_entry.insert(0, " + ".join(self.current_macro["keys"]))

        self.delay_entry.delete(0, "end")
        self.delay_entry.insert(0, str(self.current_macro["delay"]))

        self.repeat_entry.delete(0, "end")
        self.repeat_entry.insert(0, str(self.current_macro["repeat"]))

        self.start_entry.delete(0, "end")
        self.start_entry.insert(0, str(self.current_macro["start_after"]))

    def get_selected_macro(self):
        for i, macro in enumerate(self.macros):
            if macro == self.current_macro:
                return i
        return None

    def record_keys(self, event):
        key = event.keysym.lower()
        if (event.state & 0x4) and key == "backspace":
            self.current_macro["keys"].clear()
        elif key == "return":
            if self.recording:
                self.combo_entry.unbind("<KeyPress>")
                self.recording = False
            else:
                self.current_macro["keys"].append("return")
                self.recording = True
        else:
            self.current_macro["keys"].append(key)

        self.combo_entry.delete(0, "end")
        self.combo_entry.insert(0, " + ".join(self.current_macro["keys"]))

if __name__ == "__main__":
    app = MacroManagerApp()
    app.mainloop()
