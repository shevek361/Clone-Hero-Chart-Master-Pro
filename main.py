import tkinter as tk
from tkinter import ttk, filedialog
import os, json, threading
from processor import SmartProcessor
from gui_components import GeneratorTab, LibraryTab

LANG_DICT = {
    "Deutsch": {
        "tab_gen": "🚀 Generator", "tab_lib": "📚 Library Builder",
        "meth": "Methode", "prof": "Profile & Intensität", "ms_pause": "ms Pause", "max_fret": "Max Fret",
        "strat_options": ["Optimale Mischung (Hybrid)", "Profi-Charts (Nur DB)", "Reine Heuristik (Mathematisch)"],
        "tt_strat": "HYBRID: Nutzt Profi-Patterns.\nNUR DB: Nur Bekanntes.\nMATHE: Nur Regler.",
        "tt_slider": "Abstand zwischen Noten und maximale Taste.",
        "btn_reset": "ZURÜCKSETZEN", "btn_gen": "LADEN & GENERIEREN",
        "train": "Training", "btn_browse": "Ordner...", "btn_extract": "📚 Wissen extrahieren",
        "knowledge": "Wissen", "status_ready": "Status: Bereit", "status_gen": "Generierung läuft...",
        "status_train": "Training läuft...", "btn_stop": "🛑 PROZESS STOPPEN", "btn_exit": "❌ BEENDEN"
    },
    "English": {
        "tab_gen": "🚀 Generator", "tab_lib": "📚 Library Builder",
        "meth": "Method", "prof": "Profiles & Intensity", "ms_pause": "ms delay", "max_fret": "Max Fret",
        "strat_options": ["Optimal Mix (Hybrid)", "Pro Charts (DB only)", "Pure Heuristics (Math)"],
        "tt_strat": "HYBRID: Uses pro patterns.\nDB ONLY: Only known.\nMATH: Sliders only.",
        "tt_slider": "Gap between notes and maximum button.",
        "btn_reset": "RESET", "btn_gen": "LOAD & GENERATE",
        "train": "Training", "btn_browse": "Folder...", "btn_extract": "📚 Extract Knowledge",
        "knowledge": "Knowledge", "status_ready": "Status: Ready", "status_gen": "Generating...",
        "status_train": "Training...", "btn_stop": "🛑 STOP PROCESS", "btn_exit": "❌ EXIT"
    },
    "Español": {
        "tab_gen": "🚀 Generador", "tab_lib": "📚 Constructor de Lib",
        "meth": "Método", "prof": "Perfiles e Intensidad", "ms_pause": "ms pausa", "max_fret": "Traste Máx",
        "strat_options": ["Mezcla Óptima (Híbrido)", "Pro Charts (Solo DB)", "Heurística Pura (Mate)"],
        "tt_strat": "HÍBRIDO: Patrones pro.\nSOLO DB: Solo conocidos.\nMATE: Solo controles.",
        "tt_slider": "Espacio entre notas y traste máximo.",
        "btn_reset": "REINICIAR", "btn_gen": "CARGAR Y GENERAR",
        "train": "Entrenamiento", "btn_browse": "Carpeta...", "btn_extract": "📚 Extraer Conocimiento",
        "knowledge": "Conocimiento", "status_ready": "Estado: Listo", "status_gen": "Generando...",
        "status_train": "Entrenando...", "btn_stop": "🛑 DETENER PROCESO", "btn_exit": "❌ SALIR"
    }
}

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("CH Chart Master Pro v2.1.0")
        self.root.geometry("1000x950")
        self.proc = SmartProcessor()
        self.cfg_path = "user_settings.json"
        self.prefs = self.load_prefs()
        self.current_lang = tk.StringVar(value=self.prefs.get("language", "Deutsch"))
        self.stop_requested = False

        # Header
        header = tk.Frame(root, bg="#2c3e50", pady=10); header.pack(fill="x")
        tk.Label(header, text="🎸 CH CHART MASTER PRO", fg="white", bg="#2c3e50", font=("Arial", 16, "bold")).pack(side="left", padx=20)
        
        lang_menu = ttk.Combobox(header, textvariable=self.current_lang, values=list(LANG_DICT.keys()), state="readonly", width=10)
        lang_menu.pack(side="right", padx=20)
        lang_menu.bind("<<ComboboxSelected>>", self.change_language)

        # Tabs
        self.nb = ttk.Notebook(root); self.nb.pack(expand=True, fill="both", padx=10, pady=5)
        self.tab_gen = GeneratorTab(self.nb, self); self.tab_lib = LibraryTab(self.nb, self)
        self.nb.add(self.tab_gen, text="Generator"); self.nb.add(self.tab_lib, text="Library")

        # Status & Progress
        self.status_frame = tk.Frame(root, bg="#ecf0f1", pady=10); self.status_frame.pack(fill="x", padx=20)
        self.lbl_status = tk.Label(self.status_frame, text="Ready", font=("Arial", 10, "bold"), bg="#ecf0f1")
        self.lbl_status.pack(side="top", anchor="w")
        self.progress = ttk.Progressbar(self.status_frame, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", pady=5)

        # Log
        self.log_box = tk.Text(root, bg="#1e272e", fg="#d2dae2", height=10, font=("Consolas", 10))
        self.log_box.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Footer
        footer = tk.Frame(root); footer.pack(fill="x", padx=20, pady=10)
        self.btn_stop = tk.Button(footer, command=self.stop_tasks, bg="#f39c12", fg="white", font=("Arial", 10, "bold"), pady=10)
        self.btn_stop.pack(side="left", fill="x", expand=True, padx=5)
        self.btn_exit = tk.Button(footer, command=self.close, bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), pady=10)
        self.btn_exit.pack(side="right", fill="x", expand=True, padx=5)

        self.update_ui_texts()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def get_lang(self): return LANG_DICT[self.current_lang.get()]

    def change_language(self, event=None):
        self.update_ui_texts()
        self.tab_gen.setup_ui()
        self.tab_lib.setup_ui()

    def update_ui_texts(self):
        l = self.get_lang()
        self.nb.tab(0, text=l["tab_gen"]); self.nb.tab(1, text=l["tab_lib"])
        self.lbl_status.config(text=l["status_ready"])
        self.btn_stop.config(text=l["btn_stop"]); self.btn_exit.config(text=l["btn_exit"])

    def set_status(self, text_key, color="#2c3e50", val=0):
        l = self.get_lang()
        txt = l.get(text_key, text_key)
        self.lbl_status.config(text=txt, fg=color)
        self.progress["value"] = val; self.root.update_idletasks()

    def log(self, msg): 
        self.log_box.insert("end", f"> {msg}\n")
        self.log_box.see("end")

    def load_prefs(self):
        if os.path.exists(self.cfg_path):
            try:
                with open(self.cfg_path, "r") as f: return json.load(f)
            except: pass
        return {}

    def stop_tasks(self): 
        self.stop_requested = True
        self.log("STOP SIGNAL SENT")

    def browse(self):
        d = filedialog.askdirectory()
        if d: 
            self.tab_lib.ent_path.delete(0, tk.END)
            self.tab_lib.ent_path.insert(0, d)

    def run_gen(self):
        f = filedialog.askopenfilename(filetypes=[("Charts", "*.chart *.mid")])
        if not f: return
        self.set_status("status_gen", "#3498db", 50)
        try:
            setts = {k: {"speed": v[0].get(), "frets": v[1].get()} for k, v in self.tab_gen.sliders.items()}
            res, stats = self.proc.generate(f, setts, self.tab_gen.strat_var.get())
            save = filedialog.asksaveasfilename(defaultextension=".chart", initialfile=os.path.basename(f).replace(".mid", ".chart"))
            if save:
                with open(save, "w", encoding="utf-8") as o: o.write(res)
                self.log(f"SUCCESS: {os.path.basename(save)} (DB: {stats['lib']}, HEUR: {stats['heur']})")
            self.set_status("status_ready", val=100)
        except Exception as e: 
            self.log(f"ERROR: {e}")
            self.set_status("status_ready", "#c0392b", 0)

    def start_learn(self):
        p = self.tab_lib.ent_path.get()
        if p: 
            self.stop_requested = False
            self.set_status("status_train", "#27ae60", 0)
            threading.Thread(target=self.learn_worker, args=(p,), daemon=True).start()

    def learn_worker(self, folder):
        """Hintergrund-Funktion mit Anzeige des Pfades im Log."""
        files = [os.path.join(r, f) for r, d, fls in os.walk(folder) 
                 for f in fls if f.lower().endswith(('.chart', '.mid'))]
        
        new = 0
        total = len(files)
        errors = []
        skipped = 0
        
        # Sprache laden
        lang_train = self.get_lang()['train']
        self.log(f"--- {lang_train} ({total} Files) ---")
        
        for i, f in enumerate(files):
            if self.stop_requested: 
                self.log("!!! ABORTED !!!")
                break
            
            # Pfad-Logik: Wir zeigen den Pfad ab dem gewählten Ordner an
            rel_path = os.path.relpath(f, folder)
            current_song = os.path.basename(f)
            
            # Status-Update (oben am Balken zeigen wir nur den Songnamen für die Optik)
            pct = int(((i + 1) / total) * 100)
            self.set_status(f"{lang_train}: {i+1}/{total} - {current_song}", "#27ae60", pct)
            
            # Blackbox-Update (unten zeigen wir den Ordner-Pfad an)
            # Wir loggen jeden 5. Song oder wenn er neu ist, um die Box nicht zu überfluten
            try:
                result = self.proc.learn_from_file(f)
                if result == True:
                    new += 1
                    self.log(f"NEW: {rel_path}") # Zeigt den Ordner + Song an
                elif result == "skip":
                    skipped += 1
            except Exception as e:
                errors.append(f"{rel_path}: {str(e)}")
        
        self.proc.save_db()
        self.log("--- SUMMARY ---")
        self.log(f"✅ Patterns: +{new} | ↪️ Skipped: {skipped}")
        
        if errors:
            self.log(f"⚠️ Errors ({len(errors)}):")
            for err in errors[:10]: self.log(f"   - {err}")
        
        self.tab_lib.lbl_stats.config(text=f"{self.get_lang()['knowledge']}: {self.proc.db['stats']}")
        self.set_status("status_ready", val=100)
        self.stop_requested = False

    def close(self):
        self.stop_requested = True
        d = {
            "language": self.current_lang.get(),
            "strategy": self.tab_gen.strat_var.get(),
            "sliders": {k: [v[0].get(), v[1].get()] for k, v in self.tab_gen.sliders.items()}
        }
        with open(self.cfg_path, "w") as f: json.dump(d, f, indent=4)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk(); App(root); root.mainloop()
