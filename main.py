import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os, json, threading
from processor import SmartProcessor
from gui_components import GeneratorTab, LibraryTab

LANG_DICT = {
    "Deutsch": {
        "tab_gen": "🚀 Generator", "tab_lib": "📚 Library", "meth": "Methode", "btn_reset": "RESET", "btn_gen": "GENERIEREN",
        "strat_options": ["Optimale Mischung (Hybrid)", "Profi-Charts (Nur DB)", "Reine Heuristik"],
        "train": "Training", "btn_browse": "Ordner...", "btn_extract": "Extrahiere Wissen",
        "knowledge": "Wissen", "status_ready": "Bereit", "status_gen": "Generiere...",
        "status_train": "Training...", "btn_stop": "🛑 STOPPEN", "btn_exit": "❌ BEENDEN",
        "btn_reset_db": "⚠️ DB löschen", "msg_reset_confirm": "Wissen löschen?", "msg_reset_done": "Geleert."
    },
    "English": {
        "tab_gen": "🚀 Generator", "tab_lib": "📚 Library", "meth": "Method", "btn_reset": "RESET", "btn_gen": "GENERATE",
        "strat_options": ["Optimal Mix (Hybrid)", "Pro Charts (DB only)", "Pure Heuristics"],
        "train": "Training", "btn_browse": "Folder...", "btn_extract": "Extract Knowledge",
        "knowledge": "Knowledge", "status_ready": "Ready", "status_gen": "Generating...",
        "status_train": "Training...", "btn_stop": "🛑 STOP", "btn_exit": "❌ EXIT",
        "btn_reset_db": "⚠️ Reset DB", "msg_reset_confirm": "Clear DB?", "msg_reset_done": "Cleared."
    }
}

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("CH Chart Master Pro")
        self.root.geometry("1050x820")
        self.proc = SmartProcessor()
        self.cfg_path = "user_settings.json"
        self.prefs = self.load_prefs()
        self.current_lang = tk.StringVar(value=self.prefs.get("language", "English"))
        self.stop_requested = False
        self.last_gen_data = {}

        header = tk.Frame(root, bg="#2c3e50", pady=3); header.pack(fill="x")
        tk.Label(header, text="🎸 CH MASTER", fg="white", bg="#2c3e50", font=("Arial", 12, "bold")).pack(side="left", padx=15)
        lang_menu = ttk.Combobox(header, textvariable=self.current_lang, values=list(LANG_DICT.keys()), state="readonly", width=10)
        lang_menu.pack(side="right", padx=15); lang_menu.bind("<<ComboboxSelected>>", self.change_language)

        self.nb = ttk.Notebook(root); self.nb.pack(expand=True, fill="both", padx=5, pady=2)
        self.tab_gen = GeneratorTab(self.nb, self); self.tab_lib = LibraryTab(self.nb, self)
        self.nb.add(self.tab_gen, text="Generator"); self.nb.add(self.tab_lib, text="Library")

        self.status_frame = tk.Frame(root, bg="#ecf0f1"); self.status_frame.pack(fill="x", padx=15)
        self.lbl_status = tk.Label(self.status_frame, text="Ready", font=("Arial", 8, "bold"), bg="#ecf0f1"); self.lbl_status.pack(side="left")
        self.progress = ttk.Progressbar(self.status_frame, orient="horizontal", mode="determinate")

        self.log_box = tk.Text(root, bg="#1e272e", fg="#d2dae2", height=3, font=("Consolas", 8)); self.log_box.pack(fill="x", padx=15, pady=2)
        
        footer = tk.Frame(root); footer.pack(fill="x", padx=15, pady=2)
        self.btn_stop = tk.Button(footer, text="STOP", command=self.stop_tasks, bg="#f39c12", fg="white", font=("Arial", 8, "bold")); self.btn_stop.pack(side="left", fill="x", expand=True, padx=2)
        self.btn_exit = tk.Button(footer, text="EXIT", command=self.close, bg="#e74c3c", fg="white", font=("Arial", 8, "bold")); self.btn_exit.pack(side="right", fill="x", expand=True, padx=2)

        self.update_ui_texts(); self.tab_lib.lbl_stats.config(text=f"{self.get_lang()['knowledge']}: {self.proc.db['stats']}")
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def get_lang(self): return LANG_DICT.get(self.current_lang.get(), LANG_DICT["English"])

    def change_language(self, e=None): self.update_ui_texts(); self.tab_gen.setup_ui(); self.tab_lib.setup_ui()

    def update_ui_texts(self):
        l = self.get_lang(); self.nb.tab(0, text=l["tab_gen"]); self.nb.tab(1, text=l["tab_lib"])
        self.lbl_status.config(text=l["status_ready"]); self.btn_stop.config(text=l["btn_stop"]); self.btn_exit.config(text=l["btn_exit"])

    def set_status(self, t, c="#2c3e50", v=0):
        txt = self.get_lang().get(t, t); self.lbl_status.config(text=txt, fg=c)
        self.progress["value"] = v; self.root.update_idletasks()

    def log(self, m): self.log_box.insert("end", f"> {m}\n"); self.log_box.see("end")

    def update_preview(self):
        canvas = self.tab_gen.canvas; canvas.delete("all")
        diff = self.tab_gen.preview_diff.get()
        if diff not in self.last_gen_data: return
        notes = self.last_gen_data[diff]; ticks = sorted(notes.keys(), key=int)
        if not ticks: return
        w, zoom = canvas.winfo_width(), self.tab_gen.zoom_level
        if w < 50: w = 600
        min_t, max_t = int(ticks[0]), int(ticks[-1])
        total_height = (max_t - min_t) * 0.2 * zoom + 500
        canvas.config(scrollregion=(0, 0, w, total_height))
        colors = ["#2ecc71", "#e74c3c", "#f1c40f", "#3498db", "#e67e22"]
        lane_w = w / 6
        for i in range(5):
            x = (i+1) * lane_w
            canvas.create_line(x, 0, x, total_height, fill="#2c3e50", width=1)
        for t in ticks:
            y = (int(t) - min_t) * 0.2 * zoom + 50
            for f, _ in notes[t]:
                f_idx = int(f)
                if f_idx < 5:
                    x = (f_idx + 1) * lane_w
                    canvas.create_oval(x-10, y-5, x+10, y+5, fill=colors[f_idx], outline="white", width=1)

    def run_gen(self):
        f = filedialog.askopenfilename(filetypes=[("Charts", "*.chart *.mid")])
        if not f: return
        self.set_status("status_gen", "#3498db", 50)
        try:
            setts = {d: {"speed": v[0].get(), "frets": v[1].get()} for d, v in self.tab_gen.sliders.items()}
            res, stats = self.proc.generate(f, setts, self.tab_gen.strat_var.get())
            self.last_gen_data = self.proc._extract_all_generated_notes(res)
            self.update_preview()
            save = filedialog.asksaveasfilename(defaultextension=".chart", initialfile="notes.chart")
            if save:
                with open(save, "w", encoding="utf-8") as o: o.write(res)
                self.log(f"SAVED: {os.path.basename(save)}")
            self.set_status("status_ready", v=100)
        except Exception as e: self.log(f"ERR: {e}"); self.set_status("status_ready", "#c0392b", 0)

    def start_learn(self):
        p = self.tab_lib.ent_path.get()
        if p: self.stop_requested = False; threading.Thread(target=self.learn_worker, args=(p,), daemon=True).start()

    def learn_worker(self, folder):
        files = [os.path.join(r, f) for r, d, fls in os.walk(folder) for f in fls if f.lower().endswith(('.chart', '.mid'))]
        new, total = 0, len(files)
        for i, f in enumerate(files):
            if self.stop_requested: break
            self.set_status(f"{i+1}/{total}", "#27ae60", int(((i+1)/total)*100))
            if self.proc.learn_from_file(f): new += 1
        self.proc.save_db(); self.tab_lib.lbl_stats.config(text=f"{self.get_lang()['knowledge']}: {self.proc.db['stats']}"); self.set_status("status_ready", v=100)

    def reset_library(self):
        if messagebox.askyesno("Reset", self.get_lang()["msg_reset_confirm"]):
            self.proc.db = {"patterns": {}, "stats": 0, "learned_files": []}; self.proc.save_db(); self.tab_lib.lbl_stats.config(text="0")

    def browse(self):
        d = filedialog.askdirectory()
        if d: self.tab_lib.ent_path.delete(0, tk.END); self.tab_lib.ent_path.insert(0, d)

    def load_prefs(self):
        try:
            if os.path.exists(self.cfg_path):
                with open(self.cfg_path, "r") as f: return json.load(f)
        except: pass
        return {}

    def stop_tasks(self): self.stop_requested = True

    def close(self):
        try:
            slider_data = {}
            for diff, (s_val, f_val) in self.tab_gen.sliders.items():
                slider_data[diff] = [s_val.get(), f_val.get()]

            d = {
                "language": self.current_lang.get(),
                "strategy": self.tab_gen.strat_var.get(),
                "sliders": slider_data
            }
        
            with open(self.cfg_path, "w") as f:
                json.dump(d, f, indent=4)
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
        
        # Jetzt steht es außerhalb des try-except Blocks:
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk(); App(root); root.mainloop()
