import tkinter as tk
from tkinter import ttk, filedialog
import os
import json
import threading
from processor import SmartProcessor
from gui_components import GeneratorTab, LibraryTab

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("CH Chart Master Pro v2.1.0")
        self.root.geometry("1000x950")
        
        self.proc = SmartProcessor()
        self.cfg_path = "user_settings.json"
        self.prefs = self.load_prefs()
        self.stop_requested = False

        # Header
        header = tk.Frame(root, bg="#2c3e50", pady=15); header.pack(fill="x")
        tk.Label(header, text="🎸 CH CHART MASTER PRO v2.1.0", fg="white", bg="#2c3e50", font=("Arial", 16, "bold")).pack()
        
        # Tabs
        self.nb = ttk.Notebook(root)
        self.nb.pack(expand=True, fill="both", padx=10, pady=5)
        
        self.tab_gen = GeneratorTab(self.nb, self)
        self.tab_lib = LibraryTab(self.nb, self)
        
        self.nb.add(self.tab_gen, text="  🚀 Generator  ")
        self.nb.add(self.tab_lib, text="  📚 Library Builder  ")

        # Log & Footer
        self.log_box = tk.Text(root, bg="#1e272e", fg="#d2dae2", height=10, font=("Consolas", 10))
        self.log_box.pack(fill="both", expand=True, padx=20, pady=10)
        
        tk.Button(root, text="🛑 ABBRECHEN & BEENDEN", command=self.close, bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), pady=10).pack(fill="x", padx=20, pady=10)
        
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def log(self, msg): 
        self.log_box.insert("end", f"> {msg}\n")
        self.log_box.see("end")

    def load_prefs(self):
        if os.path.exists(self.cfg_path):
            try:
                with open(self.cfg_path, "r") as f: return json.load(f)
            except: pass
        return {}

    def browse(self):
        d = filedialog.askdirectory()
        if d: 
            self.tab_lib.ent_path.delete(0, tk.END)
            self.tab_lib.ent_path.insert(0, d)

    def run_gen(self):
        f = filedialog.askopenfilename(filetypes=[("Clone Hero Files", "*.chart *.mid")])
        if not f: return
        try:
            setts = {k: {"speed": v[0].get(), "frets": v[1].get()} for k, v in self.tab_gen.sliders.items()}
            res, stats = self.proc.generate(f, setts, self.tab_gen.strat_var.get())
            save = filedialog.asksaveasfilename(defaultextension=".chart", initialfile=os.path.basename(f).replace(".mid", ".chart"))
            if save:
                with open(save, "w", encoding="utf-8") as o: o.write(res)
                # Erweiterte Log-Ausgabe:
                log_msg = f"ERFOLG: {os.path.basename(save)}\n"
                log_msg += f"   - Datenbank-Patterns: {stats['lib']}\n"
                log_msg += f"   - Mathematisch erzeugt: {stats['heur']}\n"
                log_msg += f"   - Akkorde vereinfacht: {stats['simplified']}"
                self.log(log_msg)
        except Exception as e: self.log(f"FEHLER: {str(e)}")

    def start_learn(self):
        p = self.tab_lib.ent_path.get()
        if p: 
            self.stop_requested = False
            threading.Thread(target=self.learn_worker, args=(p,), daemon=True).start()

    def learn_worker(self, folder):
        files = [os.path.join(r, f) for r, d, fls in os.walk(folder) for f in fls if f.lower().endswith(('.chart', '.mid'))]
        new = 0
        for i, f in enumerate(files):
            if self.stop_requested: break
            if self.proc.learn_from_file(f) == True: new += 1
            if i % 10 == 0: self.log(f"Analysiere: {i+1}/{len(files)}...")
        self.proc.save_db()
        self.log(f"Training beendet. {new} neue Songs gelernt.")
        self.tab_lib.lbl_stats.config(text=f"Wissen: {self.proc.db['stats']} Songs")

    def close(self):
        self.stop_requested = True
        d = {
            "strategy": self.tab_gen.strat_var.get(),
            "sliders": {k: [v[0].get(), v[1].get()] for k, v in self.tab_gen.sliders.items()}
        }
        with open(self.cfg_path, "w") as f: json.dump(d, f, indent=4)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
